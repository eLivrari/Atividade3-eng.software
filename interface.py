import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from analisador import ler_extrato


def formatar_valor(valor):
    texto = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {texto}"


class Janela:

    def __init__(self, raiz):
        self.raiz = raiz
        raiz.title("Analisador de Gastos Pessoais")
        raiz.geometry("760x480")

        topo = ttk.Frame(raiz, padding=10)
        topo.pack(fill="x")

        ttk.Button(topo, text="Abrir extrato...", command=self.abrir).pack(side="left")
        self.rotulo_arquivo = ttk.Label(topo, text="Nenhum arquivo carregado")
        self.rotulo_arquivo.pack(side="left", padx=10)

        meio = ttk.Frame(raiz, padding=(10, 0))
        meio.pack(fill="both", expand=True)

        colunas = ("data", "descricao", "categoria", "valor")
        self.tabela = ttk.Treeview(meio, columns=colunas, show="headings")
        self.tabela.heading("data", text="Data")
        self.tabela.heading("descricao", text="Descrição")
        self.tabela.heading("categoria", text="Categoria")
        self.tabela.heading("valor", text="Valor")
        self.tabela.column("data", width=90, anchor="center")
        self.tabela.column("descricao", width=300)
        self.tabela.column("categoria", width=150)
        self.tabela.column("valor", width=120, anchor="e")

        barra = ttk.Scrollbar(meio, orient="vertical", command=self.tabela.yview)
        self.tabela.configure(yscrollcommand=barra.set)
        self.tabela.pack(side="left", fill="both", expand=True)
        barra.pack(side="right", fill="y")

        self.rodape = ttk.Label(raiz, text="", padding=10)
        self.rodape.pack(fill="x")

    def abrir(self):
        caminho = filedialog.askopenfilename(
            title="Escolha o extrato",
            filetypes=[("Arquivos CSV", "*.csv"), ("Todos os arquivos", "*.*")],
        )
        if not caminho:
            return

        try:
            transacoes = ler_extrato(caminho)
        except FileNotFoundError:
            messagebox.showerror("Erro", "Arquivo não encontrado")
            return
        except ValueError as erro:
            messagebox.showerror("Erro no extrato", str(erro))
            return

        self.mostrar(transacoes)
        self.rotulo_arquivo.config(text=caminho)

    def mostrar(self, transacoes):
        self.tabela.delete(*self.tabela.get_children())
        for t in transacoes:
            self.tabela.insert("", "end", values=(
                t["data"].strftime("%d/%m/%Y"),
                t["descricao"],
                t["categoria"],
                formatar_valor(t["valor"]),
            ))

        total = sum(t["valor"] for t in transacoes)
        self.rodape.config(
            text=f"{len(transacoes)} transações carregadas    Total: {formatar_valor(total)}"
        )


if __name__ == "__main__":
    raiz = tk.Tk()
    Janela(raiz)
    raiz.mainloop()
