import csv
import requests
import os
import time
from urllib.parse import urlparse


def download_images(input_csv_articles, input_csv_links, output_dir):
    """Скачивает изображения, используя артикулы из одного CSV и ссылки из другого."""

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    articles = []
    with open(input_csv_articles, 'r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        next(reader) # Пропускаем заголовок, если он есть
        for row in reader:
            articles.append(row[0]) # Добавляем артикул в список

    with open(input_csv_links, 'r', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        for i, row in enumerate(reader): # Добавляем индекс строки
            try:
                article = articles[i] # Берем артикул по индексу
            except IndexError:
                print("Не найден артикул для строки", i+1)
                continue

            for j in range(1, 11):
                image_url = row.get(f'Ссылка на фото {j}')
                if image_url:
                    try:
                        response = requests.get(image_url, stream=True, timeout=10)
                        response.raise_for_status()

                        parsed_url = urlparse(image_url)
                        ext = os.path.splitext(parsed_url.path)[1] or '.jpg'

                        filename = f"{article}{f'_{j}' if j > 1 else ''}{ext}"
                        filepath = os.path.join(output_dir, filename)

                        with open(filepath, 'wb') as f:
                            for chunk in response.iter_content(chunk_size=8192):
                                f.write(chunk)

                        print(f"Скачано изображение: {filename}")
                        time.sleep(1)

                    except requests.exceptions.RequestException as e:
                        print(f"Ошибка при скачивании изображения {image_url}: {e}")
                    except Exception as e:
                        print(f"Произошла ошибка: {e}")


if __name__ == "__main__":
    input_csv_articles = "1.csv"  # Файл с артикулами
    input_csv_links = "product_specs.csv"  # Файл со ссылками на изображения
    output_image_dir = "images"

    download_images(input_csv_articles, input_csv_links, output_image_dir)
    print("Закачка изображений завершена.")
