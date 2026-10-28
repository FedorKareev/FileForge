from django.shortcuts import render
from django.core.files.uploadedfile import SimpleUploadedFile
import cv2
import numpy as np
from pyzbar.pyzbar import decode

def index(request):
    result = None
    error = None
    if request.method == 'POST':
        uploaded_file = request.FILES.get('file')
        if not uploaded_file:
            error = 'Выберите изображение.'
        else:
            try:
                file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
                image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
                decoded_objects = decode(image)
                
                if decoded_objects:
                    result = "Найденные QR-коды:\n"
                    for obj in decoded_objects:
                        result += obj.data.decode('utf-8') + "\n"
                else:
                    error = "На картинке не найден QR-код."
            except Exception as e:
                error = f"Ошибка обработки: {e}"

    return render(request, 'qrscan.html', {'result': result, 'error': error})