from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    result = None
    if request.method == 'POST':
        if 'convert' in request.POST:
            file = request.FILES.get('file')
            if file:
                result = file.name
    return render(request, 'index.html', {'result': result})

def download(request):
    response = HttpResponse(b'', content_type='application/octet-stream')
    response['Content-Disposition'] = 'attachment; filename="file.txt"'
    return response