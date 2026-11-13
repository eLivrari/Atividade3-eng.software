import csv
from datetime import datetime

COLUNAS = ["data", "descricao", "categoria", "valor"]


def converter_valor(texto, numero_linha):
    # aceita 12.50, 12,50 e 1.200,00
    if "," in texto:
        texto = texto.replace(".", "").replace(",", ".")
    try:
        return float(texto)
    except ValueError:
        raise ValueError(f"Linha {numero_linha}: valor inválido '{texto}'")


def ler_csv(caminho):
    with open(caminho, encoding="utf-8") as arquivo:
        leitor = csv.DictReader(arquivo)

        for coluna in COLUNAS:
            if coluna not in leitor.fieldnames:
                raise ValueError(f"Está faltando a coluna '{coluna}' no arquivo")

        transacoes = []
        numero_linha = 1  # a linha 1 é o cabeçalho
        for linha in leitor:
            numero_linha += 1
            transacao = {
                "data": datetime.strptime(linha["data"], "%d/%m/%Y").date(),
                "descricao": linha["descricao"],
                "categoria": linha["categoria"],
                "valor": converter_valor(linha["valor"], numero_linha),
            }
            transacoes.append(transacao)

    return transacoes


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