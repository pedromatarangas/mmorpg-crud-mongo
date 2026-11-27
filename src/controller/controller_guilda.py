# =====================================================================
# controller_guilda.py
# Inserir, atualizar e remover GUILDAS, conversando com o usuário
# e executando os comandos do MongoDB na coleção "guildas".
# =====================================================================
import re
from model.guildas import Guilda
from conexion.mongo_queries import MongoQueries
from utils.entrada import ler_inteiro, ler_texto, ler_data, perguntar_sim_nao


class Controller_Guilda:

    def __init__(self):
        pass

    # -----------------------------------------------------------------
    # Funções de apoio (usadas pelas funções principais lá embaixo)
    # -----------------------------------------------------------------
    def buscar_guilda(self, mongo, id_guilda):
        """Busca a guilda pelo ID. Devolve um objeto Guilda, ou None se não existir."""
        documento = mongo.db["guildas"].find_one({"id_guilda": id_guilda})
        if documento is None:
            return None
        return Guilda(documento["id_guilda"], documento["nome"], documento["data_criacao"])

    def verifica_existencia_guilda(self, mongo, id_guilda):
        """Devolve True se existe guilda com esse ID."""
        return mongo.db["guildas"].count_documents({"id_guilda": id_guilda}) > 0

    def nome_ja_usado(self, mongo, nome, ignorar_id=None):
        """Devolve True se outra guilda já usa esse nome (sem diferenciar maiúsculas)."""
        # $regex com ^ e $ = nome exatamente igual; "i" = ignora maiúsculas/minúsculas
        filtro = {"nome": {"$regex": f"^{re.escape(nome)}$", "$options": "i"}}
        if ignorar_id is not None:
            # $ne = "not equal" (diferente de): ignora a própria guilda na atualização
            filtro["id_guilda"] = {"$ne": ignorar_id}
        return mongo.db["guildas"].count_documents(filtro) > 0

    def listar_guildas(self, mongo):
        """Mostra as guildas na tela e devolve quantas existem."""
        documentos = mongo.db["guildas"].find({}, {"_id": 0, "id_guilda": 1, "nome": 1}).sort("id_guilda", 1)
        return mongo.imprimir(documentos, ["id_guilda", "nome"])

    # -----------------------------------------------------------------
    # INSERIR
    # -----------------------------------------------------------------
    def inserir_guilda(self):
        mongo = MongoQueries()
        mongo.conectar()
        while True:
            print("\n=== NOVA GUILDA ===")
            nome = ler_texto("Nome da guilda: ", 50)

            if self.nome_ja_usado(mongo, nome):
                print(f"\nJá existe uma guilda chamada '{nome}'.")
            else:
                data_criacao = ler_data("Data de criação")
                novo_id = mongo.proximo_id("guildas", "id_guilda")
                mongo.db["guildas"].insert_one({
                    "id_guilda": novo_id,
                    "nome": nome,
                    "data_criacao": data_criacao,
                })
                nova_guilda = self.buscar_guilda(mongo, novo_id)
                print("\nGuilda cadastrada com sucesso!")
                print(nova_guilda.to_string())

            if not perguntar_sim_nao("\nDeseja inserir mais alguma guilda?"):
                break
        mongo.fechar()

    # -----------------------------------------------------------------
    # ATUALIZAR
    # -----------------------------------------------------------------
    def atualizar_guilda(self):
        mongo = MongoQueries()
        mongo.conectar()
        while True:
            print("\n=== ATUALIZAR GUILDA ===\n")
            if self.listar_guildas(mongo) == 0:
                print("\nNão há guildas cadastradas.")
                break

            id_guilda = ler_inteiro("\nID da guilda que deseja atualizar: ")
            guilda = self.buscar_guilda(mongo, id_guilda)

            if guilda is None:
                print(f"\nNão existe guilda com o ID {id_guilda}.")
            else:
                print("\nDados atuais: " + guilda.to_string())
                print("Informe os novos dados:")
                novo_nome = ler_texto("Nome da guilda: ", 50)
                if self.nome_ja_usado(mongo, novo_nome, id_guilda):
                    print(f"\nJá existe outra guilda chamada '{novo_nome}'.")
                else:
                    nova_data = ler_data("Data de criação")
                    # $set troca só os campos informados, mantendo o resto do documento
                    mongo.db["guildas"].update_one(
                        {"id_guilda": id_guilda},
                        {"$set": {"nome": novo_nome, "data_criacao": nova_data}})
                    guilda_atualizada = self.buscar_guilda(mongo, id_guilda)
                    print("\nGuilda atualizada com sucesso!")
                    print(guilda_atualizada.to_string())

            if not perguntar_sim_nao("\nDeseja atualizar mais alguma guilda?"):
                break
        mongo.fechar()

    # -----------------------------------------------------------------
    # REMOVER
    # -----------------------------------------------------------------
    def excluir_guilda(self):
        mongo = MongoQueries()
        mongo.conectar()
        while True:
            print("\n=== REMOVER GUILDA ===\n")
            if self.listar_guildas(mongo) == 0:
                print("\nNão há guildas cadastradas.")
                break

            id_guilda = ler_inteiro("\nID da guilda que deseja remover: ")
            guilda = self.buscar_guilda(mongo, id_guilda)

            if guilda is None:
                print(f"\nNão existe guilda com o ID {id_guilda}.")
            else:
                print("\n" + guilda.to_string())
                if not perguntar_sim_nao("Confirma a remoção desta guilda?"):
                    print("\nRemoção cancelada.")
                    break   # o edital pede: se "Não", volta ao menu principal

                # A guilda é referenciada em documentos da coleção "personagens"?
                # O MongoDB não tem chave estrangeira: quem confere é o nosso código.
                qtd = mongo.db["personagens"].count_documents({"id_guilda": id_guilda})

                if qtd > 0:
                    # Tem personagens: a guilda NÃO pode ser excluída
                    print(f"\nA guilda '{guilda.get_nome()}' não pode ser excluída, "
                          f"porque ainda tem {qtd} personagem(ns):\n")
                    membros = mongo.db["personagens"].find(
                        {"id_guilda": id_guilda},
                        {"_id": 0, "id_personagem": 1, "nome": 1}).sort("id_personagem", 1)
                    mongo.imprimir(membros, ["id_personagem", "nome"])
                    print("\nTransfira esses personagens para outra guilda "
                          "(menu Atualizar > Personagens) e tente novamente.")
                else:
                    mongo.db["guildas"].delete_one({"id_guilda": id_guilda})
                    print("\nGuilda removida com sucesso!")

            if not perguntar_sim_nao("\nDeseja remover mais alguma guilda?"):
                break
        mongo.fechar()
