# =====================================================================
# controller_jogador.py
# Inserir, atualizar e remover JOGADORES, conversando com o usuário
# e executando os comandos do MongoDB na coleção "jogadores".
# =====================================================================
import re
from model.jogadores import Jogador
from conexion.mongo_queries import MongoQueries
from utils.entrada import ler_inteiro, ler_texto, ler_data, perguntar_sim_nao


class Controller_Jogador:

    def __init__(self):
        pass

    # -----------------------------------------------------------------
    # Funções de apoio
    # -----------------------------------------------------------------
    def buscar_jogador(self, mongo, id_jogador):
        """Busca o jogador pelo ID. Devolve um objeto Jogador, ou None se não existir."""
        documento = mongo.db["jogadores"].find_one({"id_jogador": id_jogador})
        if documento is None:
            return None
        return Jogador(documento["id_jogador"], documento["nickname"],
                       documento["email"], documento["data_cadastro"])

    def verifica_existencia_jogador(self, mongo, id_jogador):
        """Devolve True se existe jogador com esse ID."""
        return mongo.db["jogadores"].count_documents({"id_jogador": id_jogador}) > 0

    def nickname_ja_usado(self, mongo, nickname, ignorar_id=None):
        """Devolve True se outro jogador já usa esse nickname (sem diferenciar maiúsculas)."""
        filtro = {"nickname": {"$regex": f"^{re.escape(nickname)}$", "$options": "i"}}
        if ignorar_id is not None:
            filtro["id_jogador"] = {"$ne": ignorar_id}
        return mongo.db["jogadores"].count_documents(filtro) > 0

    def ler_email(self):
        """Lê um e-mail e confere se tem '@'."""
        while True:
            email = ler_texto("E-mail: ", 100)
            if "@" in email:
                return email
            print("  E-mail inválido: precisa ter '@'.")

    def listar_jogadores(self, mongo):
        """Mostra os jogadores na tela e devolve quantos existem."""
        documentos = mongo.db["jogadores"].find({}, {"_id": 0, "id_jogador": 1, "nickname": 1}).sort("id_jogador", 1)
        return mongo.imprimir(documentos, ["id_jogador", "nickname"])

    # -----------------------------------------------------------------
    # INSERIR
    # -----------------------------------------------------------------
    def inserir_jogador(self):
        mongo = MongoQueries()
        mongo.conectar()
        while True:
            print("\n=== NOVO JOGADOR ===")
            nickname = ler_texto("Nickname: ", 30)

            if self.nickname_ja_usado(mongo, nickname):
                print(f"\nO nickname '{nickname}' já está em uso.")
            else:
                email = self.ler_email()
                data_cadastro = ler_data("Data de cadastro")
                novo_id = mongo.proximo_id("jogadores", "id_jogador")
                mongo.db["jogadores"].insert_one({
                    "id_jogador": novo_id,
                    "nickname": nickname,
                    "email": email,
                    "data_cadastro": data_cadastro,
                })
                novo_jogador = self.buscar_jogador(mongo, novo_id)
                print("\nJogador cadastrado com sucesso!")
                print(novo_jogador.to_string())

            if not perguntar_sim_nao("\nDeseja inserir mais algum jogador?"):
                break
        mongo.fechar()

    # -----------------------------------------------------------------
    # ATUALIZAR
    # -----------------------------------------------------------------
    def atualizar_jogador(self):
        mongo = MongoQueries()
        mongo.conectar()
        while True:
            print("\n=== ATUALIZAR JOGADOR ===\n")
            if self.listar_jogadores(mongo) == 0:
                print("\nNão há jogadores cadastrados.")
                break

            id_jogador = ler_inteiro("\nID do jogador que deseja atualizar: ")
            jogador = self.buscar_jogador(mongo, id_jogador)

            if jogador is None:
                print(f"\nNão existe jogador com o ID {id_jogador}.")
            else:
                print("\nDados atuais: " + jogador.to_string())
                print("Informe os novos dados:")
                novo_nickname = ler_texto("Nickname: ", 30)
                if self.nickname_ja_usado(mongo, novo_nickname, id_jogador):
                    print(f"\nO nickname '{novo_nickname}' já está em uso por outro jogador.")
                else:
                    novo_email = self.ler_email()
                    nova_data = ler_data("Data de cadastro")
                    mongo.db["jogadores"].update_one(
                        {"id_jogador": id_jogador},
                        {"$set": {"nickname": novo_nickname, "email": novo_email,
                                  "data_cadastro": nova_data}})
                    jogador_atualizado = self.buscar_jogador(mongo, id_jogador)
                    print("\nJogador atualizado com sucesso!")
                    print(jogador_atualizado.to_string())

            if not perguntar_sim_nao("\nDeseja atualizar mais algum jogador?"):
                break
        mongo.fechar()

    # -----------------------------------------------------------------
    # REMOVER
    # -----------------------------------------------------------------
    def excluir_jogador(self):
        mongo = MongoQueries()
        mongo.conectar()
        while True:
            print("\n=== REMOVER JOGADOR ===\n")
            if self.listar_jogadores(mongo) == 0:
                print("\nNão há jogadores cadastrados.")
                break

            id_jogador = ler_inteiro("\nID do jogador que deseja remover: ")
            jogador = self.buscar_jogador(mongo, id_jogador)

            if jogador is None:
                print(f"\nNão existe jogador com o ID {id_jogador}.")
            else:
                print("\n" + jogador.to_string())
                if not perguntar_sim_nao("Confirma a remoção deste jogador?"):
                    print("\nRemoção cancelada.")
                    break   # o edital pede: se "Não", volta ao menu principal

                # O jogador é referenciado em documentos da coleção "personagens"?
                qtd = mongo.db["personagens"].count_documents({"id_jogador": id_jogador})

                if qtd > 0:
                    print(f"\nAtenção: o jogador '{jogador.get_nickname()}' tem {qtd} personagem(ns).")
                    if perguntar_sim_nao("Deseja remover esses personagens junto com o jogador?"):
                        # Primeiro os "filhos" (personagens), depois o jogador
                        mongo.db["personagens"].delete_many({"id_jogador": id_jogador})
                        mongo.db["jogadores"].delete_one({"id_jogador": id_jogador})
                        print(f"\nJogador e {qtd} personagem(ns) removidos com sucesso!")
                    else:
                        print("\nO jogador não foi removido, porque ainda tem personagens.")
                else:
                    mongo.db["jogadores"].delete_one({"id_jogador": id_jogador})
                    print("\nJogador removido com sucesso!")

            if not perguntar_sim_nao("\nDeseja remover mais algum jogador?"):
                break
        mongo.fechar()