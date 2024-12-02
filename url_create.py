import csv

def create_links(csv_file, output_file):

 with open(csv_file, 'r', encoding='utf-8') as infile, \
   open(output_file, 'w', encoding='utf-8', newline='') as outfile:
  reader = csv.reader(infile)
  writer = csv.writer(outfile, delimiter=';', quoting=csv.QUOTE_ALL)

  for row in reader:
   first_value = row[0].lower().replace('-', '')
   second_value = row[1]
   link = f"https://catalog.onliner.by/{second_value}/gappo/{first_value}"
   writer.writerow([first_value, link])

# Пример использования
csv_file = 'qwerty.csv'
output_file = 'links_2.csv'
create_links(csv_file, output_file)

