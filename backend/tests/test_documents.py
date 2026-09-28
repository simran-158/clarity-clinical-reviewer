import io
import pytest
import pymupdf
from PIL import Image
from app.documents import prepare_text, prepare_upload, DocumentError


def pdf_bytes(pages=1, mixed=False):
    doc = pymupdf.open()
    for n in range(pages):
        page = doc.new_page()
        if not mixed or n == 0:
            page.insert_text((50, 50), 'SYNTHETIC NOTE. Alex Example reports a cough for three days. Temperature 37 C.')
    return doc.tobytes()

@pytest.mark.parametrize('text', ['', '   ', 'a' * 20001])
def test_invalid_text(text):
    with pytest.raises(DocumentError):
        prepare_text(text)


def test_irrelevant_text_is_preserved_for_analysis():
    assert prepare_text('Shopping list: apples and rice').pages[0].text == 'Shopping list: apples and rice'

@pytest.mark.parametrize('data,name', [(b'not pdf', 'note.pdf'), (b'\x89PNG\r\n\x1a\ncorrupt', 'note.png'), (b'x' * (10 * 1024 * 1024 + 1), 'note.pdf'), (pdf_bytes(11), 'long.pdf'), (pdf_bytes(), 'note.png')])
def test_bad_upload_rejected(data, name):
    with pytest.raises(DocumentError):
        prepare_upload(data, name)


def test_mixed_pdf_routes_every_page():
    result = prepare_upload(pdf_bytes(2, mixed=True), 'mixed.pdf')
    assert [p.page for p in result.pages] == [1, 2]
    assert 'cough' in result.pages[0].text
    assert result.pages[1].image is not None


def test_image_is_decoded_and_normalized():
    buf = io.BytesIO()
    Image.new('RGB', (300, 200), 'white').save(buf, 'PNG')
    page = prepare_upload(buf.getvalue(), 'sample.png').pages[0]
    assert page.image.startswith(b'\x89PNG')


def test_encrypted_pdf_has_actionable_error():
    doc = pymupdf.open()
    doc.new_page()
    data = doc.tobytes(encryption=pymupdf.PDF_ENCRYPT_AES_256, owner_pw='secret', user_pw='secret')
    with pytest.raises(DocumentError, match='password'):
        prepare_upload(data, 'locked.pdf')
