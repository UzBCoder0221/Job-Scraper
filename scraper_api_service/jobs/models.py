from django.db import models

class Company(models.Model):
    name=models.CharField(max_length=255)
    url=models.URLField(null=True)
    logo=models.URLField(null=True)
    
    def __str__(self):
        return f"{self.name}"

class Location(models.Model):
    location = models.CharField(max_length=255)
    def __str__(self):
        return f"{self.location}"

class Tag(models.Model):
    tag = models.CharField(max_length=127)

    def __str__(self):
        return f"{self.tag}"
    
class Salary(models.Model):
    min=models.CharField(max_length=31)
    max=models.CharField(max_length=31)
    currency=models.CharField(max_length=31)
    unit=models.CharField(max_length=31)

    def __str__(self):
        return f"{self.min} - {self.max} {self.currency}"

class Job(models.Model):
    title = models.CharField(max_length=255)
    company = models.ForeignKey(Company,on_delete=models.CASCADE,related_name="company")
    description=models.TextField()
    benefits=models.TextField(null=True)
    salary=models.ForeignKey(Salary,on_delete=models.CASCADE,related_name="salary")
    employmentType=models.CharField(max_length=63)
    jobLocation=models.ManyToManyField(Location,related_name="job_location")
    applicantLocationRequirements=models.ManyToManyField(Location,related_name="requirement_job_location",blank=True)
    image=models.URLField(null=True)
    workHours=models.CharField(max_length=31,null=True)
    url=models.URLField()
    validThrough=models.DateTimeField(null=True)
    tags=models.ManyToManyField(Tag,related_name="tags",blank=True)
    posted_at=models.DateTimeField()
    scraped_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
       return f"{self.title}"
