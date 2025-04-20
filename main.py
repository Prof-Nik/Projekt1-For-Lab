import os
import sys
import argparse
from PIL import Image
import docx2txt
from pdf2image import convert_from_path
def convert_image(input_path, output_path, output_format):
    try:
        img = Image.open(input_path)
        img.save(output_path, output_format)
        print(f"Изображение '{input_path}' успешно сконвертировано в '{output_path}'")
    except Exception as e:
        print(f"Ошибка при конвертации изображения '{input_path}': {e}")
def convert_text(input_path, output_path, output_format):
    try:
        with open(input_path, 'r', encoding='utf-8') as f: # Улучшена обработка кодировки
            text = f.read()
        with open(output_path, 'w', encoding='utf-8') as f: # Улучшена обработка кодировки
            f.write(text)
        print(f"Текстовый файл '{input_path}' успешно сконвертирован в '{output_path}'")
    except Exception as e:
        print(f"Ошибка при конвертации текстового файла '{input_path}': {e}")
def convert_docx(input_path, output_path):
    try:
        text = docx2txt.process(input_path)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"Документ docx '{input_path}' успешно сконвертирован в '{output_path}'")
    except Exception as e:
        print(f"Ошибка при конвертации документа docx '{input_path}': {e}")
def convert_pdf_to_image(input_path, output_dir):
    try:
        pages = convert_from_path(input_path)
        for i, page in enumerate(pages):
            output_path = os.path.join(output_dir, f"page_{i+1}.jpg")
            page.save(output_path, "JPEG")
            print(f"Страница {i+1} из PDF '{input_path}' сохранена в '{output_path}'")
    except Exception as e:
        print(f"Ошибка при конвертации PDF '{input_path}': {e}")
def batch_convert(input_dir, output_dir, input_format, output_format):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir) # Создаем выходную директорию, если ее нет
    for filename in os.listdir(input_dir):
        if filename.endswith(f".{input_format}"):
            input_path = os.path.join(input_dir, filename)
            name_without_ext = os.path.splitext(filename)[0]
            output_path = os.path.join(output_dir, f"{name_without_ext}.{output_format}")
            try: # try-except блок перемещен внутрь цикла
                if input_format.lower() in ('jpg', 'png', 'jpeg', 'bmp'):
                    convert_image(input_path, output_path, output_format)
                elif input_format.lower() == 'txt':
                    convert_text(input_path, output_path, output_format)
                elif input_format.lower() == 'docx':
                    convert_docx(input_path, output_path)
            except Exception as e:
                print(f"Ошибка при конвертации файла '{input_path}': {e}")
def main():
    parser = argparse.ArgumentParser(description="Конвертер файлов")
    subparsers = parser.add_subparsers(dest='command', help='Выберите команду')
    # Парсер для одиночной конвертации
    convert_parser = subparsers.add_parser('convert', help='Конвертировать один файл')
    convert_parser.add_argument('input', help='Путь к входному файлу')
    convert_parser.add_argument('output', help='Путь к выходному файлу')
    convert_parser.add_argument('-f', '--format', help='Формат выходного файла (для изображений)')
    # Парсер для пакетной конвертации
    batch_parser = subparsers.add_parser('batch', help='Пакетная конвертация')
    batch_parser.add_argument('input_dir', help='Путь к входной директории')
    batch_parser.add_argument('output_dir', help='Путь к выходной директории')
    batch_parser.add_argument('input_format', help='Входной формат файлов (например, jpg, png, txt, docx)')
    batch_parser.add_argument('output_format', help='Выходной формат файлов (например, jpg, png, txt)')
    pdf_parser = subparsers.add_parser('pdf2img', help='Конвертировать PDF в изображения')
    pdf_parser.add_argument('input', help='Путь к PDF файлу')
    pdf_parser.add_argument('output_dir', help='Путь к выходной директории')
    args = parser.parse_args()

if __name__ == "__main__":
    main()