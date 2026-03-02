import requests
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .forms import GrobidUploadForm
from .utils import convert_tei_to_jats, extract_metadata

@csrf_exempt
def grobid_upload(request):
    if request.method == 'POST':
        form = GrobidUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['file']
            
            # Prepare the request to Grobid
            url = f"{settings.GROBID_SERVER_URL.rstrip('/')}/api/processFulltextDocument"
            files = {'input': uploaded_file}
            
            try:
                response = requests.post(url, files=files)
                response.raise_for_status()
                tei_content = response.text
                jats_content = convert_tei_to_jats(tei_content)
                metadata = extract_metadata(tei_content)
                return JsonResponse({'status': 'success', 'tei': tei_content, 'jats': jats_content, 'metadata': metadata})
            except requests.RequestException as e:
                return JsonResponse({'status': 'error', 'message': f"Error communicating with Grobid server: {e}"}, status=500)
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid form data'}, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)

@csrf_exempt
def generate_jats(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            tei_content = data.get('tei')
            metadata = data.get('metadata')
            
            if not tei_content:
                return JsonResponse({'status': 'error', 'message': 'TEI content is required'}, status=400)
            
            jats_content = convert_tei_to_jats(tei_content, metadata)
            return JsonResponse({'status': 'success', 'jats': jats_content})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)
