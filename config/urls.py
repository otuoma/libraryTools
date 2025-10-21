
from django.contrib import admin
from django.urls import path
from core import views as core_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('upload/', core_views.upload_exam_paper, name='upload_exam_paper'),
    path('', core_views.upload_exam_paper, name='upload_exam_paper'),
    path('verify/', core_views.verify_metadata, name='verify_metadata'),
]
