"""Regras de negócio do Analisador de Gastos Pessoais.

História 1 (leitura do extrato) foi refatorada na Sprint 4 aplicando:

* Template Method: ``LeitorExtrato.ler`` define o passo a passo fixo
  (abrir -> validar colunas -> converter cada linha) e as subclasses só
  dizem como extrair os registros do formato delas.
* Factory Method: ``criar_leitor`` escolhe o leitor certo pela extensão do
  arquivo, consultando o registro ``LEITORES``. Um novo formato (ex.: OFX)
  entra criando uma subclasse e registrando-a, sem mexer no resto.
* Facade: ``ler_csv`` e ``ler_extrato`` escondem as classes de quem só quer
  a lista de transações (CLI e testes).
"""
import csv
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path

COLUNAS = ("data", "descricao", "categoria", "valor")
FORMATO_DATA = "%d/%m/%Y"


class ErroExtrato(ValueError):
    """Problema no conteúdo do extrato.

    Herda de ValueError para manter o contrato da arquitetura: as regras
    lançam ValueError e só a CLI fala com o usuário.
    """


# ---------------------------------------------------------------------------
# Conversões de campo
# ---------------------------------------------------------------------------

def converter_valor(texto, numero_linha):
    """Converte '12.50', '12,50', '1.200,00' ou 'R$ 12,50' para float."""
    original = texto
    limpo = texto.replace("R$", "").replace(" ", "").strip()
    if "," in limpo:
        # formato brasileiro: ponto é separador de milhar, vírgula é decimal
        limpo = limpo.replace(".", "").replace(",", ".")
    try:
        return float(limpo)
    except ValueError:
        raise ErroExtrato(
            f"Linha {numero_linha}: valor inválido '{original}'"
        ) from None


def converter_data(texto, numero_linha):
    """Converte 'DD/MM/AAAA' para date, informando a linha em caso de erro."""
    try:
        return datetime.strptime(texto.strip(), FORMATO_DATA).date()
    except ValueError:
        raise ErroExtrato(
            f"Linha {numero_linha}: data inválida '{texto}' (use DD/MM/AAAA)"
        ) from None


def criar_transacao(registro, numero_linha):
    """Transforma um registro bruto (dict de textos) em uma transação."""
    faltando = [c for c in COLUNAS if registro.get(c) is None]
    if faltando:
        raise ErroExtrato(
            f"Linha {numero_linha}: faltam campos ({', '.join(faltando)})"
        )

    return {
        "data": converter_data(registro["data"], numero_linha),
        "descricao": registro["descricao"].strip(),
        "categoria": registro["categoria"].strip(),
        "valor": converter_valor(registro["valor"], numero_linha),
    }


# ---------------------------------------------------------------------------
# Leitores (Template Method)
# ---------------------------------------------------------------------------

class LeitorExtrato(ABC):
    """Esqueleto da leitura de um extrato, igual para qualquer formato."""

    encoding = "utf-8-sig"  # aceita arquivos salvos pelo Excel (com BOM)

    def ler(self, caminho):
        """Método template: a ordem dos passos é fixa."""
        with open(caminho, encoding=self.encoding, newline="") as arquivo:
            cabecalho, registros = self.extrair_registros(arquivo)
            self.validar_colunas(cabecalho)
            return [
                criar_transacao(registro, numero_linha)
                for numero_linha, registro in registros
            ]

    @abstractmethod
    def extrair_registros(self, arquivo):
        """Devolve (cabecalho, iteravel de (numero_linha, dict))."""

    def validar_colunas(self, cabecalho):
        if not cabecalho:
            raise ErroExtrato("O arquivo está vazio ou sem cabeçalho")
        faltando = [c for c in COLUNAS if c not in cabecalho]
        if len(faltando) == 1:
            raise ErroExtrato(f"Está faltando a coluna '{faltando[0]}' no arquivo")
        if faltando:
            nomes = ", ".join(f"'{c}'" for c in faltando)
            raise ErroExtrato(f"Estão faltando as colunas {nomes} no arquivo")


class LeitorCSV(LeitorExtrato):
    """Lê CSV separado por vírgula ou por ponto e vírgula."""

    def extrair_registros(self, arquivo):
        primeira_linha = arquivo.readline()
        arquivo.seek(0)
        separador = ";" if primeira_linha.count(";") > primeira_linha.count(",") else ","

        leitor = csv.DictReader(arquivo, delimiter=separador)
        if leitor.fieldnames:
            # "Data ", "DESCRICAO" etc. viram "data", "descricao"
            leitor.fieldnames = [nome.strip().lower() for nome in leitor.fieldnames]
        cabecalho = leitor.fieldnames or []

        def registros():
            for registro in leitor:
                # line_num é a linha real do arquivo, mesmo com linhas em branco
                yield leitor.line_num, registro

        return cabecalho, registros()


# ---------------------------------------------------------------------------
# Fábrica (Factory Method) e fachadas
# ---------------------------------------------------------------------------

LEITORES = {
    ".csv": LeitorCSV,
}


def criar_leitor(caminho):
    """Escolhe o leitor pela extensão do arquivo."""
    extensao = Path(caminho).suffix.lower()
    try:
        return LEITORES[extensao]()
    except KeyError:
        aceitos = ", ".join(sorted(LEITORES))
        raise ErroExtrato(
            f"Formato '{extensao or 'sem extensão'}' não suportado (aceitos: {aceitos})"
        ) from None


def ler_extrato(caminho):
    """Lê um extrato de qualquer formato suportado."""
    return criar_leitor(caminho).ler(caminho)


def ler_csv(caminho):
    """Lê um extrato CSV (mantido para compatibilidade com a Sprint 2)."""
    return LeitorCSV().ler(caminho)
