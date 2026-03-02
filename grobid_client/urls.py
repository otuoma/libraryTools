from django.urls import path
from . import views

urlpatterns = [
    path('', views.grobid_upload, name='grobid_upload'),
    path('api/generate-jats', views.generate_jats, name='generate_jats'),
]
