import shutil
import uuid
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from django.conf import settings
from django.http import FileResponse
from django.shortcuts import render

from .services import convert_pdf_to_images, save_uploaded_file

def index(request):
    result = None
    error = None
    if request.method == 'POST':
        uploaded_file = request.FILES.get('file')
        if not uploaded_file:
            error = 'Выберите PDF-файл.'
        elif Path(uploaded_file.name).suffix.lower() != '.pdf':
            error = 'Поддерживаются только PDF-файлы.'
        else:
            job_id = uuid.uuid4().hex
            job_dir = Path(settings.MEDIA_ROOT) / 'jobs' / job_id
            source_path = save_uploaded_file(
                uploaded_file.read(), job_dir / 'source.pdf'
            )

            try:
                image_paths = convert_pdf_to_images(source_path, job_dir / 'pages')
                archive_path = job_dir / 'converted_pages.zip'
                with ZipFile(archive_path, 'w', ZIP_DEFLATED) as archive:
                    for image_path in image_paths:
                        archive.write(image_path, image_path.name)
            except (OSError, RuntimeError, ValueError) as exc:
                shutil.rmtree(job_dir, ignore_errors=True)
                error = f'Не удалось обработать PDF: {exc}'
            else:
                request.session['download_path'] = str(archive_path)
                result = f'Готово: страниц сконвертировано — {len(image_paths)}'

    return render(request, 'index.html', {'result': result, 'error': error})

def download(request):
    archive_path = Path(request.session.get('download_path', ''))
    media_root = Path(settings.MEDIA_ROOT).resolve()

    try:
        safe_archive_path = archive_path.resolve()
        is_in_media_root = media_root == safe_archive_path or media_root in safe_archive_path.parents
    except (OSError, RuntimeError):
        is_in_media_root = False

    if not is_in_media_root or not safe_archive_path.is_file():
        return render(request, 'index.html', {
            'error': 'Сначала загрузите и сконвертируйте PDF-файл.'
        }, status=404)

    return FileResponse(
        safe_archive_path.open('rb'),
        content_type='application/zip',
        as_attachment=True,
        filename='converted_pages.zip',
    )