from pymongo import MongoClient
from config import MONGO

client = MongoClient(MONGO.URI)
db = client[MONGO.NAME]
