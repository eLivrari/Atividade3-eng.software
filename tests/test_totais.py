# Testes da história 2: ver quanto gastei por categoria e por mês
from datetime import date

import pytest

from analisador import gastos_por_categoria, gastos_por_mes


def t(dia, categoria, valor):
    return {"data": dia, "descricao": "x", "categoria": categoria, "valor": valor}


TRANSACOES = [
    t(date(2026, 3, 5), "Mercado", 80.0),
    t(date(2026, 3, 20), "Mercado", 45.5),
    t(date(2026, 3, 21), "Lazer", 30.0),
    t(date(2026, 4, 2), "Mercado", 60.0),
]


# História 2, critério 1
def test_total_por_categoria():
    totais = gastos_por_categoria(TRANSACOES)

    assert totais["Mercado"] == pytest.approx(185.5)
    assert totais["Lazer"] == pytest.approx(30.0)


# História 2, critério 2
def test_total_por_mes():
    totais = gastos_por_mes(TRANSACOES)

    assert totais == {"2026-03": pytest.approx(155.5), "2026-04": pytest.approx(60.0)}


# História 2, critério 3
def test_categoria_ignora_maiuscula():
    transacoes = [
        t(date(2026, 3, 5), "Mercado", 10.0),
        t(date(2026, 3, 6), "mercado", 5.0),
    ]

    totais = gastos_por_categoria(transacoes)

    assert len(totais) == 1
    assert list(totais.values())[0] == pytest.approx(15.0)


# História 2, critério 4
def test_lista_vazia():
    assert gastos_por_categoria([]) == {}
    assert gastos_por_mes([]) == {}
