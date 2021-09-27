from flask import Flask, render_template, url_for
from flask_sqlalchemy import SQLAlchemy
from bs4 import BeautifulSoup
import requests
from flask import abort
from peewee import *

#Базы данных
db = SqliteDatabase('PlaceAndProduct.sq')

class Product(Model):
    barcode = IntegerField()
    productname = CharField()
    shopname = CharField()
    shopid = IntegerField()
    price = FloatField()
    categories = CharField()
    class Meta:
        database = db

class ShopAdress(Model):
    shopadress = CharField()
    shopid = IntegerField()
    shopname = CharField()
    class Meta:
        database = db

class categories(Model):
    category = IntegerField()
    recom = CharField()
    namecategory = CharField()
    class Meta:
        database = db

app = Flask(__name__)


@app.route('/')
@app.route('/home')
def about():
    return "Hello"


#Контроллер поиска имени товаре по штрихкоду
@app.route('/api/barcode/info/<string:Barcode>', methods=['GET'])
def gets(Barcode):
    BarcodeList = "https://barcode-list.ru/barcode/RU/%D0%9F%D0%BE%D0%B8%D1%81%D0%BA.htm?barcode=" + Barcode
    resp = requests.get(BarcodeList)
    soup = BeautifulSoup(resp.text, 'lxml')
    name = str(soup.select_one("td:nth-of-type(3)"))
    return (name[31:len(name) - 5])


#Контроллер поиск ближайших магазинов с этим же товаром c более низкой ценой
#принимать будт строку с баркодом и кординатами начального местополодения.
@app.route('/api/shopadress/coords,barcode/<string:Cordnow>/<string:Barcode>', methods=['GET'])
def getNear(Barcode, Cordnow):
    mindist = 2  # здесь условно
    mindistshopcord = ""
    pricenow = 1000 # здесь условно
    Identific = 0
    IdentificPrice = 0
    x1, y1 = map(float, Cordnow.split())
    for i in Product.select():
        if i.barcode == int(Barcode):
            Identific = i.shopid
            IdentificPrice = i.price
        for k in ShopAdress.select():
            if k.shopid == Identific:
                x2, y2 = map(float, k.shopadress.split())
                if ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5 < mindist and IdentificPrice <= pricenow:
                    dist = ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5
                    pricenow = IdentificPrice
                    mindistshopcord = k.shopadress
    if mindistshopcord == "":
        return("0")
    else:
        BarcodeList = "https://barcode-list.ru/barcode/RU/%D0%9F%D0%BE%D0%B8%D1%81%D0%BA.htm?barcode=" + Barcode
        resp = requests.get(BarcodeList)
        soup = BeautifulSoup(resp.text, 'lxml')
        name = str(soup.select_one("td:nth-of-type(3)"))
        name = name[31:len(name) - 5]
        prop = 0.01
        dist = str(round(dist/prop))
        stroka = "1" + dist + mindistshopcord + name
        print(stroka)
        return (stroka)


#Контроллер показа рекомендациий о товаре
@app.route('/api/recomendation/<string:Barcode>', methods=['GET'])
def getRecomendation(Barcode):
    recomendation = ''
    cat = ''
    Barcode = int(Barcode)
    for i in Product.select():
        if Barcode == i.barcode:
            cat = i.categories
            break
    lcat = []
    for k in range(len(cat)):
        lcat = lcat + list(cat[0])
        cat = cat[1:]
    #В lcat получается cписок из строковых номеров категорий товаров
    for j in range(len(lcat)):
        c = int(lcat[j])
        for m in categories.select():
            if m.category == c:
                recomendation  = recomendation + m.recom
    if recomendation == '':
        return ('Рекомендаций не обнаружено')
    else:
        return(recomendation)


#Контроллер сохранение информации о товаре, то есть в каком магазине и где этот магазин расположен, если его нет в БД
@app.route('/api/shopbase/add/<string:Barcode>/<string:shopname>/<string:Price>/<string:cordnow>', methods=['GET'])
def addProduct(Barcode, shopname, Price, cordnow):
    print("Получен запрос с " + Barcode)
    Price = float(Price)
    shopid = 0

    BarcodeList = "https://barcode-list.ru/barcode/RU/%D0%9F%D0%BE%D0%B8%D1%81%D0%BA.htm?barcode=" + Barcode
    resp = requests.get(BarcodeList)
    soup = BeautifulSoup(resp.text, 'lxml')
    name = str(soup.select_one("td:nth-of-type(3)"))
    eatname = name[31:len(name) - 5]

    if shopname == 'Пятерочка':
        shopid = 1
    elif shopname == 'Магнит':
        shopid = 2
    elif shopname == 'Перекрёсток':
        shopid = 3
    elif shopname == 'Перекресток':
        shopid = 3
    elif shopname == 'Ашан':
        shopid = 4
    elif shopname == 'Дикси':
        shopid = 5

    Barcode = int(Barcode)
    eat = Product.create(barcode = Barcode, productname = eatname, shopname = shopname, shopid = shopid, price = Price)
    place = ShopAdress.create(shopid = shopid, shopadress = cordnow, shopname = shopname)
    return ('Ваш товар добавлен')

'''
#Контроллер список ближайших магазинов
@app.route('/api/shopadress/<string:cordnow>', methods=['GET'])
def getNearshop(cordnow):
    #здесь подключаем базу данных (ShopAdress) к сайту
    mindist = 100
    mindistshopid = ""
    x1, y1 = map(float, cordnow.split())
    for k in ShopAdress.select():
        x2, y2 = map(float, k.shopadress.split())
        if ((x1 - x2)**2 + (y1 - y2)**2)**0.5 < mindist:
            mindistshopid = mindistshopid + "," + str(k.id)
            # в mindistshopid получиться строка из ShopAdress.id близлежащих магазинов
    mindistshopid = mindistshopid[1:]
    if mindistshopid == "":
        return("Ближайших магазинов не обнаружено")
    else:
        return(mindistshopid)
'''




if __name__ == '__main__':
    app.run(port=8080, debug = True, host = '0.0.0.0') # для телефона нужно вставлять host = '0.0.0.0'