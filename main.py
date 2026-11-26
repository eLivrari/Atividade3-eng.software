import sys

from analisador import ler_extrato
from analisador import gastos_por_categoria, gastos_por_mes, ler_csv, verificar_limites


def formatar_transacao(t):
    data = t["data"].strftime("%d/%m/%Y")
    valor = f"{t['valor']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{data}  {t['descricao']:<28} {t['categoria']:<14} R$ {valor:>10}"


def main(argumentos):
    if len(argumentos) < 2:
        print("Uso: python3 main.py arquivo.csv")
        return 1

    caminho = argumentos[1]

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
    return 0

    totais_categoria = gastos_por_categoria(transacoes)
    print("\nGastos por categoria:")
    for categoria, total in totais_categoria.items():
        print(f"  {categoria:<15} R$ {total:.2f}")

if __name__ == "__main__":
    sys.exit(main(sys.argv))
    totais_mes = gastos_por_mes(transacoes)
    print("\nGastos por mês:")
    for mes, total in sorted(totais_mes.items()):
        print(f"  {mes:<15} R$ {total:.2f}")

    limites = {"Mercado": 300.0, "Lazer": 150.0, "Transporte": 100.0}
    alertas = verificar_limites(totais_categoria, limites)

    print("\nAlertas de limite:")
    if len(alertas) == 0:
        print("  Nenhuma categoria passou do limite")
    for alerta in alertas:
        print(f"  {alerta['categoria']:<15} gastou R$ {alerta['gasto']:.2f}")
        print(f"  {'':<15} limite R$ {alerta['limite']:.2f}, passou R$ {alerta['excedente']:.2f}")

main()
