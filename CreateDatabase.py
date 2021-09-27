from peewee import *

db = SqliteDatabase('PlaceAndProduct.sq')

class Product(Model):
    barcode = IntegerField()
    productname = CharField()
    shopname = CharField()
    shopid = IntegerField()
    price = FloatField()


    class Meta:
        database = db


class ShopAdress(Model):
    shopadress = CharField()
    shopid = IntegerField()
    shopname = CharField()

    class Meta:
        database = db

Product.create_table()
ShopAdress.create_table()