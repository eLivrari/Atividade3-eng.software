# Testes da história 1: carregar o extrato em CSV
from datetime import date

import pytest

from analisador import ler_csv


def criar_csv(pasta, conteudo):
    arquivo = pasta / "extrato.csv"
    arquivo.write_text(conteudo, encoding="utf-8")
    return arquivo


# História 1, critério 1
def test_le_linhas(tmp_path):
    arquivo = criar_csv(tmp_path, (
        "data,descricao,categoria,valor\n"
        "05/03/2026,Pão de açúcar,Mercado,80.00\n"
        "06/03/2026,Uber,Transporte,23.40\n"
    ))

    transacoes = ler_csv(arquivo)

    assert len(transacoes) == 2
    assert transacoes[0]["descricao"] == "Pão de açúcar"
    assert transacoes[1]["categoria"] == "Transporte"


# História 1, critério 2
def test_data(tmp_path):
    arquivo = criar_csv(tmp_path, (
        "data,descricao,categoria,valor\n"
        "05/03/2026,Cinema,Lazer,30.00\n"
    ))

    transacoes = ler_csv(arquivo)

    assert transacoes[0]["data"] == date(2026, 3, 5)


# História 1, critério 3
def test_valor_com_virgula(tmp_path):
    arquivo = criar_csv(tmp_path, (
        'data,descricao,categoria,valor\n'
        '10/03/2026,Lanche,Alimentação,"12,50"\n'
    ))

    transacoes = ler_csv(arquivo)

    assert transacoes[0]["valor"] == 12.5


# História 1, critério 4
def test_falta_coluna(tmp_path):
    arquivo = criar_csv(tmp_path, (
        "data,descricao,valor\n"
        "10/03/2026,Lanche,12.50\n"
    ))

    with pytest.raises(ValueError, match="categoria"):
        ler_csv(arquivo)


# História 1, critério 5
# linha 3 contando o cabeçalho
def test_valor_invalido(tmp_path):
    arquivo = criar_csv(tmp_path, (
        "data,descricao,categoria,valor\n"
        "10/03/2026,Lanche,Alimentação,12.50\n"
        "11/03/2026,Ônibus,Transporte,abc\n"
    ))

    with pytest.raises(ValueError, match="3"):
        ler_csv(arquivo)
