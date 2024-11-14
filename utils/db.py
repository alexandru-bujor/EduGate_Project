from pymongo import MongoClient

def get_db_connection():
    client = MongoClient(
        "mongodb+srv://sandumagla:QHpB0YxzKyhPLmuw@test.zpzjq.mongodb.net/School_Acces?retryWrites=true&w=majority"
    )
    return client['School_Acces']
