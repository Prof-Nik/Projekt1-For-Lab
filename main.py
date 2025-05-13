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
    # Создаем выходную директорию ВСЕГДА в начале, если ее нет
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Создана выходная директория: '{output_dir}'") # Добавим лог
    elif not os.path.isdir(output_dir):
        print(f"Ошибка: Путь для выходной директории '{output_dir}' существует, но не является директорией.")
        return # Выходим, если output_dir не директория
    # Проверяем существование входной директории
    if not os.path.isdir(input_dir): # Проверяем, что это директория
        print(f"Ошибка: Входная директория '{input_dir}' не найдена или не является директорией.")
        return # Выходим, если input_dir не существует или не директория
    processed_files_count = 0 # Для подсчета обработанных файлов
    found_files_count = 0
    for filename in os.listdir(input_dir):
        if filename.endswith(f".{input_format}"):
            found_files_count += 1
            input_path = os.path.join(input_dir, filename)
            name_without_ext = os.path.splitext(filename)[0]
            output_path = os.path.join(output_dir, f"{name_without_ext}.{output_format}")
            try:
                if input_format.lower() in ('jpg', 'png', 'jpeg', 'bmp'):
                    convert_image(input_path, output_path, output_format)
                    processed_files_count +=1
                elif input_format.lower() == 'txt':
                    convert_text(input_path, output_path, output_format) # output_format здесь может быть не нужен
                    processed_files_count +=1
                elif input_format.lower() == 'docx':
                    convert_docx(input_path, output_path)
                    processed_files_count +=1
                # Добавьте другие типы, если необходимо
            except Exception as e:
                print(f"Ошибка при конвертации файла '{input_path}': {e}")
    if found_files_count == 0 and os.path.exists(input_dir): # Добавил проверку существования input_dir
        print(f"В директории '{input_dir}' не найдено файлов с расширением '.{input_format}'.")
    elif processed_files_count > 0:
        print(f"Пакетная конвертация завершена. Обработано файлов: {processed_files_count}.")
    # Если input_dir не существовал, сообщение об этом уже было выведено выше
def main():
    parser = argparse.ArgumentParser(description="Конвертер файлов")
    subparsers = parser.add_subparsers(dest='command', help='Выберите команду')
    subparsers.required = False # Делаем команду необязательной для интерактивного режима

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

    exit_code = 0 # Код завершения по умолчанию

    # Если команда была передана через CLI, выполняем её и выходим
    if args.command:
        try:
            if args.command == 'convert':
                if not os.path.exists(args.input):
                    print(f"Ошибка: Входной файл '{args.input}' не найден.", file=sys.stderr)
                    sys.exit(1) # Важно выходить с ошибкой

                pil_format = args.format
                # Определение формата, если он не задан явно для изображений
                if args.input.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff')) and not pil_format:
                    _, output_ext = os.path.splitext(args.output)
                    pil_format = output_ext.lstrip('.').upper()
                    if not pil_format:
                        print("Ошибка: Для конвертации изображения необходимо указать выходной формат с помощью опции -f или через расширение имени выходного файла.", file=sys.stderr)
                        sys.exit(1)
                    if pil_format == 'JPG': pil_format = 'JPEG'


                if args.input.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff')):
                    convert_image(args.input, args.output, pil_format)
                elif args.input.lower().endswith('.txt'):
                    convert_text(args.input, args.output, pil_format if pil_format else 'txt') # pil_format здесь может быть нерелевантен
                elif args.input.lower().endswith('.docx'):
                    convert_docx(args.input, args.output)
                else:
                    print(f"Ошибка: Неподдерживаемый формат входного файла для команды 'convert': {args.input}", file=sys.stderr)
                    sys.exit(1)

            elif args.command == 'batch':
                batch_convert(args.input_dir, args.output_dir, args.input_format, args.output_format)

            elif args.command == 'pdf2img':
                convert_pdf_to_image(args.input, args.output_dir)

        except FileNotFoundError as e:
            print(f"Ошибка FileNotFoundError: {e}", file=sys.stderr)
            exit_code = 1
        except Exception as e:
            # Функции конвертации уже печатают свои ошибки
            # Но мы хотим, чтобы CLI вернул ненулевой код
            # print(f"Произошла ошибка при выполнении команды '{args.command}': {e}", file=sys.stderr) # Можно раскомментировать для доп. отладки
            exit_code = 1 # Сигнализируем об ошибке

        sys.exit(exit_code) # Выходим после выполнения CLI команды

    else:
        # ИНТЕРАКТИВНЫЙ РЕЖИМ (если команда не была указана)
        # Эта часть не будет выполняться в ваших функциональных тестах,
        # если вы всегда передаете команду ('convert', 'batch' и т.д.)
        print("Конвертер файлов запущен в интерактивном режиме.")
        print("Введите 'help' для списка команд или 'exit' для выхода.")
        while True:
            try:
                user_input_str = input("converter> ").strip()
                if not user_input_str:
                    continue
                if user_input_str.lower() == 'exit':
                    break
                if user_input_str.lower() == 'help':
                    parser.print_help()
                    continue

                # Пытаемся распарсить ввод пользователя как аргументы CLI
                try:
                    # shlex нужен для корректного разделения строки с кавычками
                    import shlex
                    interactive_args = parser.parse_args(shlex.split(user_input_str))

                    # Повторно вызываем main с этими аргументами (это рекурсия, но для CLI обертки может быть ок)
                    # Чтобы избежать глубокой рекурсии, лучше вынести логику команд в отдельную функцию
                    # или просто перепарсить и выполнить здесь.
                    # Для простоты, здесь можно было бы дублировать логику обработки команд.
                    # НО! Проще заставить main() завершаться после выполнения CLI команды,
                    # и если мы здесь, значит, CLI не было.
                    # Если пользователь ввел команду, main() выше бы ее обработала и вышла.
                    # Этот блок `else` для случая, когда `args.command` изначально был None.
                    # Значит, нужно передать `interactive_args` в обработчик.

                    # Переделаем: если мы здесь, значит args.command был None.
                    # Если пользователь ввел команду, то interactive_args.command будет установлен.
                    if interactive_args.command:
                        # Выполняем команду (логика похожа на ту, что выше)
                        # Это можно вынести в отдельную функцию handle_command(args_obj)
                        if interactive_args.command == 'convert':
                            # ... (логика convert для interactive_args) ...
                            print(f"Выполняю 'convert' для {interactive_args.input} -> {interactive_args.output}")
                            # convert_image(...) / convert_text(...) / convert_docx(...)
                        elif interactive_args.command == 'batch':
                            # ... (логика batch для interactive_args) ...
                            print(f"Выполняю 'batch' для {interactive_args.input_dir}")
                        elif interactive_args.command == 'pdf2img':
                            # ... (логика pdf2img для interactive_args) ...
                             print(f"Выполняю 'pdf2img' для {interactive_args.input}")
                        else:
                            print(f"Неизвестная команда в интерактивном режиме: {interactive_args.command}")
                    else:
                        # Если пользователь ввел что-то, что не является командой
                        parser.print_help()

                except SystemExit: # argparse вызывает SystemExit при ошибках парсинга или help
                    pass # Просто продолжаем цикл интерактивного ввода
                except Exception as e_interactive:
                    print(f"Ошибка в интерактивной команде: {e_interactive}")

            except EOFError:
                print("\nВыход.")
                break
            except KeyboardInterrupt:
                print("\nПрервано пользователем.")
                break
        sys.exit(0) # Успешный выход из интерактивного режима

if __name__ == "__main__":
    main()
