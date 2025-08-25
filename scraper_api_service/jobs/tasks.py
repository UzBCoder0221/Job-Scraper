import logging
from celery import shared_task
from django.core.management import call_command

logger = logging.getLogger("scraper")

@shared_task
def scrape_jobs_task(limit=0,catch_up=True):
    logger.info(f"Celery triggered scraper with limit={limit}")
    args=[]
    if limit:
        args.append(f"--limit={limit}")
    if catch_up:
        args.append('--catch-up')
    call_command("scrape_jobs", *args)
