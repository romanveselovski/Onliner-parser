import csv
import requests
import re
from bs4 import BeautifulSoup
import time
import sys
import logging

# Настройка логирования
logging.basicConfig(filename='parser.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')


def parse_csv_and_create_csv(input_csv, output_csv):

    all_fieldnames = []
    all_rows = []

    with open(input_csv, 'r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        total_rows = sum(1 for row in reader)
        csvfile.seek(0)

        processed_rows = 0
        start_time = time.time()

        for row in reader:
            product_code, url = row
            row_data = {}

            try:
                # Удаление дефисов из URL (потенциально проблемное место, проверьте корректность)
                url = url.replace("-", "")
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'
                }
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')

                # Парсинг ссылок на изображения
                fotorama_div = soup.find('div', id='product-gallery-fotorama')
                if fotorama_div:
                    image_tags = fotorama_div.find_all('img')  # Находим все img внутри div
                    for i, img_tag in enumerate(image_tags):
                        row_data[f'Ссылка на фото {i + 1}'] = img_tag.get('href')  # Извлекаем href
                        if f'Ссылка на фото {i + 1}' not in all_fieldnames:
                            all_fieldnames.append(f'Ссылка на фото {i + 1}')

                specs_div = soup.find('div', id='specs')
                if specs_div:
                    specs_table = specs_div.find('table', class_='product-specs__table')
                    if specs_table:
                        for tr in specs_table.find_all('tr'):
                            if 'product-specs__table-title' in tr.get('class', []):
                                continue

                            tds = tr.find_all('td')
                            if len(tds) == 2:
                                field_name = tds[0].contents[0].strip().replace('\n', '').replace('\r', '') if len(tds[0].contents) > 0 and isinstance(tds[0].contents[0], str) else ""
                                value_span = tds[1].find('span', class_='value__text')
                                value = re.sub(r'\s+', ' ', value_span.text).strip() if value_span else ""

                                if tds[1].find('span', class_='i-x'):
                                    value = "Нет"

                                if tds[1].find('span', class_='i-tip'):
                                    value = "Да" + (", " + value if value else "")

                                row_data[field_name] = value
                                if field_name not in all_fieldnames:
                                    all_fieldnames.append(field_name)
                    else:
                        logging.error(f"Таблица характеристик не найдена внутри div#specs на странице {url}")
                else:
                    logging.error(f"Div с id='specs' не найден на странице {url}")

            except requests.exceptions.RequestException as e:
                logging.error(f"Ошибка при загрузке страницы {url}: {e}")
            except Exception as e:
                logging.error(f"Произошла ошибка при обработке страницы {url}: {e}")

            finally:
                processed_rows += 1
                elapsed_time = time.time() - start_time
                progress = (processed_rows / total_rows) * 100
                time_remaining = (elapsed_time / processed_rows) * (total_rows - processed_rows) if processed_rows > 0 else 0
                print(f"\rОбработано: {processed_rows}/{total_rows} ({progress:.2f}%) | Время: {elapsed_time:.2f} сек | Осталось: {time_remaining:.2f} сек", end="")
                sys.stdout.flush()
                all_rows.append(row_data)
                time.sleep(1)

    with open(output_csv, 'w', newline='', encoding='utf-8-sig') as output_csvfile:
        writer = csv.DictWriter(output_csvfile, fieldnames=all_fieldnames, delimiter=';', extrasaction='ignore')
        writer.writeheader()
        writer.writerows(all_rows)

    print("\nПарсинг завершен!")


# Пример использования
input_csv_file = "links_2.csv"
output_csv_file = "product_specs_2.csv"
parse_csv_and_create_csv(input_csv_file, output_csv_file)