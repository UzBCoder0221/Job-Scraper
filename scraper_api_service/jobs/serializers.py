from rest_framework import serializers
from jobs.models import Job, Location, Company, Tag, Salary


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        exclude = ['id']
class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        exclude = ['id']
class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        exclude = ['id']
class SalarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Salary
        exclude = ['id']

class JobSerializer(serializers.ModelSerializer):
    company = CompanySerializer()
    salary = SalarySerializer()
    jobLocation=LocationSerializer(many=True)
    applicantLocationRequirements=LocationSerializer(many=True)
    tags=TagSerializer(many=True)
    class Meta:
        model = Job
        fields = "__all__"