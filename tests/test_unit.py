import os
import shutil
import pytest
from PIL import Image
from main import (
    convert_image,
    convert_text,
    convert_docx,
    convert_pdf_to_image,
)

# Пути к тестовым данным
TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), "test_data")
TXT_FILE = os.path.join(TEST_DATA_DIR, "sample.txt")
JPG_FILE = os.path.join(TEST_DATA_DIR, "sample.jpg")
PNG_FILE = os.path.join(TEST_DATA_DIR, "sample.png")
DOCX_FILE = os.path.join(TEST_DATA_DIR, "sample.docx")
PDF_FILE = os.path.join(TEST_DATA_DIR, "sample.pdf")

# Временная директория для выходных файлов тестов
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "test_output_unit")

@pytest.fixture(scope="session", autouse=True)
def manage_output_dir():
    """Создает и очищает временную директорию для выходных файлов перед и после тестов."""
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    yield
    # Очистка после всех тестов в сессии (можно убрать, если нужно посмотреть результаты)
    # shutil.rmtree(OUTPUT_DIR)


# --- Тесты для convert_image ---
def test_convert_image_jpg_to_png():
    input_path = JPG_FILE
    output_path = os.path.join(OUTPUT_DIR, "converted_from_jpg.png")
    convert_image(input_path, output_path, "PNG")
    assert os.path.exists(output_path)
    try:
        img = Image.open(output_path)
        assert img.format == "PNG"
    except Exception as e:
        pytest.fail(f"Не удалось открыть или проверить сконвертированное изображение: {e}")

def test_convert_image_png_to_jpg():
    input_path = PNG_FILE
    output_path = os.path.join(OUTPUT_DIR, "converted_from_png.jpg")
    convert_image(input_path, output_path, "JPEG") # Pillow использует 'JPEG' для .jpg
    assert os.path.exists(output_path)
    try:
        img = Image.open(output_path)
        assert img.format == "JPEG"
    except Exception as e:
        pytest.fail(f"Не удалось открыть или проверить сконвертированное изображение: {e}")

def test_convert_image_non_existent_input(capsys):
    input_path = os.path.join(TEST_DATA_DIR, "non_existent.jpg")
    output_path = os.path.join(OUTPUT_DIR, "wont_be_created.png")
    convert_image(input_path, output_path, "PNG")
    captured = capsys.readouterr()
    assert "Ошибка при конвертации изображения" in captured.out # Проверяем вывод об ошибке
    assert not os.path.exists(output_path)


# --- Тесты для convert_text ---
def test_convert_text_successful():
    input_path = TXT_FILE
    output_path = os.path.join(OUTPUT_DIR, "converted.txt")
    convert_text(input_path, output_path, "txt") # 3-й аргумент для convert_text игнорируется
    assert os.path.exists(output_path)
    with open(output_path, 'r', encoding='utf-8') as f:
        content = f.read()
    with open(input_path, 'r', encoding='utf-8') as f_orig:
        original_content = f_orig.read()
    assert content == original_content

def test_convert_text_non_existent_input(capsys):
    input_path = os.path.join(TEST_DATA_DIR, "non_existent.txt")
    output_path = os.path.join(OUTPUT_DIR, "wont_be_created.txt")
    convert_text(input_path, output_path, "txt")
    captured = capsys.readouterr()
    assert "Ошибка при конвертации текстового файла" in captured.out
    assert not os.path.exists(output_path)


# --- Тесты для convert_docx ---
def test_convert_docx_successful():
    input_path = DOCX_FILE
    output_path = os.path.join(OUTPUT_DIR, "converted_from_docx.txt")
    convert_docx(input_path, output_path)
    assert os.path.exists(output_path)
    with open(output_path, 'r', encoding='utf-8') as f:
        content = f.read()
    assert "Test DOCX content" in content # Примерное содержимое

def test_convert_docx_non_existent_input(capsys):
    input_path = os.path.join(TEST_DATA_DIR, "non_existent.docx")
    output_path = os.path.join(OUTPUT_DIR, "wont_be_created_docx.txt")
    convert_docx(input_path, output_path)
    captured = capsys.readouterr()
    assert "Ошибка при конвертации документа docx" in captured.out
    assert not os.path.exists(output_path)


# --- Тесты для convert_pdf_to_image ---
# Эти тесты могут быть медленными и зависят от Poppler
@pytest.mark.skipif(not shutil.which("pdftoppm"), reason="Poppler (pdftoppm) не найден в PATH")
def test_convert_pdf_to_image_successful():
    input_path = PDF_FILE
    pdf_output_pages_dir = os.path.join(OUTPUT_DIR, "pdf_pages")
    if not os.path.exists(pdf_output_pages_dir):
        os.makedirs(pdf_output_pages_dir)

    convert_pdf_to_image(input_path, pdf_output_pages_dir)

    # Проверяем, что создана хотя бы одна страница
    # Для нашего одностраничного PDF ожидаем page_1.jpg
    expected_page_path = os.path.join(pdf_output_pages_dir, "page_1.jpg")
    assert os.path.exists(expected_page_path), f"Ожидаемый файл {expected_page_path} не найден"

    try:
        img = Image.open(expected_page_path)
        assert img.format == "JPEG"
    except Exception as e:
        pytest.fail(f"Не удалось открыть или проверить изображение страницы PDF: {e}")

@pytest.mark.skipif(not shutil.which("pdftoppm"), reason="Poppler (pdftoppm) не найден в PATH")
def test_convert_pdf_to_image_non_existent_input(capsys):
    input_path = os.path.join(TEST_DATA_DIR, "non_existent.pdf")
    pdf_output_pages_dir = os.path.join(OUTPUT_DIR, "pdf_pages_non_existent")
    # Директория может создаваться внутри функции, так что ее отсутствие до вызова - ок

    convert_pdf_to_image(input_path, pdf_output_pages_dir)
    captured = capsys.readouterr()
    # Ваша функция convert_pdf_to_image выводит сообщение об ошибке, если файл не найден
    # Но само исключение pdf2image.exceptions.PDFOpenError может быть поймано позже
    # Убедитесь, что ваша функция печатает что-то при FileNotFoundError,
    # либо измените проверку на ожидаемое исключение от pdf2image
    assert "Ошибка при конвертации PDF" in captured.out or "PDF файл не найден" in captured.out
    assert not os.listdir(pdf_output_pages_dir if os.path.exists(pdf_output_pages_dir) else [])