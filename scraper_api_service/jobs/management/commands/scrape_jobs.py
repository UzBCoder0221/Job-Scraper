from django.core.management.base import BaseCommand
from django.conf import settings
from jobs.models import *
import requests
from fake_useragent import UserAgent
from django.utils import timezone
from lxml import html
from bs4 import BeautifulSoup
import requests
from tqdm import tqdm
import json
import re
import os
import logging
import random
import pickle

logger = logging.getLogger("watchdog")

class Command(BaseCommand):
    help = "Scrapes job listings and saves them to the database"

    def add_arguments(self, parser):
        parser.add_argument(
            "--limit",
            type=int,
            default=1,
            help="Number of jobs to scrape (optional; default is 1)",
        )    
        parser.add_argument(
            "--catch-up",
            action='store_true',
            help="An option to catch up with jobs on the site. (if not added/written then False)",
        )    

    def getDataOffsetX(self,segment_number:int) -> list:
        """
        Fetches job data from RemoteOK for a given page offset.

        Returns:
            List[Tuple[
                str,                     # title
                List[Optional[str]],      # [organization_name, organization_url, organization_logo]
                str,                     # description
                Optional[str],           # benefits
                Optional[List[Union[int, str]]],  # [min_salary, max_salary, currency, unit]
                Optional[str],           # employment_type
                Optional[List[Optional[str]]],    # country
                Optional[List[Optional[str]]],    # country_req
                Optional[str],           # image
                Optional[str],           # work_hours
                Optional[str],           # link
                Optional[str],           # valid_through
                Optional[List[str]],     # tags
                Optional[str]            # date_posted
            ]]
        
        Args:
            segment_number (int): The pagination offset to fetch jobs from.
        """
        url = f"https://remoteok.com/?&action=get_jobs&offset={segment_number}"
        headers = {
            "User-Agent": UserAgent().random,
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Connection": "keep-alive",
        }
        path_to_proxies=os.path.join(settings.BASE_DIR,'proxies.pkl')
        for _ in range(100):
            try:
                with open(path_to_proxies,'rb') as f:
                    proxy=random.choice(pickle.load(f))
                resp = requests.get(url, headers=headers,proxies={'http':proxy}).text
                break
            except Exception as e:
                logger.critical(f"100 responses from remoteok.com were unnatural/unexpected {e}",exc_info=True)
                print("Check the logs. remoteok.com might be down.")
        tree = html.fromstring(resp)

        links_and_tags = []
        for tr in tree.xpath('//tr[contains(@class,"job job-")]'):
            link = tr.get('data-url')
            tags = self.clean_attrs(raw=str(resp),link=link)
            links_and_tags.append(("https://remoteok.com"+link, tags))

        scripts = tree.xpath('//script[@type="application/ld+json"]/text()')
        job_data=[]
        for i, script in enumerate(scripts):
            data:dict = self.safe_json_load(script)
            if not data:
                print("Could not parse JSON at all")
                continue

            org = data.get('hiringOrganization', {})
            salary_info = data.get('baseSalary', {}).get('value', {})

            benefits = data.get('jobBenefits') or None
            if benefits:
                benefits = " | ".join([str(i).replace('_', ' ').capitalize() for i in benefits])

            description=BeautifulSoup(data.get('description'),'html.parser').get_text('',strip=True).replace('\xa0',' ')
            description=re.sub(r'\n+','\n',description)

            country = [f.get('address', {}).get('addressCountry') for f in data.get('jobLocation', [])] or None
            country_req = [f.get('name', {}) for f in data.get('applicantLocationRequirements', [])] or None
            salary = None
            if salary_info:
                salary = [salary_info.get('minValue'), salary_info.get('maxValue'), data.get('baseSalary', {}).get('currency'),salary_info.get('unitText')]
            job_data.append((
                data.get('title'),
                [org.get('name'), org.get('url'), org.get('logo',{}).get("url",{}) or None],
                description,
                benefits,
                salary,
                (data.get('employmentType') or "").replace('_', ' ').capitalize() if data.get('employmentType') else None,
                country,
                country_req,
                data.get('image'),
                data.get('workHours'),
                links_and_tags[i][0] if i < len(links_and_tags) else None,
                data.get('validThrough',None),
                links_and_tags[i][1] if i < len(links_and_tags) else None,
                data.get('datePosted'),
            ))
        return job_data

    def safe_json_load(self,raw: str):
        try:
            raw = re.sub(r'}\s*{', '}, {', raw)
            raw = re.sub(r',\s*([}\]])', r'\1', raw)
            return json.loads(raw)
        except Exception:
            return None

    def clean_attrs(self,raw: str, link: str) -> list:
        aa = f'data-url="{link}"'
        raw = raw[raw.find(aa) + len(aa):]
        raw = raw[:raw.find('>')]
        raw = re.sub(r'\sdata-[^=]+="[^"]*"', '', raw)
        raw = re.sub(r'\sclass="[^"]*"', '', raw)
        return (
            raw.replace('","', " ")
            .replace('"]"', "")
            .replace('title=""', "")
            .replace(f'id="job-{link.split("-")[-1]}"', "")
            .replace('="', "")
            .replace('"', "")
            .strip()
            .split()
        )
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Starting job scraping..."))
        catch_up:bool = options.get("catch_up")
        limit:int = options.get("limit")
        job_data_for_logger=None
        logger.info(f"Started to scrape {limit} batch(es) of jobs")
        pbar=tqdm(total=limit*49,desc="Scraping jobs",unit="job",)
        job_count=0
        if catch_up:
            limit=9999
            pbar.total=limit*49
            pbar.refresh()
        try:
            for i in range(limit):
                created_count=0
                inner_cycle=0
                for j in (batch_of_data:=self.getDataOffsetX(i+1)):
                    job_data_for_logger=j
                    company_name, company_url, company_logo = j[1]
                    company, _ = Company.objects.update_or_create(
                        name=company_name,
                        defaults={
                            "url": company_url,
                            "logo": company_logo,
                        }
                    )
                    salary, _ = Salary.objects.update_or_create(
                        min= j[4][0],
                        max= j[4][1],
                        currency= j[4][2],
                        unit= j[4][3]
                    )
                    job, created = Job.objects.update_or_create(
                        title=j[0],
                        company=company,
                        url=j[10],
                        posted_at=j[13],
                        defaults={
                            "description": j[2],
                            "benefits": j[3],
                            "salary": salary,
                            "employmentType": j[5],
                            "image": j[8],
                            "workHours": j[9],
                            "validThrough": j[11],
                            "scraped_at": timezone.now(),
                        }
                    )
                    if not created:
                        created_count+=1
                    if created_count==len(batch_of_data) and catch_up:
                        pbar.total=pbar.n
                        pbar.refresh()
                        pbar.close()
                        self.stdout.write(self.style.SUCCESS(f"Scraping finished. Saved {job_count} jobs."))
                        exit()
                    tags=[]
                    for i in j[12]:
                        tag, _ =Tag.objects.get_or_create(tag=i)
                        tags.append(tag)
                    job.tags.set(tags)
                    job_locations=[]
                    for i in j[6]:
                        loc, _ =Location.objects.get_or_create(location=i)
                        job_locations.append(loc)
                    job.jobLocation.set(job_locations)
                    loc_objs = []
                    for i in j[7] or []:
                        if not i:
                            continue
                        loc, _ = Location.objects.get_or_create(location=i.strip())
                        loc_objs.append(loc)
                    job.applicantLocationRequirements.set(loc_objs)
                    pbar.update(1)
                    inner_cycle+=1
                    if inner_cycle>49:
                        pbar.total+=inner_cycle-49
                        pbar.refresh()
                    job_count+=1
                
            logger.info(f"Scraped {job_count} jobs successfully")
        except Exception as _:
            error=f"Error occured while scraping job:\n\n{job_data_for_logger}\n\n"
            logger.exception(error,exc_info=True)
            self.stdout.write(self.style.ERROR("Error occured: See logs/log_error.log"))
        pbar.close()
        self.stdout.write(self.style.SUCCESS(f"Scraping finished. Saved {job_count} jobs."))
