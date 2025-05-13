import os
import shutil
import pytest
from main import batch_convert # Убедитесь, что импорт идет из вашего файла

TEST_DATA_DIR_INTEGRATION = os.path.join(os.path.dirname(__file__), "test_data_integration")
OUTPUT_DIR_INTEGRATION = os.path.join(os.path.dirname(__file__), "test_output_integration")

@pytest.fixture(scope="module", autouse=True)
def setup_integration_dirs():
    """Создает и очищает директории для интеграционных тестов."""
    # Очистка перед тестами
    if os.path.exists(TEST_DATA_DIR_INTEGRATION):
        shutil.rmtree(TEST_DATA_DIR_INTEGRATION)
    if os.path.exists(OUTPUT_DIR_INTEGRATION):
        shutil.rmtree(OUTPUT_DIR_INTEGRATION)

    os.makedirs(TEST_DATA_DIR_INTEGRATION, exist_ok=True)
    os.makedirs(OUTPUT_DIR_INTEGRATION, exist_ok=True)

    # Копируем базовые тестовые файлы для интеграции
    base_test_data_dir = os.path.join(os.path.dirname(__file__), "test_data")
    shutil.copy(os.path.join(base_test_data_dir, "sample.jpg"), os.path.join(TEST_DATA_DIR_INTEGRATION, "img1.jpg"))
    shutil.copy(os.path.join(base_test_data_dir, "sample.png"), os.path.join(TEST_DATA_DIR_INTEGRATION, "img2.png"))
    shutil.copy(os.path.join(base_test_data_dir, "sample.txt"), os.path.join(TEST_DATA_DIR_INTEGRATION, "doc1.txt"))
    shutil.copy(os.path.join(base_test_data_dir, "sample.docx"), os.path.join(TEST_DATA_DIR_INTEGRATION, "report.docx"))
    # Создадим файл другого формата, который не должен быть обработан
    with open(os.path.join(TEST_DATA_DIR_INTEGRATION, "other.log"), "w") as f:
        f.write("log data")

    yield
    # Очистка после всех тестов модуля (можно убрать)
    # shutil.rmtree(TEST_DATA_DIR_INTEGRATION)
    # shutil.rmtree(OUTPUT_DIR_INTEGRATION)

def test_batch_convert_jpg_to_png():
    input_dir = TEST_DATA_DIR_INTEGRATION
    output_dir = os.path.join(OUTPUT_DIR_INTEGRATION, "jpg_to_png")
    batch_convert(input_dir, output_dir, "jpg", "png")

    assert os.path.exists(os.path.join(output_dir, "img1.png"))
    assert not os.path.exists(os.path.join(output_dir, "img2.jpg")) # png не должен был конвертироваться
    assert not os.path.exists(os.path.join(output_dir, "doc1.png"))
    assert not os.path.exists(os.path.join(output_dir, "other.png"))

def test_batch_convert_docx_to_txt():
    input_dir = TEST_DATA_DIR_INTEGRATION
    output_dir = os.path.join(OUTPUT_DIR_INTEGRATION, "docx_to_txt")
    batch_convert(input_dir, output_dir, "docx", "txt")

    expected_output_path = os.path.join(output_dir, "report.txt")
    assert os.path.exists(expected_output_path)
    with open(expected_output_path, 'r', encoding='utf-8') as f:
        content = f.read()
    assert "Test DOCX content" in content
    assert not os.path.exists(os.path.join(output_dir, "img1.txt"))

def test_batch_convert_empty_input_format(capsys):
    input_dir = TEST_DATA_DIR_INTEGRATION
    output_dir = os.path.join(OUTPUT_DIR_INTEGRATION, "empty_format")
    # Подаем формат, которого нет
    batch_convert(input_dir, output_dir, "xyz", "abc")
    # Проверяем, что выходная директория пуста (или содержит только .gitkeep, если создается)
    # или проверяем вывод в консоль, если ваша функция что-то печатает
    if os.path.exists(output_dir): # Директория создается функцией
        assert not any(f.endswith(".abc") for f in os.listdir(output_dir))
    # Можно также проверить вывод, если ваша функция печатает сообщение о том, что файлы не найдены

def test_batch_convert_non_existent_input_dir(capsys):
    input_dir = os.path.join(TEST_DATA_DIR_INTEGRATION, "non_existent_dir")
    output_dir = os.path.join(OUTPUT_DIR_INTEGRATION, "output_for_non_existent_input")
    # Ваша функция batch_convert должна обрабатывать это, не падая
    # Например, печатать ошибку и не создавать output_dir или создавать пустой
    batch_convert(input_dir, output_dir, "jpg", "png")
    # Зависит от реализации batch_convert, как она обрабатывает несуществующую input_dir
    # В текущей реализации вашего скрипта, она ничего не печатает и не падает,
    # просто цикл for filename in os.listdir(input_dir): не выполнится
    # и output_dir может быть создан пустым.
    assert os.path.exists(output_dir) # output_dir создается в любом случае
    assert len(os.listdir(output_dir)) == 0 # Должен быть пуст