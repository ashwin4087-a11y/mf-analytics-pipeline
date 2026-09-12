-- queries.sql
-- 10 Analytical Queries for Bluestock Mutual Fund Analytics

-- 1. Top 5 funds by AUM
SELECT 
    f.scheme_name, 
    f.fund_house, 
    p.aum_crore 
FROM fact_performance p
JOIN dim_fund f ON p.amfi_code = f.amfi_code
ORDER BY p.aum_crore DESC
LIMIT 5;

-- 2. Average NAV per month
SELECT 
    f.scheme_name,
    d.year, 
    d.month, 
    AVG(n.nav) as avg_nav
FROM fact_nav n
JOIN dim_date d ON n.date = d.date
JOIN dim_fund f ON n.amfi_code = f.amfi_code
WHERE n.is_trading_day = 1
GROUP BY f.scheme_name, d.year, d.month
ORDER BY f.scheme_name, d.year, d.month;

-- 3. SIP YoY growth
SELECT 
    month, 
    sip_inflow_crore, 
    yoy_growth_pct
FROM fact_monthly_sip
WHERE yoy_growth_pct IS NOT NULL
ORDER BY month DESC;

-- 4. Transactions by state
SELECT 
    state, 
    COUNT(*) as total_transactions, 
    SUM(amount_inr) as total_volume_inr
FROM fact_transactions
GROUP BY state
ORDER BY total_volume_inr DESC;

-- 5. Funds with expense_ratio < 1%
SELECT 
    scheme_name, 
    category, 
    expense_ratio_pct 
FROM dim_fund
WHERE expense_ratio_pct < 1.0
ORDER BY expense_ratio_pct ASC;

-- 6. Top 5 funds by 1-year return
SELECT 
    f.scheme_name, 
    f.category, 
    p.return_1yr_pct 
FROM fact_performance p
JOIN dim_fund f ON p.amfi_code = f.amfi_code
ORDER BY p.return_1yr_pct DESC
LIMIT 5;

-- 7. Fund count by category
SELECT 
    category, 
    COUNT(*) as number_of_funds
FROM dim_fund
GROUP BY category
ORDER BY number_of_funds DESC;

-- 8. Monthly transaction volume (count and total amount)
SELECT 
    d.year, 
    d.month, 
    COUNT(t.transaction_id) as num_transactions, 
    SUM(t.amount_inr) as total_amount
FROM fact_transactions t
JOIN dim_date d ON t.transaction_date = d.date
GROUP BY d.year, d.month
ORDER BY d.year, d.month;

-- 9. Average transaction amount by transaction type
SELECT 
    transaction_type, 
    AVG(amount_inr) as avg_transaction_amount,
    COUNT(*) as total_transactions
FROM fact_transactions
GROUP BY transaction_type
ORDER BY avg_transaction_amount DESC;

-- 10. AUM growth over time by fund house
SELECT 
    date, 
    fund_house, 
    aum_crore
FROM fact_aum
ORDER BY fund_house, date;
