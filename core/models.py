
from django.db import models

class ExamPaper(models.Model):
	academic_year = models.CharField(max_length=20)
	year_of_study = models.CharField(max_length=20)
	semester = models.CharField(max_length=20)
	level_of_study = models.CharField(max_length=20)
	exam_type = models.CharField(max_length=25)
	course_title = models.CharField(max_length=250)
	program = models.CharField(max_length=250)
	course_code = models.CharField(max_length=20)
	collection = models.CharField(max_length=100, blank=True)
	pdf_file = models.FileField(upload_to='exam_papers/')
	uploaded_at = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"{self.course_code} - {self.course_title} ({self.academic_year})"
