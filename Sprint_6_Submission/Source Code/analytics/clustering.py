import os
import pandas as pd
import numpy as np
import sqlite3
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import seaborn as sns

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')
REPORTS_DIR = os.path.join(BASE_DIR, 'reports')
DB_PATH = os.path.join(BASE_DIR, 'data', 'nifty100.db')

def run_clustering():
    conn = sqlite3.connect(DB_PATH)
    
    query = """
    SELECT * FROM (
        SELECT company_id, 
               return_on_equity_pct as ROE, 
               debt_to_equity as DE, 
               revenue_cagr_5yr, 
               fcf_cagr_5yr, 
               operating_profit_margin_pct as OPM,
               ROW_NUMBER() OVER(PARTITION BY company_id ORDER BY year DESC) as rn
        FROM financial_ratios 
    ) WHERE rn = 1
    """
    df = pd.read_sql(query, conn).drop(columns=['rn'])
    
    sec_query = "SELECT company_id, broad_sector FROM sectors"
    df_sec = pd.read_sql(sec_query, conn)
    conn.close()
    
    df = df.merge(df_sec, on='company_id', how='left')
    
    features = ['ROE', 'DE', 'revenue_cagr_5yr', 'fcf_cagr_5yr', 'OPM']
    
    # Sector median imputation
    for feature in features:
        df[feature] = pd.to_numeric(df[feature], errors='coerce')
        df[feature] = df.groupby('broad_sector')[feature].transform(lambda x: x.fillna(x.median()))
        # Global median for any remaining NaNs
        df[feature] = df[feature].fillna(df[feature].median())
        
    X = df[features]
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Elbow plot
    inertia = []
    K = range(1, 10)
    for k in K:
        kmeans = KMeans(n_clusters=k, random_state=42)
        kmeans.fit(X_scaled)
        inertia.append(kmeans.inertia_)
        
    os.makedirs(REPORTS_DIR, exist_ok=True)
    plt.figure()
    plt.plot(K, inertia, 'bx-')
    plt.xlabel('k')
    plt.ylabel('Inertia')
    plt.title('Elbow Method For Optimal k')
    plt.savefig(os.path.join(REPORTS_DIR, 'elbow_plot.png'))
    plt.close()
    
    # KMeans n_clusters=5
    kmeans = KMeans(n_clusters=5, random_state=42)
    df['cluster'] = kmeans.fit_predict(X_scaled)
    
    # Meaningful names
    # Calculate cluster means to assign names
    cluster_means = df.groupby('cluster')[features].mean()
    # Simple logic based on means
    cluster_names = {}
    for c in range(5):
        means = cluster_means.loc[c]
        if means['ROE'] > df['ROE'].mean() and means['DE'] < df['DE'].mean():
            cluster_names[c] = 'High Quality / Low Debt'
        elif means['revenue_cagr_5yr'] > df['revenue_cagr_5yr'].mean():
            cluster_names[c] = 'High Growth'
        elif means['DE'] > df['DE'].mean() * 1.5:
            cluster_names[c] = 'Highly Leveraged'
        elif means['OPM'] > df['OPM'].mean() * 1.2:
            cluster_names[c] = 'High Margin Leaders'
        else:
            cluster_names[c] = f'Cluster {c} (Mixed)'
            
    df['cluster_name'] = df['cluster'].map(cluster_names)
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    df[['company_id', 'cluster', 'cluster_name']].to_csv(os.path.join(OUTPUT_DIR, 'cluster_labels.csv'), index=False)
    
    # Correlation Heatmap
    plt.figure(figsize=(8,6))
    sns.heatmap(df[features].corr(), annot=True, cmap='coolwarm', fmt=".2f")
    plt.title("Feature Correlation Heatmap")
    plt.tight_layout()
    plt.savefig(os.path.join(REPORTS_DIR, 'correlation_heatmap.png'))
    plt.close()
    
    # Outliers: abs(sector_z_score) > 3
    outliers = []
    for feature in features:
        df[f'{feature}_sector_mean'] = df.groupby('broad_sector')[feature].transform('mean')
        df[f'{feature}_sector_std'] = df.groupby('broad_sector')[feature].transform('std')
        # Avoid division by zero
        df[f'{feature}_sector_std'] = df[f'{feature}_sector_std'].replace(0, np.nan)
        df[f'{feature}_z'] = (df[feature] - df[f'{feature}_sector_mean']) / df[f'{feature}_sector_std']
        
        # Fill NaNs with 0 (if std was 0, it means all values are same, so z=0)
        df[f'{feature}_z'] = df[f'{feature}_z'].fillna(0)
        
        outlier_rows = df[df[f'{feature}_z'].abs() > 3]
        for _, row in outlier_rows.iterrows():
            outliers.append({
                'company_id': row['company_id'],
                'feature': feature,
                'value': row[feature],
                'sector_mean': row[f'{feature}_sector_mean'],
                'z_score': row[f'{feature}_z']
            })
            
    df_outliers = pd.DataFrame(outliers)
    df_outliers.to_csv(os.path.join(OUTPUT_DIR, 'outlier_report.csv'), index=False)
    
    # Portfolio stats
    stats = []
    for c in range(5):
        c_df = df[df['cluster'] == c]
        stat = {'cluster': c, 'cluster_name': cluster_names.get(c, f"Cluster {c}"), 'count': len(c_df)}
        for f in features:
            stat[f'{f}_mean'] = c_df[f].mean()
            stat[f'{f}_median'] = c_df[f].median()
        stats.append(stat)
        
    df_stats = pd.DataFrame(stats)
    df_stats.to_csv(os.path.join(OUTPUT_DIR, 'portfolio_stats.csv'), index=False)
    print("Clustering and Analysis Complete.")

if __name__ == '__main__':
    run_clustering()
