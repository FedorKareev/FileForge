from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZipFile

import fitz
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from .services import convert_pdf_to_images


class ConverterServiceTests(TestCase):
	def test_pdf_is_converted_to_png_pages(self):
		with TemporaryDirectory() as temp_dir:
			temp_path = Path(temp_dir)
			pdf_path = temp_path / 'source.pdf'
			document = fitz.open()
			document.new_page()
			document.new_page()
			document.save(pdf_path)
			document.close()

			image_paths = convert_pdf_to_images(pdf_path, temp_path / 'pages')

			self.assertEqual(len(image_paths), 2)
			self.assertTrue(all(path.suffix == '.png' for path in image_paths))


class ConverterViewTests(TestCase):
	def test_upload_converts_pdf_and_downloads_zip(self):
		with TemporaryDirectory() as temp_dir:
			with self.settings(MEDIA_ROOT=temp_dir):
				pdf = fitz.open()
				pdf.new_page()
				pdf_bytes = pdf.tobytes()
				pdf.close()

				response = self.client.post(
					'/',
					{
						'file': SimpleUploadedFile(
							'document.pdf', pdf_bytes, content_type='application/pdf'
						),
						'convert': '1',
					},
					format='multipart',
				)

				self.assertEqual(response.status_code, 200)
				self.assertContains(response, 'страниц сконвертировано')

				download_response = self.client.get('/download/')
				self.assertEqual(download_response.status_code, 200)
				self.assertEqual(download_response['Content-Type'], 'application/zip')
				archive_bytes = b''.join(download_response.streaming_content)
				download_response.close()
				with ZipFile(BytesIO(archive_bytes)) as archive:
					self.assertEqual(archive.namelist(), ['page_1.png'])

# Create your tests here.
