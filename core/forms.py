from django import forms
from .models import ExamPaper

class ExamPaperUploadForm(forms.ModelForm):
    class Meta:
        model = ExamPaper
        fields = ['pdf_file']



class ExamPaperMetadataForm(forms.ModelForm):
    LEVEL_CHOICES = [
        ('Bachelors', 'Bachelors'),
        ('Masters', 'Masters'),
        ('PhD', 'PhD'),
        ('Diploma', 'Diploma'),
        ('Certificate', 'Certificate'),
    ]
    EXAM_TYPE_CHOICES = [
        ('Regular Exam', 'Regular Exam'),
        ('Supplementary Exam', 'Supplementary Exam'),
    ]

    level_of_study = forms.ChoiceField(choices=LEVEL_CHOICES, initial='Bachelors', required=False)
    exam_type = forms.ChoiceField(choices=EXAM_TYPE_CHOICES, initial='Regular Exam', required=False)
    pdf_path = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = ExamPaper
        fields = [
            'academic_year',
            'year_of_study',
            'semester',
            'level_of_study',
            'exam_type',
            'course_title',
            'course_code',
            'program',
            'collection',
            'pdf_path',
        ]
