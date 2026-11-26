# =====================================================================
# mongo_queries.py
# Classe que faz a "ponte" entre o Python e o banco MongoDB.
# Os controllers, os relatórios e a splash screen usam esta classe.
# =====================================================================
import pymongo
from urllib.parse import quote_plus

# ---------------------------------------------------------------------
# DADOS DA CONEXÃO (os mesmos do docker-compose.yml da VM)
# ---------------------------------------------------------------------
USUARIO = "mongoadmin"
SENHA = "secret"
HOST = "localhost"
PORTA = 27017
BANCO = "labdatabase"


class MongoQueries:

    def __init__(self):
        # A conexão só é aberta quando o método conectar() é chamado
        self.cliente = None
        self.db = None

    def conectar(self):
        """Abre a conexão com o MongoDB, se ainda não estiver aberta."""
        if self.cliente is None:
            # quote_plus protege a senha caso ela tenha caracteres especiais
            endereco = f"mongodb://{USUARIO}:{quote_plus(SENHA)}@{HOST}:{PORTA}/"
            self.cliente = pymongo.MongoClient(endereco, serverSelectionTimeoutMS=5000)
            # db é o banco: é por ele que acessamos as coleções, ex.: self.db["guildas"]
            self.db = self.cliente[BANCO]

    def proximo_id(self, colecao, campo_id):
        """O MongoDB não tem sequence: busca o maior ID da coleção e soma 1.
        Ex.: proximo_id("guildas", "id_guilda") -> 5 se o maior ID for 4."""
        self.conectar()
        maior = self.db[colecao].find_one(sort=[(campo_id, pymongo.DESCENDING)])
        if maior is None:
            return 1
        return int(maior[campo_id]) + 1

    def imprimir(self, documentos, colunas):
        """Mostra uma lista de documentos como tabela na tela.
        'colunas' diz quais campos mostrar e em que ordem.
        Devolve quantos documentos foram mostrados."""
        documentos = list(documentos)
        if len(documentos) == 0:
            print("  (nenhum documento encontrado)")
            return 0

        # Calcula a largura de cada coluna (o maior texto dela)
        larguras = [len(coluna) for coluna in colunas]
        for documento in documentos:
            for i in range(len(colunas)):
                larguras[i] = max(larguras[i], len(self.texto(documento.get(colunas[i]))))

        # Cabeçalho, linha separadora e os documentos
        print("  " + " | ".join(colunas[i].upper().ljust(larguras[i]) for i in range(len(colunas))))
        print("  " + "-+-".join("-" * largura for largura in larguras))
        for documento in documentos:
            print("  " + " | ".join(self.texto(documento.get(colunas[i])).ljust(larguras[i])
                                    for i in range(len(colunas))))
        return len(documentos)

    def texto(self, valor):
        """Transforma um valor em texto (None vira vazio).
        Números com casas decimais (como médias) aparecem com 1 casa."""
        if valor is None:
            return ""
        if isinstance(valor, float):
            return f"{valor:.1f}"
        return str(valor)

    def fechar(self):
        """Fecha a conexão com o MongoDB."""
        if self.cliente is not None:
            self.cliente.close()
            self.cliente = None
            self.db = None
