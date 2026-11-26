import sys

from analisador import ler_extrato


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


if __name__ == "__main__":
    sys.exit(main(sys.argv))
