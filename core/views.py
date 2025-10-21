
from cgitb import text
from importlib.metadata import metadata
from django.shortcuts import render, redirect
from urllib3 import request
from .forms import ExamPaperUploadForm, ExamPaperMetadataForm
from .models import ExamPaper
import pdfplumber, string
from dspace_rest_client.client import DSpaceClient, Item, Bundle, Bitstream
from my_secrets import secrets
import re

# Configuration from environment variables
URL = secrets.get("API_URL")
USERNAME = secrets.get("API_USERNAME")
PASSWORD = secrets.get("API_PASSWORD")

d = DSpaceClient(api_endpoint=URL, username=USERNAME, password=PASSWORD, fake_user_agent=True)

# if not authenticated:
#     print('Error logging in! Giving up.')
#     sys.exit(1)

def upload_exam_paper(request):
	
	if request.method == 'POST':
		form = ExamPaperUploadForm(request.POST, request.FILES)
		if form.is_valid():
			exam_paper = form.save(commit=False)
			pdf_file = request.FILES['pdf_file']
			# Save PDF to file system
			exam_paper.pdf_file = pdf_file
			exam_paper.save()
			pdf_path = exam_paper.pdf_file.path
			# Extract text from first page
			with pdfplumber.open(pdf_path) as pdf:
				first_page = pdf.pages[0]
				text = first_page.extract_text()
			# Extract metadata from text
			metadata = extract_metadata(text)
			# Pre-fill metadata form, including pdf_path
			metadata_form = ExamPaperMetadataForm(initial={**metadata, 'pdf_file': pdf_file, 'pdf_path': pdf_path})
			request.session['pdf_file'] = pdf_path
			request.session['metadata'] = metadata
			request.session['extracted_text'] = text
			program = metadata.get('program', '')
			collections = search_collection(f"{program}")
			return render(request, 'core/verify_metadata.html', {'form': metadata_form, 'extracted_text': text, 'program': program, 'collections': collections, 'pdf_path': pdf_path})
	else:
		form = ExamPaperUploadForm()
	return render(request, 'core/upload_exam_paper.html', {'form': form})

def verify_metadata(request):
	if request.method == 'POST':
		authenticated = d.authenticate()
		form = ExamPaperMetadataForm(request.POST, request.FILES)
		if form.is_valid():
			form.save()
			pdf_file = f"{form.cleaned_data.get('pdf_path', '')}"
			created_item = create_item(form)
			if isinstance(created_item, Item) and created_item.uuid is not None:
				print(f"==========Item created successfully with UUID: {created_item.uuid}================")
			else:
				return render(request, 'core/verify_metadata.html', {'form': form, 'pdf_path': pdf_file})
			
			uploaded_bitstream = upload_item_bitstream(created_item, pdf_file=pdf_file)
			if(uploaded_bitstream):
				# Clear session data
				request.session.flush()
				return redirect('upload_exam_paper')
			return render(request, 'core/verify_metadata.html', {'form': form, 'pdf_path': pdf_file})
		else:
			pdf_file = request.POST.get('pdf_path', '')
			return render(request, 'core/verify_metadata.html', {'form': form, 'pdf_path': pdf_file})
	else:
		metadata = request.session.get('metadata', {})
		pdf_file = request.session.get('pdf_file', None)
		extracted_text = request.session.get('extracted_text', '')
		pdf_path = request.session.get('pdf_path', '')
		form = ExamPaperMetadataForm(initial={**metadata, 'pdf_file': pdf_file, 'pdf_path': pdf_path})
    
		return render(request, 'core/verify_metadata.html', {'form': form, 'extracted_text': extracted_text, 'pdf_path': pdf_path})

def extract_metadata(text):
	# Improved regex-based extraction
	metadata = {}
	# Academic year
	match = re.search(r'(\d{4}/\d{4}) ACADEMIC YEAR', text)
	metadata['academic_year'] = match.group(1) if match else ''
	# Year of study
	match = re.search(r'(FIRST|SECOND|THIRD|FOURTH|FIFTH|SIXTH) YEAR', text)
	year_map = {
		'FIRST': 'First Year',
		'SECOND': 'Second Year',
		'THIRD': 'Third Year',
		'FOURTH': 'Fourth Year',
		'FIFTH': 'Fifth Year',
		'SIXTH': 'Sixth Year',
	}
	metadata['year_of_study'] = year_map.get(match.group(1), '') if match else ''
	# Semester
	match = re.search(r'(FIRST|SECOND) SEMESTER', text)
	sem_map = {
		'FIRST': 'First Semester',
		'SECOND': 'Second Semester',
	}
	metadata['semester'] = sem_map.get(match.group(1), '') if match else ''
	# Level of study
	# match = re.search(r'FOR THE DEGREE OF\s+([A-Z ]+)', text)
	match = re.search(r'FOR THE DEGREE OF\s*(.+?)(?=\n[A-Z ]+:|$)', text, re.DOTALL)
	level = match.group(1).strip().title().replace(':', '') if match else ''
	
	# Normalize level to dropdown values
	
	if 'Bachelor' in level:
		level = 'Bachelors'
	elif 'PhD' in level:
		level = 'PhD'
	elif 'Master' in level:
		level = 'Masters'
	elif 'Diploma' in level:
		level = 'Diploma'
	elif 'Certificate' in level:
		level = 'Certificate'
	else:
		level = ''
	metadata['level_of_study'] = level
	# Exam type
	match = re.search(r'(REGULAR|SUPPLEMENTARY) EXAMINATIONS', text)
	exam_type = ''
	if match:
		if match.group(1) == 'REGULAR':
			exam_type = 'Regular Exam'
		elif match.group(1) == 'SUPPLEMENTARY':
			exam_type = 'Supplementary Exam'
	metadata['exam_type'] = exam_type
	# Course title
	# match = re.search(r'COURSE TITLE: ([A-Z ]+)', text)
	match = re.search(r'COURSE TITLE:\s*(.+?)(?=\n[A-Z ]+:|$)', text, re.DOTALL)

	metadata['course_title'] = match.group(1).strip().title() if match else ''
	# Course code
	match = re.search(r'COURSE CODE: ([A-Z0-9 ]+)', text)
	metadata['course_code'] = match.group(1).strip() if match else ''

	match = re.search(r'FOR THE DEGREE OF\s+(.+?)(?=\nCOURSE CODE:)', text, re.DOTALL | re.IGNORECASE)
	program = match.group(1).strip().translate(str.maketrans('', '', string.punctuation)).title() if match else ''
	if not program:
		match = re.search(r'FOR THE DEGREE OF:\s+(.+?)(?=\nCOURSE CODE:)', text, re.DOTALL | re.IGNORECASE)
		program = match.group(1).strip().translate(str.maketrans('', '', string.punctuation)).title() if match else ''

	# If there are multiple 'Bachelor' occurrences, keep only up to the first
	lower_program = program.lower()
	first_bachelor = lower_program.find('bachelor')
	if first_bachelor != -1:
		second_bachelor = lower_program.find('bachelor', first_bachelor + 1)
		if second_bachelor != -1:
			# Only keep up to the first occurrence
			program = program[:second_bachelor].strip()

	metadata['program'] = program
	return metadata

