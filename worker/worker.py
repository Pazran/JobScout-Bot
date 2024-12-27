import time
import random
import threading
from pprint import pprint
from scraper.scraper import fetch_data
from database.database import create_table, insert_job, job_exists
from config.config import URL_TO_SCRAPE
import logging

logger = logging.getLogger(__name__)

# Flag to stop worker
stop_worker = False

def check_for_new_jobs():
    """Check for new jobs and add them to the database if not already present."""
    logger.info("Checking for new jobs...")

    # Fetch the current list of jobs
    current_jobs = fetch_data(URL_TO_SCRAPE)

    if current_jobs:
        new_jobs = []
        for job in current_jobs:
            # Check if the job is already in the database
            if not job_exists(job['uniqueId']):
                insert_job(job)  # Add the job to the database
                new_jobs.append(job)

        if new_jobs:
            logger.info("Found %s new job(s).", len(new_jobs))
            for job in new_jobs:
                logger.debug("New job: %s", dict(job))
                # Pretty-print each new job to the console
                print("\n--- New Job Found ---")
                pprint(job, sort_dicts=False)
                print("---------------------")
        else:
            logger.info("No new jobs found.")
    else:
        logger.info("No jobs fetched, skipping this check.")

def start_scraping_worker(interval=random.uniform(60, 120)):
    """Start the worker that runs periodically to check for new jobs."""
    global stop_worker

    # Ensure the database table exists
    create_table()

    while not stop_worker:
        check_for_new_jobs()
        time.sleep(interval)  # Wait for the specified interval before checking again