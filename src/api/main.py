import os
import time
import sqlite3
import pandas as pd
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional, List

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(BASE_DIR, 'data', 'nifty100.db')
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')
REPORTS_DIR = os.path.join(BASE_DIR, 'reports', 'tearsheets')

app = FastAPI(title="Nifty 100 API", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

START_TIME = time.time()

# Request logging and timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_t = time.time()
    response = await call_next(request)
    process_time = time.time() - start_t
    response.headers["X-Process-Time"] = str(process_time)
    # request logging would go here if needed
    return response

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

@app.get("/api/v1/health")
def health(db: sqlite3.Connection = Depends(get_db)):
    uptime = time.time() - START_TIME
    
    # DB Row counts
    counts = {}
    for table in ["companies", "profitandloss", "balancesheet", "cashflow", "financial_ratios", "sectors", "peer_groups", "documents"]:
        try:
            c = db.execute(f"SELECT COUNT(*) as cnt FROM {table}").fetchone()
            counts[table] = c['cnt']
        except:
            counts[table] = 0
            
    return {
        "status": "ok",
        "uptime_seconds": uptime,
        "version": "1.0.0",
        "db_row_counts": counts
    }

@app.get("/api/v1/companies")
def get_companies(db: sqlite3.Connection = Depends(get_db)):
    cursor = db.execute("SELECT id as ticker, company_name FROM companies")
    return [dict(row) for row in cursor.fetchall()]

@app.get("/api/v1/companies/{ticker}")
def get_company(ticker: str, db: sqlite3.Connection = Depends(get_db)):
    row = db.execute("SELECT id as ticker, company_name FROM companies WHERE id=?", (ticker,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Company not found")
    return dict(row)

@app.get("/api/v1/companies/{ticker}/pl")
def get_company_pl(ticker: str, year: Optional[int] = None, db: sqlite3.Connection = Depends(get_db)):
    query = "SELECT * FROM profitandloss WHERE company_id=?"
    params = [ticker]
    if year:
        query += " AND year=?"
        params.append(year)
    cursor = db.execute(query, params)
    rows = cursor.fetchall()
    if not rows:
        raise HTTPException(status_code=404, detail="Data not found")
    return [dict(row) for row in rows]

@app.get("/api/v1/companies/{ticker}/bs")
def get_company_bs(ticker: str, year: Optional[int] = None, db: sqlite3.Connection = Depends(get_db)):
    query = "SELECT * FROM balancesheet WHERE company_id=?"
    params = [ticker]
    if year:
        query += " AND year=?"
        params.append(year)
    cursor = db.execute(query, params)
    rows = cursor.fetchall()
    if not rows:
        raise HTTPException(status_code=404, detail="Data not found")
    return [dict(row) for row in rows]

@app.get("/api/v1/companies/{ticker}/cashflow")
def get_company_cashflow(ticker: str, year: Optional[int] = None, db: sqlite3.Connection = Depends(get_db)):
    query = "SELECT * FROM cashflow WHERE company_id=?"
    params = [ticker]
    if year:
        query += " AND year=?"
        params.append(year)
    cursor = db.execute(query, params)
    rows = cursor.fetchall()
    if not rows:
        raise HTTPException(status_code=404, detail="Data not found")
    return [dict(row) for row in rows]

@app.get("/api/v1/companies/{ticker}/ratios")
def get_company_ratios(ticker: str, year: Optional[int] = None, db: sqlite3.Connection = Depends(get_db)):
    query = "SELECT * FROM financial_ratios WHERE company_id=?"
    params = [ticker]
    if year:
        query += " AND year=?"
        params.append(year)
    cursor = db.execute(query, params)
    rows = cursor.fetchall()
    if not rows:
        raise HTTPException(status_code=404, detail="Data not found")
    return [dict(row) for row in rows]

@app.get("/api/v1/companies/{ticker}/tearsheet")
def get_company_tearsheet(ticker: str):
    path = os.path.join(REPORTS_DIR, f"{ticker}_Tearsheet.pdf")
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Tearsheet not found")
    return FileResponse(path, media_type="application/pdf", filename=f"{ticker}_Tearsheet.pdf")

@app.get("/api/v1/screener")
def get_screener(db: sqlite3.Connection = Depends(get_db)):
    # Return latest financial ratios for screener
    query = """
    SELECT company_id as ticker, return_on_equity_pct as roe, debt_to_equity as de, 
           free_cash_flow_cr as fcf, composite_quality_score
    FROM financial_ratios 
    WHERE year = (SELECT MAX(year) FROM financial_ratios)
    """
    cursor = db.execute(query)
    return [dict(row) for row in cursor.fetchall()]

@app.get("/api/v1/sectors")
def get_sectors(db: sqlite3.Connection = Depends(get_db)):
    cursor = db.execute("SELECT DISTINCT broad_sector FROM sectors")
    return [row['broad_sector'] for row in cursor.fetchall()]

@app.get("/api/v1/sectors/{sector}/companies")
def get_sector_companies(sector: str, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.execute("SELECT company_id as ticker FROM sectors WHERE broad_sector=?", (sector,))
    return [row['ticker'] for row in cursor.fetchall()]

@app.get("/api/v1/peers/{group_name}")
def get_peer_group(group_name: str, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.execute("SELECT company_id as ticker, is_benchmark FROM peer_groups WHERE peer_group_name=?", (group_name,))
    rows = cursor.fetchall()
    if not rows:
        raise HTTPException(status_code=404, detail="Peer group not found")
    return [dict(row) for row in rows]

@app.get("/api/v1/companies/{ticker}/peers/compare")
def get_company_peers_compare(ticker: str, db: sqlite3.Connection = Depends(get_db)):
    # Find peer group of the company
    group_row = db.execute("SELECT peer_group_name FROM peer_groups WHERE company_id=?", (ticker,)).fetchone()
    if not group_row:
        raise HTTPException(status_code=404, detail="No peer group assigned for this company")
        
    group_name = group_row['peer_group_name']
    
    # Get all peers in the group
    peers = db.execute("SELECT company_id as ticker, is_benchmark FROM peer_groups WHERE peer_group_name=?", (group_name,)).fetchall()
    
    # Get latest ratios for these peers
    tickers = [row['ticker'] for row in peers]
    placeholders = ','.join(['?'] * len(tickers))
    
    query = f"""
    SELECT company_id as ticker, return_on_equity_pct as roe, debt_to_equity as de, 
           composite_quality_score
    FROM financial_ratios 
    WHERE year = (SELECT MAX(year) FROM financial_ratios) AND company_id IN ({placeholders})
    """
    metrics = db.execute(query, tickers).fetchall()
    
    return {
        "peer_group_name": group_name,
        "companies": [dict(row) for row in metrics]
    }

@app.get("/api/v1/market-cap/{ticker}")
def get_market_cap(ticker: str, year: Optional[int] = None, db: sqlite3.Connection = Depends(get_db)):
    query = "SELECT * FROM market_cap WHERE company_id=?"
    params = [ticker]
    if year:
        query += " AND year=?"
        params.append(year)
    cursor = db.execute(query, params)
    rows = cursor.fetchall()
    if not rows:
        raise HTTPException(status_code=404, detail="Data not found")
    return [dict(row) for row in rows]

@app.get("/api/v1/portfolio/stats")
def get_portfolio_stats():
    path = os.path.join(OUTPUT_DIR, 'portfolio_stats.csv')
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Portfolio stats not found. Run clustering first.")
    df = pd.read_csv(path)
    return df.to_dict(orient='records')

@app.get("/api/v1/companies/{ticker}/documents")
def get_documents(ticker: str, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.execute("SELECT year, annual_report FROM documents WHERE company_id=?", (ticker,))
    rows = cursor.fetchall()
    if not rows:
        raise HTTPException(status_code=404, detail="No documents found")
    return [dict(row) for row in rows]
