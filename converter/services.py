from pathlib import Path

import fitz


def save_uploaded_file(file_bytes: bytes, destination_path: str | Path) -> Path:
    file_path = Path(destination_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    file_path.write_bytes(file_bytes)
    return file_path


def convert_pdf_to_images(pdf_path: str | Path, output_folder: str | Path) -> list[Path]:
    output_dir = Path(output_folder)
    output_dir.mkdir(parents=True, exist_ok=True)
    created_images = []

    with fitz.open(pdf_path) as document:
        for page_number, page in enumerate(document, start=1):
            pixmap = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
            image_path = output_dir / f"page_{page_number}.png"
            pixmap.save(str(image_path))
            created_images.append(image_path)

    return created_images