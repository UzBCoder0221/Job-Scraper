from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import *
from .serializers import *
from .filters import JobFilter

class JobViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter,]
    filterset_class = JobFilter
    search_fields = ["title", "company__name", "description", "benefits", "employmentType"]
    ordering_fields = ["posted_at", "scraped_at", "validThrough"]
    ordering = ["-posted_at"] 
