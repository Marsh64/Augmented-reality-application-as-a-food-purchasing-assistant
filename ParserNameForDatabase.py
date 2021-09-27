from bs4 import BeautifulSoup
import requests

Barcode = '4600823093010'
BarcodeList = "https://barcode-list.ru/barcode/RU/%D0%9F%D0%BE%D0%B8%D1%81%D0%BA.htm?barcode=" + Barcode
resp = requests.get(BarcodeList)
soup = BeautifulSoup(resp.text, 'lxml')
name = str(soup.select_one("td:nth-of-type(3)"))
print(name[31:len(name)-5])
