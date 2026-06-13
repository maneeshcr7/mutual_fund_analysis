"""
Bluestock Mutual Fund Analysis - Master Execution Script
=========================================================

This script orchestrates the complete ETL pipeline, analytics, and report generation
for the Bluestock Mutual Fund Capstone Project.

Usage:
    python run_pipeline.py              # Run complete pipeline
    python run_pipeline.py --etl        # Run only ETL steps
    python run_pipeline.py --analytics  # Run only analytics
    python run_pipeline.py --reports    # Generate reports only
    python run_pipeline.py --clean      # Clean and rebuild database

Author: Bluestock Capstone Project
Version: 1.0
"""

import argparse
import sys
import os
from pathlib import Path
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('pipeline.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent / "scripts"))


def run_etl_pipeline():
    """Run the ETL pipeline: data ingestion and cleaning."""
    logger.info("=" * 60)
    logger.info("STEP 1: ETL Pipeline")
    logger.info("=" * 60)
    
    try:
        # Import and run ETL pipeline
        from scripts.etl_pipeline import main as etl_main
        logger.info("Running data ingestion...")
        datasets = etl_main()
        logger.info(f"ETL pipeline completed. Loaded {len(datasets)} datasets.")
        return True
    except Exception as e:
        logger.error(f"ETL pipeline failed: {str(e)}")
        return False


def run_data_cleaning():
    """Run data cleaning and database loading."""
    logger.info("=" * 60)
    logger.info("STEP 2: Data Cleaning & Database Loading")
    logger.info("=" * 60)
    
    try:
        from scripts.data_cleaning import main as cleaning_main
        logger.info("Running data cleaning...")
        dataframes = cleaning_main()
        logger.info("Data cleaning and database loading completed.")
        return True
    except Exception as e:
        logger.error(f"Data cleaning failed: {str(e)}")
        return False


def run_compute_metrics():
    """Compute performance metrics."""
    logger.info("=" * 60)
    logger.info("STEP 3: Performance Metrics Computation")
    logger.info("=" * 60)
    
    try:
        from scripts.compute_metrics import main as metrics_main
        logger.info("Computing performance metrics...")
        results_df = metrics_main()
        logger.info(f"Computed metrics for {len(results_df)} funds.")
        return True
    except Exception as e:
        logger.error(f"Metrics computation failed: {str(e)}")
        return False


def run_recommender():
    """Run fund recommender system."""
    logger.info("=" * 60)
    logger.info("STEP 4: Fund Recommender System")
    logger.info("=" * 60)
    
    try:
        from scripts.recommender import main as recommender_main
        logger.info("Running fund recommender...")
        recommender_main()
        logger.info("Fund recommender completed.")
        return True
    except Exception as e:
        logger.error(f"Recommender system failed: {str(e)}")
        return False


def run_live_nav_fetch():
    """Fetch live NAV data."""
    logger.info("=" * 60)
    logger.info("STEP 5: Live NAV Fetch")
    logger.info("=" * 60)
    
    try:
        from scripts.live_nav_fetch import main as nav_main
        logger.info("Fetching live NAV data...")
        nav_data = nav_main()
        logger.info(f"Fetched NAV data for {len(nav_data)} schemes.")
        return True
    except Exception as e:
        logger.error(f"Live NAV fetch failed: {str(e)}")
        return False


def generate_reports():
    """Generate final reports (PDF and PPTX)."""
    logger.info("=" * 60)
    logger.info("STEP 6: Report Generation")
    logger.info("=" * 60)
    
    try:
        # Generate PDF report
        from scripts.generate_final_report import generate_pdf
        logger.info("Generating PDF report...")
        generate_pdf()
        logger.info("PDF report generated successfully.")
        
        # Generate PowerPoint presentation
        from scripts.generate_presentation import generate_presentation
        logger.info("Generating PowerPoint presentation...")
        generate_presentation()
        logger.info("PowerPoint presentation generated successfully.")
        
        return True
    except Exception as e:
        logger.error(f"Report generation failed: {str(e)}")
        return False


def run_full_pipeline():
    """Run the complete pipeline."""
    start_time = datetime.now()
    
    logger.info("=" * 60)
    logger.info("BLUESTOCK MUTUAL FUND ANALYSIS - FULL PIPELINE")
    logger.info(f"Start Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)
    
    steps = [
        ("ETL Pipeline", run_etl_pipeline),
        ("Data Cleaning", run_data_cleaning),
        ("Performance Metrics", run_compute_metrics),
        ("Recommender System", run_recommender),
        ("Live NAV Fetch", run_live_nav_fetch),
        ("Report Generation", generate_reports)
    ]
    
    results = {}
    
    for step_name, step_func in steps:
        logger.info(f"\n{'=' * 60}")
        logger.info(f"Executing: {step_name}")
        logger.info("=" * 60)
        
        try:
            success = step_func()
            results[step_name] = "SUCCESS" if success else "FAILED"
        except Exception as e:
            logger.error(f"{step_name} failed with error: {str(e)}")
            results[step_name] = "ERROR"
    
    # Summary
    end_time = datetime.now()
    duration = end_time - start_time
    
    logger.info("\n" + "=" * 60)
    logger.info("PIPELINE EXECUTION SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Start Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"End Time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Duration: {duration}")
    logger.info("-" * 60)
    
    for step_name, status in results.items():
        logger.info(f"{step_name}: {status}")
    
    logger.info("=" * 60)
    
    # Check if all steps succeeded
    all_success = all(status == "SUCCESS" for status in results.values())
    
    if all_success:
        logger.info("✓ All pipeline steps completed successfully!")
    else:
        logger.warning("✗ Some pipeline steps failed. Check logs for details.")
    
    return all_success


def main():
    """Main entry point for the pipeline."""
    parser = argparse.ArgumentParser(
        description="Bluestock Mutual Fund Analysis Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python run_pipeline.py              # Run complete pipeline
    python run_pipeline.py --etl        # Run only ETL steps
    python run_pipeline.py --analytics  # Run only analytics
    python run_pipeline.py --reports    # Generate reports only
    python run_pipeline.py --clean      # Clean and rebuild database
        """
    )
    
    parser.add_argument(
        '--etl',
        action='store_true',
        help='Run only ETL pipeline (data ingestion and cleaning)'
    )
    
    parser.add_argument(
        '--analytics',
        action='store_true',
        help='Run only analytics (metrics and recommender)'
    )
    
    parser.add_argument(
        '--reports',
        action='store_true',
        help='Generate reports only (PDF and PPTX)'
    )
    
    parser.add_argument(
        '--clean',
        action='store_true',
        help='Clean and rebuild database'
    )
    
    parser.add_argument(
        '--nav',
        action='store_true',
        help='Fetch live NAV data only'
    )
    
    args = parser.parse_args()
    
    # If no arguments provided, run full pipeline
    if not any([args.etl, args.analytics, args.reports, args.clean, args.nav]):
        success = run_full_pipeline()
        sys.exit(0 if success else 1)
    
    # Run specific steps based on arguments
    if args.clean:
        # Remove existing database and rebuild
        db_path = Path("bluestock_mf.db")
        if db_path.exists():
            db_path.unlink()
            logger.info("Removed existing database.")
        run_data_cleaning()
    
    if args.etl:
        run_etl_pipeline()
        run_data_cleaning()
    
    if args.analytics:
        run_compute_metrics()
        run_recommender()
    
    if args.nav:
        run_live_nav_fetch()
    
    if args.reports:
        generate_reports()


if __name__ == "__main__":
    main()
