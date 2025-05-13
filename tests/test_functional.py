import os
import shutil
import subprocess
import pytest
import sys
from PIL import Image


CONVERTER_SCRIPT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "main.py")

TEST_DATA_DIR_FUNC = os.path.join(os.path.dirname(__file__), "test_data")
OUTPUT_DIR_FUNC = os.path.join(os.path.dirname(__file__), "test_output_functional")

@pytest.fixture(scope="module", autouse=True)
def manage_functional_output_dir():
    if os.path.exists(OUTPUT_DIR_FUNC):
        shutil.rmtree(OUTPUT_DIR_FUNC)
    os.makedirs(OUTPUT_DIR_FUNC, exist_ok=True)
    yield
    # shutil.rmtree(OUTPUT_DIR_FUNC) # Очистка

def run_script(args_list):
    """Хелпер для запуска скрипта с аргументами."""
    return subprocess.run([sys.executable, CONVERTER_SCRIPT] + args_list, capture_output=True, text=True, check=False)

# --- Тесты для команды 'convert' ---
def test_cli_convert_jpg_to_png():
    input_file = os.path.join(TEST_DATA_DIR_FUNC, "sample.jpg")
    output_file = os.path.join(OUTPUT_DIR_FUNC, "cli_converted.png")

    result = run_script(["convert", input_file, output_file, "-f", "PNG"])

    assert result.returncode == 0, f"Скрипт завершился с ошибкой: {result.stderr}"
    assert os.path.exists(output_file)
    assert "успешно сконвертировано" in result.stdout
    try:
        img = Image.open(output_file)
        assert img.format == "PNG"
    except Exception as e:
        pytest.fail(f"Не удалось открыть или проверить сконвертированное изображение: {e}")

def test_cli_convert_docx_to_txt():
    input_file = os.path.join(TEST_DATA_DIR_FUNC, "sample.docx")
    output_file = os.path.join(OUTPUT_DIR_FUNC, "cli_docx.txt")

    result = run_script(["convert", input_file, output_file]) # Формат для txt не нужен

    assert result.returncode == 0, f"Скрипт завершился с ошибкой: {result.stderr}"
    assert os.path.exists(output_file)
    assert "успешно сконвертирован" in result.stdout # Проверьте точный текст из вашей функции
    with open(output_file, 'r', encoding='utf-8') as f:
        content = f.read()
    assert "Test DOCX content" in content

def test_cli_convert_missing_args():
    result = run_script(["convert", os.path.join(TEST_DATA_DIR_FUNC, "sample.jpg")]) # Не хватает output
    assert result.returncode != 0 # Ожидаем ошибку от argparse
    assert "error: the following arguments are required: output" in result.stderr.lower() # Проверяем stderr

def test_cli_convert_input_not_found():
    input_file = os.path.join(TEST_DATA_DIR_FUNC, "non_existent.jpg")
    output_file = os.path.join(OUTPUT_DIR_FUNC, "cli_not_created.png")
    result = run_script(["convert", input_file, output_file, "-f", "PNG"])
    # Ваша функция main должна обрабатывать это, например, через проверку os.path.exists
    # или передавать ошибку из функции конвертации
    # В текущей версии main, она передаст ошибку из функции convert_image
    assert result.returncode == 0 # т.к. вы ловите Exception и печатаете
    assert "Ошибка при конвертации изображения" in result.stdout
    assert not os.path.exists(output_file)


# --- Тесты для команды 'batch' ---
@pytest.fixture(scope="module")
def setup_batch_cli_dirs():
    input_batch_dir = os.path.join(OUTPUT_DIR_FUNC, "batch_input_cli")
    output_batch_dir_target = os.path.join(OUTPUT_DIR_FUNC, "batch_output_cli")

    if os.path.exists(input_batch_dir): shutil.rmtree(input_batch_dir)
    if os.path.exists(output_batch_dir_target): shutil.rmtree(output_batch_dir_target)
    os.makedirs(input_batch_dir)
    # Не создаем output_batch_dir_target, скрипт должен это сделать

    shutil.copy(os.path.join(TEST_DATA_DIR_FUNC, "sample.jpg"), os.path.join(input_batch_dir, "img1.jpg"))
    shutil.copy(os.path.join(TEST_DATA_DIR_FUNC, "sample.png"), os.path.join(input_batch_dir, "img2.png")) # Для проверки фильтрации
    return input_batch_dir, output_batch_dir_target

def test_cli_batch_convert_jpg_to_png(setup_batch_cli_dirs):
    input_dir, output_dir = setup_batch_cli_dirs

    result = run_script(["batch", input_dir, output_dir, "jpg", "png"])

    assert result.returncode == 0, f"Скрипт завершился с ошибкой: {result.stderr}"
    assert os.path.exists(os.path.join(output_dir, "img1.png"))
    assert not os.path.exists(os.path.join(output_dir, "img2.png")) # т.к. входной формат был png
    assert "успешно сконвертировано" in result.stdout # или другой вывод от batch_convert

# --- Тесты для команды 'pdf2img' ---
@pytest.mark.skipif(not shutil.which("pdftoppm"), reason="Poppler (pdftoppm) не найден в PATH")
def test_cli_pdf2img():
    input_file = os.path.join(TEST_DATA_DIR_FUNC, "sample.pdf")
    output_pdf_pages_dir = os.path.join(OUTPUT_DIR_FUNC, "cli_pdf_pages")
    # Не создаем output_pdf_pages_dir, скрипт должен это сделать, если его нет

    result = run_script(["pdf2img", input_file, output_pdf_pages_dir])

    assert result.returncode == 0, f"Скрипт завершился с ошибкой: {result.stderr}"
    assert os.path.exists(output_pdf_pages_dir)
    expected_page = os.path.join(output_pdf_pages_dir, "page_1.jpg")
    assert os.path.exists(expected_page)
    assert f"Страница 1 из PDF '{input_file}' сохранена" in result.stdout
    try:
        img = Image.open(expected_page)
        assert img.format == "JPEG"
    except Exception as e:
        pytest.fail(f"Не удалось открыть или проверить изображение страницы PDF: {e}")


def test_cli_unknown_command():
    result = run_script(["unknown_command_test"])
    assert result.returncode != 0
    assert "invalid choice: 'unknown_command_test'" in result.stderr.lower()

def test_cli_no_command():
    result = run_script([])
    assert result.returncode != 0
    assert "usage: main.py" in result.stderr.lower() # argparse выведет usage
    assert "error: the following arguments are required: command" in result.stderr.lower()