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


# ---------------------------------------------------------------------------
# Sprint 4: casos extras cobertos pela refatoração da história 1
# ---------------------------------------------------------------------------
from analisador import ErroExtrato, LeitorCSV, criar_leitor, ler_extrato


def test_data_invalida_informa_a_linha(tmp_path):
    arquivo = criar_csv(tmp_path, (
        "data,descricao,categoria,valor\n"
        "10/03/2026,Lanche,Alimentação,12.50\n"
        "31/02/2026,Cinema,Lazer,30.00\n"
    ))

    with pytest.raises(ValueError, match="Linha 3: data inválida"):
        ler_csv(arquivo)


def test_numero_da_linha_considera_linhas_em_branco(tmp_path):
    arquivo = criar_csv(tmp_path, (
        "data,descricao,categoria,valor\n"
        "10/03/2026,Lanche,Alimentação,12.50\n"
        "\n"
        "11/03/2026,Ônibus,Transporte,abc\n"
    ))

    with pytest.raises(ValueError, match="Linha 4"):
        ler_csv(arquivo)


def test_lista_todas_as_colunas_que_faltam(tmp_path):
    arquivo = criar_csv(tmp_path, "data,valor\n10/03/2026,12.50\n")

    with pytest.raises(ValueError, match="'descricao', 'categoria'"):
        ler_csv(arquivo)


def test_arquivo_vazio(tmp_path):
    arquivo = criar_csv(tmp_path, "")

    with pytest.raises(ValueError, match="vazio"):
        ler_csv(arquivo)


def test_linha_com_campos_faltando(tmp_path):
    arquivo = criar_csv(tmp_path, (
        "data,descricao,categoria,valor\n"
        "10/03/2026,Lanche\n"
    ))

    with pytest.raises(ValueError, match="Linha 2: faltam campos"):
        ler_csv(arquivo)


def test_aceita_ponto_e_virgula_bom_e_cabecalho_maiusculo(tmp_path):
    arquivo = tmp_path / "extrato.csv"
    arquivo.write_text(
        "﻿Data;Descricao;Categoria;Valor\n"
        "05/03/2026; Mercado Dia ;Mercado;R$ 1.234,56\n",
        encoding="utf-8",
    )

    transacoes = ler_csv(arquivo)

    assert transacoes == [{
        "data": date(2026, 3, 5),
        "descricao": "Mercado Dia",
        "categoria": "Mercado",
        "valor": 1234.56,
    }]


def test_colunas_extras_sao_ignoradas(tmp_path):
    arquivo = criar_csv(tmp_path, (
        "data,descricao,categoria,valor,forma_pagamento\n"
        "05/03/2026,Uber,Transporte,23.40,Pix\n"
    ))

    transacoes = ler_csv(arquivo)

    assert set(transacoes[0]) == {"data", "descricao", "categoria", "valor"}


def test_fabrica_escolhe_leitor_pela_extensao():
    assert isinstance(criar_leitor("extrato.CSV"), LeitorCSV)

    with pytest.raises(ErroExtrato, match="não suportado"):
        criar_leitor("extrato.pdf")


def test_extrato_de_exemplo_completo():
    transacoes = ler_extrato("exemplos/extrato_completo.csv")

    assert len(transacoes) > 100
    assert all(t["valor"] > 0 for t in transacoes)