def search_collection(collection_name):
	# Search collections by name using DSpace REST API
	# Use a query that matches the collection_name
	cleaned_collection_name = re.sub(r'\b(?:msc|bsc)\b', '', collection_name, flags=re.IGNORECASE).strip()
	search_results = d.search_objects(query=f"{cleaned_collection_name}", dso_type='collection', page=0, size=500)
	print(f"=========Found {len(search_results)} collections matching '{collection_name}'==========")
	collections = []
	for collection in search_results:
		collections.append({
			"collection_name": collection.name,
			"collection_uuid": collection.uuid
		})
	return collections

def upload_item_bitstream(item: Item, pdf_file)-> bool:
	if item is None or not isinstance(item, Item):
		print("Invalid item provided for bitstream upload.")
		return False
	
	bundle = d.create_bundle(parent=item, name="ORIGINAL")
	metadata = item.metadata
	if isinstance(bundle, Bundle) and bundle.uuid is not None:
		print(f'New bundle created! UUID: {bundle.uuid}')

		bitstream_metadata = {
			'dc.description':
				[{"value": "Past Exam Paper PDF", 'language': 'en',
				'authority': None, 'confidence': -1, 'place': 0}]
		}
		filename = pdf_file.split('/')[-1] if '/' in pdf_file else pdf_file.split('\\')[-1]
		# file_name = f"{metadata.get('karupp.coursecode', 'ExamPaper')}__{metadata.get('karupp.yearofstudy', '')}.pdf"

		new_bitstream = d.create_bitstream(bundle=bundle, name=filename,
                                   path=pdf_file, mime='application/pdf', metadata=bitstream_metadata)
		if isinstance(new_bitstream, Bitstream) and new_bitstream.uuid is not None:
			print(f'New bitstream created! UUID: {new_bitstream.uuid}')
			return True
		else:
			print('Error! Giving up.')
			return False
	else:
		print('Error! Giving up.')
		return False

def create_item(metadata: ExamPaperMetadataForm):
	item_data = {
		"name": metadata.cleaned_data.get('course_title', ''),
		"metadata": {
			"karupp.coursecode": [{
					"value": metadata.cleaned_data.get('course_code', ''),
					"language": "en",
					"authority": None,
					"confidence": -1
				}],
			"dc.title": [
				{
					"value": metadata.cleaned_data.get('course_title', ''),
					"language": "en",
					"authority": None,
					"confidence": -1
				}
			],
			"karupp.academicyear": [
				{
					"value": metadata.cleaned_data.get('academic_year', ''),
					"language": "en",
					"authority": None,
					"confidence": -1
				}
			],
			"karupp.studylevel": [
				{
					"value": metadata.cleaned_data.get('level_of_study', ''),
					"language": "en",
					"authority": None,
					"confidence": -1
				}
			],
			"karupp.yearofstudy": [
				{
					"value": metadata.cleaned_data.get('year_of_study', ''),
					"language": "en",
					"authority": None,
					"confidence": -1
				}
			],
			"karupp.semester": [
				{
					"value": metadata.cleaned_data.get('semester', ''),
					"language": "en",
					"authority": None,
					"confidence": -1
				}
			],
			"karupp.examtype": [
				{
					"value": metadata.cleaned_data.get('exam_type', ''),
					"language": "en",
					"authority": None,
					"confidence": -1
				}
			]
		},
		"inArchive": True,
		"discoverable": True,
		"withdrawn": False,
		"type": "item"
	}

	item = Item(item_data)
	try:
		new_item = d.create_item(parent=metadata.cleaned_data.get('program', ''), item=item)
	except Exception as e:
		print(f"Error creating item: {e}")
		return None
	if isinstance(new_item, Item) and new_item.uuid is not None:
		print(f'New item created! Handle: {new_item.handle}')
		return new_item
	else:
		print('Error! Giving up.')
		return None

	
