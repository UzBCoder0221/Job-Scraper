from django_filters import rest_framework as filters
from .models import Job

class JobFilter(filters.FilterSet):
    jobLocation = filters.CharFilter(field_name="jobLocation__location", lookup_expr="icontains")
    applicantLocationRequirements = filters.CharFilter(field_name="applicantLocationRequirements__location", lookup_expr="icontains")
    tags = filters.CharFilter(field_name="tags__tag", lookup_expr="icontains")
    employmentType = filters.CharFilter(field_name="employmentType", lookup_expr="icontains")

    class Meta:
        model = Job
        fields = ["jobLocation", "applicantLocationRequirements", "tags", "employmentType"]
