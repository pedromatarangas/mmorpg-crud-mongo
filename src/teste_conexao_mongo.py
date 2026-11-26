# Testa se o Python consegue conversar com o MongoDB.
# Rode de dentro da pasta src:  python3 teste_conexao_mongo.py
from conexion.mongo_queries import MongoQueries

mongo = MongoQueries()
mongo.conectar()
print("Conexao com o MongoDB funcionando!")
print("Colecoes existentes:", mongo.db.list_collection_names())
mongo.fechar()