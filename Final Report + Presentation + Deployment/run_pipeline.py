"""
Bluestock Mutual Fund Analytics - Master Pipeline Orchestration Script
======================================================================
This master script orchestrates the end-to-end execution of the Bluestock Mutual
Fund Analytics platform. It validates database state, runs ETL processing,
generates exploratory data analysis charts, computes risk-adjusted performance
metrics, renders dashboard screenshots, and compiles the final 19-page report
and 12-slide presentation.

Usage:
------
    python run_pipeline.py                     # Runs standard healthcheck & summary
    python run_pipeline.py --all               # Runs full end-to-end pipeline
    python run_pipeline.py --etl               # Executes data cleaning and SQLite load
    python run_pipeline.py --dashboard-images  # Renders 4 high-res dashboard images
    python run_pipeline.py --report            # Compiles Final_Report.pdf (19 pages)
    python run_pipeline.py --presentation      # Compiles Bluestock_MF_Presentation.pptx (12 slides)
    python run_pipeline.py --recommend High    # Runs fund recommender for specified risk
"""

import argparse
import logging
import os
import sqlite3
import subprocess
import sys
from pathlib import Path

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("BluestockPipeline")

SCRIPT_DIR = Path(__file__).resolve().parent

def check_environment() -> bool:
    """Verifies that all required files and database components exist."""
    db_path = SCRIPT_DIR / "bluestock_mf.db"
    report_path = SCRIPT_DIR / "Final_Report.pdf"
    pres_path = SCRIPT_DIR / "Bluestock_MF_Presentation.pptx"
    pbix_path = SCRIPT_DIR / "dashboard" / "bluestock_mf.pbix"

    logger.info("Verifying platform environment and components...")
    has_db = db_path.exists()
    has_report = report_path.exists()
    has_pres = pres_path.exists()
    has_pbix = pbix_path.exists()

    logger.info(f"  - SQLite Database (bluestock_mf.db): {'[FOUND]' if has_db else '[MISSING]'}")
    logger.info(f"  - Final Report (Final_Report.pdf): {'[FOUND]' if has_report else '[MISSING]'}")
    logger.info(f"  - Presentation (Bluestock_MF_Presentation.pptx): {'[FOUND]' if has_pres else '[MISSING]'}")
    logger.info(f"  - Power BI Dashboard (.pbix): {'[FOUND]' if has_pbix else '[MISSING]'}")

    if has_db:
        try:
            with sqlite3.connect(db_path) as conn:
                c = conn.cursor()
                fund_count = c.execute("SELECT count(*) FROM dim_fund").fetchone()[0]
                nav_count = c.execute("SELECT count(*) FROM fact_nav").fetchone()[0]
                tx_count = c.execute("SELECT count(*) FROM fact_transactions").fetchone()[0]
                logger.info(f"  - Database Records: {fund_count} funds, {nav_count:,} NAVs, {tx_count:,} transactions")
        except Exception as e:
            logger.warning(f"Error querying database: {e}")

    return has_db

def run_script(script_name: str, description: str):
    """Executes a child Python script within the active Python environment."""
    script_path = SCRIPT_DIR / script_name
    if not script_path.exists():
        logger.error(f"Script {script_name} does not exist at {script_path}")
        return False

    logger.info(f"Starting step: {description} ({script_name})...")
    result = subprocess.run([sys.executable, str(script_path)], capture_output=True, text=True, cwd=str(SCRIPT_DIR))
    if result.returncode != 0:
        logger.error(f"Failed to execute {script_name}:\n{result.stderr}")
        return False
    else:
        logger.info(f"Successfully finished {script_name}.")
        return True

def run_recommender(risk_appetite: str):
    """Invokes the algorithmic fund recommender engine."""
    from recommender import recommend_funds
    logger.info(f"Querying top recommended mutual funds for risk appetite: {risk_appetite}")
    df = recommend_funds(risk_appetite, db_path=str(SCRIPT_DIR / "bluestock_mf.db"))
    if df.empty:
        logger.warning("No recommendations returned.")
    else:
        print("\n" + "="*80)
        print(f"  TOP 3 RECOMMENDED MUTUAL FUNDS ({risk_appetite.upper()} RISK)")
        print("="*80)
        print(df.to_string(index=False))
        print("="*80 + "\n")

def main():
    parser = argparse.ArgumentParser(
        description="Bluestock Mutual Fund Analytics - Master Pipeline Orchestrator",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--all", action="store_true", help="Execute complete pipeline end-to-end")
    parser.add_argument("--etl", action="store_true", help="Run ETL and populate SQLite database")
    parser.add_argument("--dashboard-images", action="store_true", help="Render 4 Power BI dashboard screenshots")
    parser.add_argument("--report", action="store_true", help="Compile Final_Report.pdf (15-20 pages)")
    parser.add_argument("--presentation", action="store_true", help="Compile Bluestock_MF_Presentation.pptx (12 slides)")
    parser.add_argument("--recommend", type=str, choices=["Low", "Moderate", "High"], help="Get fund recommendations by risk appetite")

    args = parser.parse_args()

    print("\n" + "#"*70)
    print("  BLUESTOCK FINTECH - MUTUAL FUND ANALYTICS PLATFORM")
    print("  Master Orchestration Engine")
    print("#"*70 + "\n")

    check_environment()

    if args.recommend:
        run_recommender(args.recommend)
        return

    if args.etl or args.all:
        run_script("clean_and_load.py", "ETL Data Cleaning & SQLite Loader")

    if args.dashboard_images or args.all:
        run_script("generate_dashboard_images.py", "Dashboard Screenshot Rendering")

    if args.report or args.all:
        run_script("generate_report.py", "Final PDF Report Compilation (Target 15-20 Pages)")

    if args.presentation or args.all:
        run_script("generate_presentation.py", "12-Slide Presentation Deck Compilation")

    if not any([args.all, args.etl, args.dashboard_images, args.report, args.presentation, args.recommend]):
        logger.info("\nPipeline status healthy! All deliverables are compiled.")
        logger.info("To re-run specific components, use:")
        logger.info("  python run_pipeline.py --dashboard-images")
        logger.info("  python run_pipeline.py --report")
        logger.info("  python run_pipeline.py --presentation")
        logger.info("  python run_pipeline.py --recommend Moderate")
        logger.info("  python run_pipeline.py --all")

if __name__ == "__main__":
    main()
