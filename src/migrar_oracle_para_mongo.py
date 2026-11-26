# =====================================================================
# migrar_oracle_para_mongo.py
# Script pedido no item 4 do edital:
#   1. conecta no Oracle
#   2. consulta cada tabela do projeto da C2
#   3. conecta no MongoDB
#   4. cria uma coleção com o mesmo nome de cada tabela
#   5. insere os registros das tabelas como documentos nas coleções
# ATENÇÃO: as tabelas precisam existir no Oracle (python3 criar_tabelas.py)
# Para executar (de dentro da pasta src):  python3 migrar_oracle_para_mongo.py
# =====================================================================
from conexion.oracle_queries import OracleQueries
from conexion.mongo_queries import MongoQueries

# Para cada tabela: o SELECT que busca os dados no Oracle e os nomes
# dos campos que cada documento terá no MongoDB (na mesma ordem).
# As datas viram texto 'DD/MM/YYYY', o mesmo formato usado no programa.
TABELAS = {
    "guildas": {
        "sql": "select id_guilda, nome, to_char(data_criacao, 'DD/MM/YYYY') "
               "from guildas order by id_guilda",
        "campos": ["id_guilda", "nome", "data_criacao"],
    },
    "jogadores": {
        "sql": "select id_jogador, nickname, email, to_char(data_cadastro, 'DD/MM/YYYY') "
               "from jogadores order by id_jogador",
        "campos": ["id_jogador", "nickname", "email", "data_cadastro"],
    },
    "personagens": {
        "sql": "select id_personagem, nome, classe, nivel, id_jogador, id_guilda "
               "from personagens order by id_personagem",
        "campos": ["id_personagem", "nome", "classe", "nivel", "id_jogador", "id_guilda"],
    },
}

# Campos numéricos: o Oracle pode devolvê-los como número decimal,
# então convertemos para inteiro antes de gravar no MongoDB
CAMPOS_INTEIROS = ["id_guilda", "id_jogador", "id_personagem", "nivel"]


def linha_para_documento(linha, campos):
    """Transforma uma linha do Oracle (tupla) em um documento (dicionário).
    Ex.: (1, 'Lobos de Prata', '15/01/2026') ->
         {'id_guilda': 1, 'nome': 'Lobos de Prata', 'data_criacao': '15/01/2026'}"""
    documento = {}
    for i in range(len(campos)):
        valor = linha[i]
        if campos[i] in CAMPOS_INTEIROS:
            valor = int(valor)
        documento[campos[i]] = valor
    return documento


def main():
    oracle = OracleQueries()
    mongo = MongoQueries()
    mongo.conectar()

    for nome_tabela, info in TABELAS.items():
        # 1 e 2: consulta a tabela no Oracle
        linhas = oracle.consultar(info["sql"])
        documentos = [linha_para_documento(linha, info["campos"]) for linha in linhas]

        # 3 e 4: apaga a coleção (se já existir) e cria de novo, vazia
        if nome_tabela in mongo.db.list_collection_names():
            mongo.db.drop_collection(nome_tabela)
        mongo.db.create_collection(nome_tabela)

        # 5: insere os documentos
        if len(documentos) > 0:
            mongo.db[nome_tabela].insert_many(documentos)
        print(f"Colecao '{nome_tabela}': {len(documentos)} documento(s) inserido(s).")

    oracle.fechar()
    mongo.fechar()
    print("\nMigracao do Oracle para o MongoDB concluida!")


if __name__ == "__main__":
    main()
