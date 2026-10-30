# =====================================================================
# controller_personagem.py
# Inserir, atualizar e remover PERSONAGENS na coleção "personagens".
# Cada personagem guarda o id_jogador e o id_guilda: como o MongoDB
# não tem chave estrangeira, o código confere se eles existem.
# =====================================================================
from model.personagens import Personagem
from model.jogadores import Jogador
from model.guildas import Guilda
from conexion.mongo_queries import MongoQueries
from utils.entrada import ler_inteiro, ler_texto, perguntar_sim_nao

# As únicas classes aceitas
CLASSES = ["Guerreiro", "Mago", "Arqueiro", "Sacerdote"]


class Controller_Personagem:

    def __init__(self):
        pass

    # -----------------------------------------------------------------
    # Funções de apoio
    # -----------------------------------------------------------------
    def buscar_personagem(self, mongo, id_personagem):
        """Busca o personagem pelo ID e também o seu jogador e a sua guilda.
        Devolve um objeto Personagem, ou None se não existir."""
        doc_personagem = mongo.db["personagens"].find_one({"id_personagem": id_personagem})
        if doc_personagem is None:
            return None
        # Busca os documentos "relacionados" usando os IDs guardados no personagem
        doc_jogador = mongo.db["jogadores"].find_one({"id_jogador": doc_personagem["id_jogador"]})
        doc_guilda = mongo.db["guildas"].find_one({"id_guilda": doc_personagem["id_guilda"]})
        jogador = Jogador(doc_jogador["id_jogador"], doc_jogador["nickname"],
                          doc_jogador["email"], doc_jogador["data_cadastro"])
        guilda = Guilda(doc_guilda["id_guilda"], doc_guilda["nome"], doc_guilda["data_criacao"])
        return Personagem(doc_personagem["id_personagem"], doc_personagem["nome"],
                          doc_personagem["classe"], doc_personagem["nivel"], jogador, guilda)

    def verifica_existencia_personagem(self, mongo, id_personagem):
        """Devolve True se existe personagem com esse ID."""
        return mongo.db["personagens"].count_documents({"id_personagem": id_personagem}) > 0

    def listar_personagens(self, mongo):
        """Mostra os personagens na tela e devolve quantos existem."""
        documentos = mongo.db["personagens"].find(
            {}, {"_id": 0, "id_personagem": 1, "nome": 1, "classe": 1, "nivel": 1}).sort("id_personagem", 1)
        return mongo.imprimir(documentos, ["id_personagem", "nome", "classe", "nivel"])

    def escolher_classe(self):
        """Mostra as classes numeradas e devolve a escolhida."""
        print("Classes disponíveis:")
        for i in range(len(CLASSES)):
            print(f"  {i + 1} - {CLASSES[i]}")
        opcao = ler_inteiro(f"Escolha a classe [1-{len(CLASSES)}]: ", 1, len(CLASSES))
        return CLASSES[opcao - 1]

    def escolher_jogador(self, mongo):
        """Mostra os jogadores e devolve o ID de um que exista."""
        print("\nJogadores cadastrados:")
        documentos = mongo.db["jogadores"].find({}, {"_id": 0, "id_jogador": 1, "nickname": 1}).sort("id_jogador", 1)
        mongo.imprimir(documentos, ["id_jogador", "nickname"])
        while True:
            id_jogador = ler_inteiro("ID do jogador dono do personagem: ")
            if mongo.db["jogadores"].count_documents({"id_jogador": id_jogador}) > 0:
                return id_jogador
            print(f"  Não existe jogador com o ID {id_jogador}.")

    def escolher_guilda(self, mongo):
        """Mostra as guildas e devolve o ID de uma que exista."""
        print("\nGuildas cadastradas:")
        documentos = mongo.db["guildas"].find({}, {"_id": 0, "id_guilda": 1, "nome": 1}).sort("id_guilda", 1)
        mongo.imprimir(documentos, ["id_guilda", "nome"])
        while True:
            id_guilda = ler_inteiro("ID da guilda do personagem: ")
            if mongo.db["guildas"].count_documents({"id_guilda": id_guilda}) > 0:
                return id_guilda
            print(f"  Não existe guilda com o ID {id_guilda}.")

    def existem_jogadores_e_guildas(self, mongo):
        """Personagem precisa de jogador e guilda: confere se existem os dois."""
        qtd_jogadores = mongo.db["jogadores"].count_documents({})
        qtd_guildas = mongo.db["guildas"].count_documents({})
        if qtd_jogadores == 0 or qtd_guildas == 0:
            print("\nCadastre pelo menos um jogador e uma guilda antes de criar personagens.")
            return False
        return True

    # -----------------------------------------------------------------
    # INSERIR
    # -----------------------------------------------------------------
    def inserir_personagem(self):
        mongo = MongoQueries()
        mongo.conectar()
        while True:
            print("\n=== NOVO PERSONAGEM ===")
            if not self.existem_jogadores_e_guildas(mongo):
                break

            nome = ler_texto("Nome do personagem: ", 30)
            classe = self.escolher_classe()
            nivel = ler_inteiro("Nível [1-100]: ", 1, 100)
            id_jogador = self.escolher_jogador(mongo)
            id_guilda = self.escolher_guilda(mongo)

            novo_id = mongo.proximo_id("personagens", "id_personagem")
            mongo.db["personagens"].insert_one({
                "id_personagem": novo_id,
                "nome": nome,
                "classe": classe,
                "nivel": nivel,
                "id_jogador": id_jogador,
                "id_guilda": id_guilda,
            })
            novo_personagem = self.buscar_personagem(mongo, novo_id)
            print("\nPersonagem cadastrado com sucesso!")
            print(novo_personagem.to_string())

            if not perguntar_sim_nao("\nDeseja inserir mais algum personagem?"):
                break
        mongo.fechar()

    # -----------------------------------------------------------------
    # ATUALIZAR
    # -----------------------------------------------------------------
    def atualizar_personagem(self):
        mongo = MongoQueries()
        mongo.conectar()
        while True:
            print("\n=== ATUALIZAR PERSONAGEM ===\n")
            if self.listar_personagens(mongo) == 0:
                print("\nNão há personagens cadastrados.")
                break

            id_personagem = ler_inteiro("\nID do personagem que deseja atualizar: ")
            personagem = self.buscar_personagem(mongo, id_personagem)

            if personagem is None:
                print(f"\nNão existe personagem com o ID {id_personagem}.")
            else:
                print("\nDados atuais: " + personagem.to_string())
                print("Informe os novos dados:")
                novo_nome = ler_texto("Nome do personagem: ", 30)
                nova_classe = self.escolher_classe()
                novo_nivel = ler_inteiro("Nível [1-100]: ", 1, 100)
                novo_jogador = self.escolher_jogador(mongo)
                nova_guilda = self.escolher_guilda(mongo)
                mongo.db["personagens"].update_one(
                    {"id_personagem": id_personagem},
                    {"$set": {"nome": novo_nome, "classe": nova_classe, "nivel": novo_nivel,
                              "id_jogador": novo_jogador, "id_guilda": nova_guilda}})
                personagem_atualizado = self.buscar_personagem(mongo, id_personagem)
                print("\nPersonagem atualizado com sucesso!")
                print(personagem_atualizado.to_string())

            if not perguntar_sim_nao("\nDeseja atualizar mais algum personagem?"):
                break
        mongo.fechar()

    # -----------------------------------------------------------------
    # REMOVER
    # -----------------------------------------------------------------
    def excluir_personagem(self):
        mongo = MongoQueries()
        mongo.conectar()
        while True:
            print("\n=== REMOVER PERSONAGEM ===\n")
            if self.listar_personagens(mongo) == 0:
                print("\nNão há personagens cadastrados.")
                break

            id_personagem = ler_inteiro("\nID do personagem que deseja remover: ")
            personagem = self.buscar_personagem(mongo, id_personagem)

            if personagem is None:
                print(f"\nNão existe personagem com o ID {id_personagem}.")
            else:
                print("\n" + personagem.to_string())
                if not perguntar_sim_nao("Confirma a remoção deste personagem?"):
                    print("\nRemoção cancelada.")
                    break   # o edital pede: se "Não", volta ao menu principal
                # Nenhuma coleção referencia personagens, então pode apagar direto
                mongo.db["personagens"].delete_one({"id_personagem": id_personagem})
                print("\nPersonagem removido com sucesso!")

            if not perguntar_sim_nao("\nDeseja remover mais algum personagem?"):
                break
        mongo.fechar()
