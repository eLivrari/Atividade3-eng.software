import csv
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path

COLUNAS = ["data", "descricao", "categoria", "valor"]


class ErroExtrato(ValueError):
    pass


def converter_valor(texto, numero_linha):
    # aceita 12.50, 12,50, 1.200,00 e R$ 12,50
    limpo = texto.replace("R$", "").replace(" ", "")
    if "," in limpo:
        limpo = limpo.replace(".", "").replace(",", ".")
    try:
        return float(limpo)
    except ValueError:
        raise ErroExtrato(f"Linha {numero_linha}: valor inválido '{texto}'")


def converter_data(texto, numero_linha):
    try:
        return datetime.strptime(texto.strip(), "%d/%m/%Y").date()
    except ValueError:
        raise ErroExtrato(f"Linha {numero_linha}: data inválida '{texto}'")


def criar_transacao(linha, numero_linha):
    for coluna in COLUNAS:
        if linha.get(coluna) is None:
            raise ErroExtrato(f"Linha {numero_linha}: está faltando o campo '{coluna}'")

    return {
        "data": converter_data(linha["data"], numero_linha),
        "descricao": linha["descricao"].strip(),
        "categoria": linha["categoria"].strip(),
        "valor": converter_valor(linha["valor"], numero_linha),
    }


# Template Method: ler() é igual pra todo formato,
# cada subclasse só implementa como pegar as linhas do arquivo
class LeitorExtrato(ABC):

    def ler(self, caminho):
        # utf-8-sig por causa do csv salvo pelo Excel
        with open(caminho, encoding="utf-8-sig", newline="") as arquivo:
            cabecalho, linhas = self.extrair_linhas(arquivo)
            self.validar_colunas(cabecalho)
            return [criar_transacao(linha, numero) for numero, linha in linhas]

    @abstractmethod
    def extrair_linhas(self, arquivo):
        pass

    def validar_colunas(self, cabecalho):
        if not cabecalho:
            raise ErroExtrato("O arquivo está vazio")
        faltando = [c for c in COLUNAS if c not in cabecalho]
        if faltando:
            nomes = ", ".join(f"'{c}'" for c in faltando)
            raise ErroExtrato(f"Está faltando a coluna {nomes} no arquivo")


class LeitorCSV(LeitorExtrato):

    def extrair_linhas(self, arquivo):
        # alguns bancos exportam com ; em vez de ,
        primeira = arquivo.readline()
        arquivo.seek(0)
        separador = ";" if primeira.count(";") > primeira.count(",") else ","

        leitor = csv.DictReader(arquivo, delimiter=separador)
        if leitor.fieldnames:
            leitor.fieldnames = [nome.strip().lower() for nome in leitor.fieldnames]

        # line_num é a linha de verdade no arquivo (conta linhas em branco)
        linhas = ((leitor.line_num, linha) for linha in leitor)
        return leitor.fieldnames, linhas


# Factory: escolhe o leitor pela extensão do arquivo
LEITORES = {
    ".csv": LeitorCSV,
}


def criar_leitor(caminho):
    extensao = Path(caminho).suffix.lower()
    if extensao not in LEITORES:
        raise ErroExtrato(f"Formato '{extensao}' não suportado")
    return LEITORES[extensao]()


def ler_extrato(caminho):
    return criar_leitor(caminho).ler(caminho)


def ler_csv(caminho):
    return LeitorCSV().ler(caminho)


def gastos_por_categoria(transacoes):
    totais = {}
    nomes_originais = {}

    for transacao in transacoes:
        chave = transacao["categoria"].strip().lower()
        if chave not in nomes_originais:
            nomes_originais[chave] = transacao["categoria"].strip()
            totais[nomes_originais[chave]] = 0.0

        nome_exibicao = nomes_originais[chave]
        totais[nome_exibicao] += transacao["valor"]

    return totais


def gastos_por_mes(transacoes):
    totais = {}

    for transacao in transacoes:
        mes = transacao["data"].strftime("%Y-%m")
        totais[mes] = totais.get(mes, 0.0) + transacao["valor"]

    return totais

def verificar_limites(total, limites):
    alertas = []

    for categoria in limites:
        if limites[categoria] < 0:
            raise ValueError("Limite negativo não é permitido")

    for categoria in total:
        gasto = total[categoria]

        if categoria not in limites:
            continue

        limite = limites[categoria]

        if gasto > limite:
            alerta = {
                "categoria": categoria,"gasto": gasto,"limite": limite, "excedente" : gasto - limite,
            }
            alertas.append(alerta)
    alertas.sort(key= pegar_excedente, reverse=True)

    return alertas

def pegar_excedente(alerta):
    return alerta["excedente"]
