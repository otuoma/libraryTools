from django import forms

class GrobidUploadForm(forms.Form):
    file = forms.FileField(label='Select a PDF article', help_text='Upload a research article in PDF format.')
