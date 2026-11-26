# =====================================================================
# config.py
# Textos dos menus, dados da splash screen e funções de tela.
# =====================================================================
import os
NOME_SISTEMA = "SISTEMA DE GERENCIAMENTO DE MMORPG"
INTEGRANTES = [
    "PEDRO MARQUES MATARANGAS",
    "DAVI DE BRITO TEIXEIRA",
    "SAMUEL FLORIANO OLIVEIRA DE SIQUEIRA",
    "ARTUR CARMO DOS SANTOS",
    "GABRIEL LEAL HOFFOMAN",
]

DISCIPLINA = "BANCO DE DADOS"
SEMESTRE = "2026/2"
PROFESSOR = "HOWARD ROATTI"

# Coleções que aparecem na contagem da splash screen
COLECOES = ["guildas", "jogadores", "personagens"]

MENU_PRINCIPAL = """
=========== MENU PRINCIPAL ===========
  1 - Relatórios
  2 - Inserir documentos
  3 - Atualizar documentos
  4 - Remover documentos
  5 - Sair
======================================"""

MENU_RELATORIOS = """
============== RELATÓRIOS ==============
  1 - Personagens por classe
  2 - Personagens por guilda
  3 - Lista completa de personagens
  0 - Voltar ao menu principal
========================================"""

MENU_ENTIDADES = """
  1 - Guildas
  2 - Jogadores
  3 - Personagens
  0 - Voltar ao menu principal"""

def limpar_tela():
    """Limpa o terminal."""
    os.system("clear")

def pausar():
    """Espera o usuário apertar Enter."""
    input("\nPressione Enter para continuar...")