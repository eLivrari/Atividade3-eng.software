# Testes da história 3: ser avisado quando passar do limite
import pytest

from analisador import verificar_limites


# História 3, critério 1
def test_alerta_quando_passa_do_limite():
    alertas = verificar_limites({"Lazer": 250.0}, {"Lazer": 200.0})

    assert len(alertas) == 1
    assert alertas[0]["categoria"] == "Lazer"
    assert alertas[0]["gasto"] == 250.0
    assert alertas[0]["limite"] == 200.0
    assert alertas[0]["excedente"] == 50.0


# História 3, critério 2
def test_sem_alerta_quando_igual_ao_limite():
    alertas = verificar_limites({"Mercado": 400.0}, {"Mercado": 400.0})

    assert alertas == []


# História 3, critério 3
def test_sem_alerta_para_categoria_sem_limite():
    alertas = verificar_limites({"Transporte": 900.0}, {"Mercado": 400.0})

    assert alertas == []


# História 3, critério 4
def test_alertas_ordenados_pelo_excedente():
    totais = {"Lazer": 220.0, "Mercado": 500.0, "Transporte": 130.0}
    limites = {"Lazer": 200.0, "Mercado": 400.0, "Transporte": 100.0}

    alertas = verificar_limites(totais, limites)

    assert [a["categoria"] for a in alertas] == ["Mercado", "Transporte", "Lazer"]


# História 3, critério 5
def test_limite_negativo_da_erro():
    with pytest.raises(ValueError):
        verificar_limites({"Lazer": 50.0}, {"Lazer": -10.0})
