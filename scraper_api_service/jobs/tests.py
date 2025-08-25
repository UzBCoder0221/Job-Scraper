from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from .models import Company, Location, Tag, Salary, Job


class JobAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.company = Company.objects.create(name="Company", url="http://google.com", logo="http://google.com")
        self.salary = Salary.objects.create(min="1000", max="2000", currency="USD", unit="month")
        self.location1 = Location.objects.create(location="New York")
        self.location2 = Location.objects.create(location="Remote")
        self.tag1 = Tag.objects.create(tag="AI")
        self.tag2 = Tag.objects.create(tag="Python")

        self.job = Job.objects.create(
            title="Backend Developer",
            company=self.company,
            description="Hire wrokers to work on APIs and backend systems.",
            benefits="Health insurance | Remote work",
            salary=self.salary,
            employmentType="Full-time",
            image="http://google.com",
            workHours="Flexible",
            url="http://google.com",
            validThrough=timezone.now() + timezone.timedelta(days=30),
            posted_at=timezone.now(),
        )
        self.job.jobLocation.add(self.location1)
        self.job.applicantLocationRequirements.add(self.location2)
        self.job.tags.add(self.tag1, self.tag2)

    def test_list_jobs(self):
        response = self.client.get("/api/jobs/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        results = data.get("results", [])
        self.assertGreaterEqual(len(results), 1)

    def test_search_jobs(self):
        response = self.client.get("/api/jobs/?search=Backend")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        results = data.get("results", [])
        self.assertTrue(any(job["title"] == "Backend Developer" for job in results))

    def test_ordering_jobs(self):
        response = self.client.get("/api/jobs/?ordering=-posted_at")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        results = data.get("results", [])
        self.assertGreaterEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "Backend Developer")

    def test_filter_jobs(self):
        response = self.client.get("/api/jobs/?employmentType=Full-time")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        results = data.get("results", [])
        self.assertTrue(all(job["employmentType"] == "Full-time" for job in results))

    def test_job_detail(self):
        job_id = Job.objects.first().id
        response = self.client.get(f"/api/jobs/{job_id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["id"], job_id)

