import sys

from analisador import gastos_por_categoria, gastos_por_mes, ler_extrato, verificar_limites

LIMITES = {"Mercado": 300.0, "Lazer": 150.0, "Transporte": 100.0}


def formatar_valor(valor):
    texto = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {texto:>10}"


def formatar_transacao(t):
    data = t["data"].strftime("%d/%m/%Y")
    return f"{data}  {t['descricao']:<28} {t['categoria']:<14} {formatar_valor(t['valor'])}"


def main(argumentos):
    if len(argumentos) < 2:
        print("Uso: python3 main.py arquivo.csv")
        return 1

    caminho = argumentos[1]

    # História 1
    try:
        transacoes = ler_extrato(caminho)
    except FileNotFoundError:
        print(f"Erro: o arquivo '{caminho}' não existe")
        return 1
    except ValueError as erro:
        print(f"Erro: {erro}")
        return 1

    for t in transacoes:
        print(formatar_transacao(t))

    print(f"\n{len(transacoes)} transações carregadas")

    # História 2
    totais_categoria = gastos_por_categoria(transacoes)
    print("\nGastos por categoria:")
    for categoria, total in totais_categoria.items():
        print(f"  {categoria:<15} {formatar_valor(total)}")

    totais_mes = gastos_por_mes(transacoes)
    print("\nGastos por mês:")
    for mes, total in sorted(totais_mes.items()):
        print(f"  {mes:<15} {formatar_valor(total)}")

    # História 3
    alertas = verificar_limites(totais_categoria, LIMITES)
    print("\nAlertas de limite:")
    if len(alertas) == 0:
        print("  Nenhuma categoria passou do limite")
    for alerta in alertas:
        print(f"  {alerta['categoria']:<15} gastou {formatar_valor(alerta['gasto'])}")
        print(f"  {'':<15} limite {formatar_valor(alerta['limite'])}, passou {formatar_valor(alerta['excedente'])}")

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
