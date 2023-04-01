from unicodedata import name
import pymongo

def get_mongo():
    return pymongo.MongoClient('mongo', 27017, directConnection=True)

def get_all(mongo):
    res = mongo.find({})

    response = []
    for inst in res:
        del inst["_id"]
        response.append(inst)
    return response