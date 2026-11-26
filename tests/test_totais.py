# Testes da história 2: ver quanto gastei por categoria e por mês
from datetime import date

import pytest

from analisador import (
    AgrupamentoPorCategoria,
    AgrupamentoPorMes,
    EstrategiaAgrupamento,
    FachadaTotais,
    TotalizadorArredondado,
    TotalizadorGastos,
    TotalizadorOrdenado,
    gastos_por_categoria,
    gastos_por_mes,
)


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


# --- Testes da refatoração (Sprint 4): Strategy, Decorator e Facade ---


def test_categoria_com_espacos_e_vazia():
    transacoes = [
        t(date(2026, 3, 5), "  Mercado  ", 10.0),
        t(date(2026, 3, 6), "mercado", 5.0),
        t(date(2026, 3, 7), "   ", 12.0),
    ]

    totais = gastos_por_categoria(transacoes)

    assert totais == {"Sem categoria": 12.0, "Mercado": 15.0}


def test_strategy_personalizada():
    class AgrupamentoPorAno(EstrategiaAgrupamento):
        def chave(self, transacao):
            return str(transacao["data"].year)

    transacoes = [
        t(date(2025, 12, 30), "Lazer", 50.0),
        t(date(2026, 1, 10), "Mercado", 100.0),
    ]

    totais = TotalizadorGastos(AgrupamentoPorAno()).calcular(transacoes)

    assert totais == {"2025": 50.0, "2026": 100.0}


def test_decorator_arredondamento_e_ordenacao():
    transacoes = [
        t(date(2026, 4, 2), "Lazer", 0.1),
        t(date(2026, 3, 1), "Mercado", 100.0),
        t(date(2026, 4, 5), "Lazer", 0.2),
    ]

    calculador = TotalizadorOrdenado(
        TotalizadorArredondado(TotalizadorGastos(AgrupamentoPorMes())),
        por_valor=False,
        reverso=False,
    )
    totais = calculador.calcular(transacoes)

    assert list(totais.items()) == [("2026-03", 100.0), ("2026-04", 0.3)]


def test_decorator_ordena_categorias_por_maior_gasto():
    totais = gastos_por_categoria(TRANSACOES)

    assert list(totais.keys()) == ["Mercado", "Lazer"]


def test_fachada_resumo_completo():
    fachada = FachadaTotais()
    resumo = fachada.resumo_completo(TRANSACOES)

    assert resumo["por_categoria"] == {"Mercado": 185.5, "Lazer": 30.0}
    assert resumo["por_mes"] == {"2026-03": 155.5, "2026-04": 60.0}
    assert resumo["total_geral"] == 215.5
    assert fachada.resumo_completo([]) == {
        "por_categoria": {},
        "por_mes": {},
        "total_geral": 0.0,
    }
