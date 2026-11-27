from conexion.mongo_queries import MongoQueries
from utils import config


class Relatorio:

    def __init__(self):
        pass

    def mostrar(self, titulo, colecao, pipeline, colunas):
        """Executa o pipeline na coleção, mostra o resultado e espera o Enter."""
        print(f"\n=== {titulo} ===\n")
        mongo = MongoQueries()
        mongo.conectar()
        resultado = mongo.db[colecao].aggregate(pipeline)
        mongo.imprimir(resultado, colunas)
        mongo.fechar()
        config.pausar()

   
    def get_relatorio_personagens_por_classe(self):
        pipeline = [
            {"$group": {
                "_id": "$classe",
                "qtd_personagens": {"$sum": 1},       
                "nivel_medio": {"$avg": "$nivel"},     
                "maior_nivel": {"$max": "$nivel"},     
            }},
            
            {"$project": {
                "_id": 0,
                "classe": "$_id",
                "qtd_personagens": 1,
                "nivel_medio": 1,
                "maior_nivel": 1,
            }},
            
            {"$sort": {"classe": 1}},
        ]
        self.mostrar("PERSONAGENS POR CLASSE", "personagens", pipeline,
                     ["classe", "qtd_personagens", "nivel_medio", "maior_nivel"])

    
    def get_relatorio_personagens_por_guilda(self):
        pipeline = [
            
            {"$lookup": {
                "from": "personagens",
                "localField": "id_guilda",
                "foreignField": "id_guilda",
                "as": "membros",            
            }},
            {"$project": {
                "_id": 0,
                "guilda": "$nome",
                "qtd_membros": {"$size": "$membros"},
               
                "nivel_medio": {"$ifNull": [{"$avg": "$membros.nivel"}, 0]},
            }},
            {"$sort": {"qtd_membros": -1, "guilda": 1}},  
        ]
        self.mostrar("PERSONAGENS POR GUILDA", "guildas", pipeline,
                     ["guilda", "qtd_membros", "nivel_medio"])

   
    def get_relatorio_personagens_completo(self):
        pipeline = [
            {"$lookup": {"from": "jogadores", "localField": "id_jogador",
                         "foreignField": "id_jogador", "as": "jogador"}},
            
            {"$unwind": "$jogador"},
            {"$lookup": {"from": "guildas", "localField": "id_guilda",
                         "foreignField": "id_guilda", "as": "guilda"}},
            {"$unwind": "$guilda"},
            {"$project": {
                "_id": 0,
                "id": "$id_personagem",
                "personagem": "$nome",
                "classe": 1,
                "nivel": 1,
                "jogador": "$jogador.nickname",
                "guilda": "$guilda.nome",
            }},
            {"$sort": {"guilda": 1, "nivel": -1}},
        ]
        self.mostrar("LISTA COMPLETA DE PERSONAGENS", "personagens", pipeline,
                      ["id", "personagem", "classe", "nivel", "jogador", "guilda"])
                     ["id", "personagem", "classe", "nivel", "jogador", "guilda"])
