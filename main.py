import sys

from analisador import ler_csv


def main():
    if len(sys.argv) < 2:
        print("Uso: python3 main.py arquivo.csv")
        return

    caminho = sys.argv[1]

    try:
        transacoes = ler_csv(caminho)
    except FileNotFoundError:
        print(f"Erro: o arquivo '{caminho}' não existe")
        return
    except ValueError as erro:
        print(f"Erro: {erro}")
        return

    for t in transacoes:
        data = t["data"].strftime("%d/%m/%Y")
        print(f"{data}  {t['descricao']:<25} {t['categoria']:<15} R$ {t['valor']:.2f}")

    print(f"\n{len(transacoes)} transações carregadas")


main()
