import requests
from config import DJANGO_API_BASE

class APIClient:
    def __init__(self, base_url=DJANGO_API_BASE) -> None:
        self.base_url = base_url
        self.session = requests.Session()
    
    def get_jobs(self, params:dict={}):
        url = f"{self.base_url}/jobs/"
        temp_params={"search":params.get("search",None)}
        if params.get("page",1)>1:
            if self.session.get(url,params=temp_params).json().get('count',0) and self.session.get(url,params=temp_params).json().get('next',0):
                resp = self.session.get(url,params=params)
                resp.raise_for_status()
                results=resp.json()
            else:
                results={}
        else:
            resp = self.session.get(url,params=params)
            resp.raise_for_status()
            results=resp.json()

        return results
    
    def get_job(self, job_id):
        url = f"{self.base_url}/jobs/{job_id}/"
        resp = self.session.get(url)
        resp.raise_for_status()
        return resp.json()