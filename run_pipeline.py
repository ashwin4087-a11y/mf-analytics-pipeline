"""
Bluestock Mutual Fund Analytics - Master Pipeline Script

This script documents and can execute the core ETL and analytics pipeline.
Note: Expensive operations (like regenerating EDA charts or Jupyter notebooks)
are guarded to prevent accidental overwriting of final deliverables.
"""
import subprocess
import sys
from pathlib import Path

def run_script(script_name):
    print(f"Running {script_name}...")
    result = subprocess.run([sys.executable, script_name], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error running {script_name}:\n{result.stderr}")
    else:
        print(f"Successfully finished {script_name}.")
        
def main():
    print("--- Bluestock Mutual Fund Analytics Pipeline ---")
    
    # Check if database exists
    if Path("bluestock_mf.db").exists():
        print("Database bluestock_mf.db already exists. Skipping ETL to avoid overwriting data.")
    else:
        print("Database not found. You would normally run:")
        print("  python clean_and_load.py")
        
    print("\nNext, the EDA charts and insights were generated via:")
    print("  python run_eda.py")
    
    print("\nThe advanced analytics and performance metrics notebooks were generated via:")
    print("  python generate_perf_notebook.py")
    print("  python create_notebook.py")
    
    print("\nTo see the fund recommender in action, run:")
    print("  python recommender.py Moderate")
    
    print("\nPipeline overview complete. All deliverables are pre-compiled and available in the root directory.")

if __name__ == "__main__":
    main()
