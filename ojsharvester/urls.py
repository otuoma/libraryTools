
from django.contrib import admin
from django.urls import include, path
from ojsharvester.views import HarvestIssue

urlpatterns = [
    path('', HarvestIssue.as_view(), name='harvest_issue'),
]
