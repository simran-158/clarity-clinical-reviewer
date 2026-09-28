"""Bounded decoding; extracted document contents are always untrusted data."""
import io
import warnings
from dataclasses import dataclass, field
from pathlib import Path
import pymupdf
from PIL import Image, ImageOps, UnidentifiedImageError

MAX_BYTES = 10 * 1024 * 1024
MAX_CHARS = 20000
MAX_PAGES = 10
MAX_PIXELS = 20_000_000

class DocumentError(ValueError):
    pass

@dataclass
class PreparedPage:
    page: int
    text: str = ''
    image: bytes | None = None
    warnings: list[str] = field(default_factory=list)

@dataclass
class PreparedDocument:
    pages: list[PreparedPage]
    input_type: str


def prepare_text(text: str) -> PreparedDocument:
    if not text.strip():
        raise DocumentError('Enter clinical notes before starting a review.')
    if len(text) > MAX_CHARS:
        raise DocumentError('Use at most 20,000 characters per review.')
    return PreparedDocument([PreparedPage(1, text.strip())], 'text')


def prepare_upload(data: bytes, filename: str) -> PreparedDocument:
    if not data:
        raise DocumentError('The file is empty. Choose another document.')
    if len(data) > MAX_BYTES:
        raise DocumentError('The file exceeds 10 MB. Upload a smaller file.')
    suffix = Path(filename).suffix.lower()
    if suffix == '.pdf':
        if not data.startswith(b'%PDF-'):
            raise DocumentError('This file is not a valid PDF.')
        return _pdf(data)
    if suffix not in {'.jpg', '.jpeg', '.png', '.webp'}:
        raise DocumentError('Choose a PDF, PNG, JPEG, or WebP file.')
    try:
        with warnings.catch_warnings():
            warnings.simplefilter('error', Image.DecompressionBombWarning)
            with Image.open(io.BytesIO(data)) as source:
                expected = {'.png': 'PNG', '.jpg': 'JPEG', '.jpeg': 'JPEG', '.webp': 'WEBP'}[suffix]
                if source.format != expected:
                    raise DocumentError('The file contents do not match its image extension.')
                if source.width * source.height > MAX_PIXELS:
                    raise DocumentError('Image is too large. Resize to less than 20 megapixels.')
                source.load()
                image = ImageOps.exif_transpose(source).convert('RGB')
                image.thumbnail((2400, 2400))
                output = io.BytesIO()
                image.save(output, format='PNG')
        return PreparedDocument([PreparedPage(1, image=output.getvalue())], 'image')
    except DocumentError:
        raise
    except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError, Image.DecompressionBombWarning) as exc:
        raise DocumentError('The image cannot be read. Try a clear, undamaged image.') from exc


def _pdf(data: bytes) -> PreparedDocument:
    try:
        with pymupdf.open(stream=data, filetype='pdf') as pdf:
            if pdf.needs_pass:
                raise DocumentError('Remove the PDF password before uploading it.')
            if not 1 <= len(pdf) <= MAX_PAGES:
                raise DocumentError('PDFs must contain between 1 and 10 pages.')
            pages = []
            total = 0
            for index, page in enumerate(pdf):
                text = page.get_text().strip()
                total += len(text)
                if total > MAX_CHARS:
                    raise DocumentError('The PDF contains more than 20,000 characters. Upload a shorter document.')
                # A scan may coexist with a text header. Inspect image coverage as well as text length.
                image_area = sum(info['bbox'][2] * 0 + pymupdf.Rect(info['bbox']).get_area() for info in page.get_image_info())
                needs_vision = len(text) < 60 or image_area > page.rect.get_area() * 0.25
                image = None
                if needs_vision:
                    scale = min(2.0, 2200 / max(page.rect.width, page.rect.height, 1))
                    image = page.get_pixmap(matrix=pymupdf.Matrix(scale, scale), alpha=False).tobytes('png')
                pages.append(PreparedPage(index + 1, text, image))
        return PreparedDocument(pages, 'pdf')
    except DocumentError:
        raise
    except Exception as exc:
        raise DocumentError('The PDF is damaged or unreadable. Export it again and retry.') from exc
