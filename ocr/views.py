from django.shortcuts import render
import pytesseract
from PIL import Image
import io

def index(request):
    result = None
    error = None
    if request.method == 'POST':
        uploaded_file = request.FILES.get('file')
        if not uploaded_file:
            error = 'Выберите изображение.'
        else:
            try:
                image = Image.open(io.BytesIO(uploaded_file.read()))
                text = pytesseract.image_to_string(image, lang='rus+eng')
                if text.strip():
                    result = text
                else:
                    error = "Текст на изображении не распознан."
            except Exception as e:
                error = f"Ошибка: {e}"

    return render(request, 'ocr.html', {'result': result, 'error': error})