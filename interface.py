# Interface gráfica da história 1.
# A leitura do extrato é feita pelo analisador.py.

import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from analisador import ler_extrato

# cores
AZUL = "#1f4e8c"
AZUL_ESCURO = "#163a69"
FUNDO = "#f2f5f9"
BRANCO = "#ffffff"
BORDA = "#dde3ec"
TEXTO = "#1d2330"
CINZA = "#6b7686"
ZEBRA = "#f6f8fb"

FONTE = "Segoe UI" if sys.platform == "win32" else "DejaVu Sans"

TODAS = "Todas as categorias"


def formatar_valor(valor):
    texto = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {texto}"


class Janela:

    def __init__(self, raiz):
        self.raiz = raiz
        self.transacoes = []

        raiz.title("Analisador de Gastos Pessoais")
        raiz.geometry("920x620")
        raiz.minsize(760, 480)
        raiz.configure(bg=FUNDO)

        self.criar_estilos()
        self.criar_topo()
        self.criar_cards()
        self.criar_filtro()
        self.criar_tabela()
        self.criar_rodape()

    def criar_estilos(self):
        estilo = ttk.Style()
        estilo.theme_use("clam")

        estilo.configure("Primario.TButton", font=(FONTE, 10, "bold"),
                         background=BRANCO, foreground=AZUL,
                         borderwidth=0, padding=(14, 8))
        estilo.map("Primario.TButton", background=[("active", "#e4ecf7")])

        estilo.configure("Treeview", font=(FONTE, 10), rowheight=30,
                         background=BRANCO, fieldbackground=BRANCO,
                         foreground=TEXTO, borderwidth=0)
        estilo.configure("Treeview.Heading", font=(FONTE, 10, "bold"),
                         background="#e8eef7", foreground=AZUL_ESCURO,
                         relief="flat", padding=(8, 6))
        estilo.map("Treeview", background=[("selected", AZUL)],
                   foreground=[("selected", BRANCO)])
        estilo.map("Treeview.Heading", background=[("active", "#dbe5f3")])

        estilo.configure("TCombobox", padding=6)

    def criar_topo(self):
        topo = tk.Frame(self.raiz, bg=AZUL, padx=24, pady=18)
        topo.pack(fill="x")

        textos = tk.Frame(topo, bg=AZUL)
        textos.pack(side="left")
        tk.Label(textos, text="Analisador de Gastos Pessoais", bg=AZUL, fg=BRANCO,
                 font=(FONTE, 17, "bold")).pack(anchor="w")
        self.rotulo_arquivo = tk.Label(textos, text="Nenhum extrato carregado",
                                       bg=AZUL, fg="#c9d7ec", font=(FONTE, 10))
        self.rotulo_arquivo.pack(anchor="w", pady=(2, 0))

        ttk.Button(topo, text="Abrir extrato...", style="Primario.TButton",
                   command=self.abrir).pack(side="right")

    def criar_cards(self):
        area = tk.Frame(self.raiz, bg=FUNDO, padx=24, pady=16)
        area.pack(fill="x")

        self.cards = {}
        for i, titulo in enumerate(["Transações", "Total gasto", "Período", "Maior gasto"]):
            area.columnconfigure(i, weight=1, uniform="cards")
            card = tk.Frame(area, bg=BRANCO, padx=16, pady=12,
                            highlightbackground=BORDA, highlightthickness=1)
            card.grid(row=0, column=i, sticky="nsew", padx=(0 if i == 0 else 12, 0))

            tk.Label(card, text=titulo.upper(), bg=BRANCO, fg=CINZA,
                     font=(FONTE, 8, "bold")).pack(anchor="w")
            valor = tk.Label(card, text="-", bg=BRANCO, fg=TEXTO,
                             font=(FONTE, 15, "bold"))
            valor.pack(anchor="w", pady=(4, 0))
            detalhe = tk.Label(card, text=" ", bg=BRANCO, fg=CINZA, font=(FONTE, 9))
            detalhe.pack(anchor="w")
            self.cards[titulo] = (valor, detalhe)

    def criar_filtro(self):
        linha = tk.Frame(self.raiz, bg=FUNDO, padx=24)
        linha.pack(fill="x")

        tk.Label(linha, text="Transações", bg=FUNDO, fg=TEXTO,
                 font=(FONTE, 12, "bold")).pack(side="left")

        self.filtro = ttk.Combobox(linha, state="readonly", width=24, values=[TODAS])
        self.filtro.set(TODAS)
        self.filtro.bind("<<ComboboxSelected>>", lambda _: self.atualizar())
        self.filtro.pack(side="right")
        tk.Label(linha, text="Categoria:", bg=FUNDO, fg=CINZA,
                 font=(FONTE, 10)).pack(side="right", padx=(0, 8))

    def criar_tabela(self):
        moldura = tk.Frame(self.raiz, bg=BRANCO, highlightbackground=BORDA,
                           highlightthickness=1)
        moldura.pack(fill="both", expand=True, padx=24, pady=(10, 0))

        colunas = ("data", "descricao", "categoria", "valor")
        self.tabela = ttk.Treeview(moldura, columns=colunas, show="headings")
        self.tabela.heading("data", text="Data")
        self.tabela.heading("descricao", text="Descrição", anchor="w")
        self.tabela.heading("categoria", text="Categoria", anchor="w")
        self.tabela.heading("valor", text="Valor", anchor="e")
        self.tabela.column("data", width=100, anchor="center", stretch=False)
        self.tabela.column("descricao", width=320)
        self.tabela.column("categoria", width=170)
        self.tabela.column("valor", width=130, anchor="e", stretch=False)
        self.tabela.tag_configure("par", background=ZEBRA)

        barra = ttk.Scrollbar(moldura, orient="vertical", command=self.tabela.yview)
        self.tabela.configure(yscrollcommand=barra.set)
        self.tabela.pack(side="left", fill="both", expand=True)
        barra.pack(side="right", fill="y")

        # aparece enquanto nenhum extrato foi aberto
        self.aviso_vazio = tk.Label(
            moldura, bg=BRANCO, fg=CINZA, font=(FONTE, 11),
            text="Clique em \"Abrir extrato...\" para carregar um arquivo CSV",
        )
        self.aviso_vazio.place(relx=0.5, rely=0.5, anchor="center")

    def criar_rodape(self):
        self.rodape = tk.Label(self.raiz, text="Pronto", bg=FUNDO, fg=CINZA,
                               font=(FONTE, 9), anchor="w", padx=24, pady=10)
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

        self.transacoes = transacoes
        self.rotulo_arquivo.config(text=Path(caminho).name)

        categorias = sorted({t["categoria"] for t in transacoes})
        self.filtro.config(values=[TODAS] + categorias)
        self.filtro.set(TODAS)

        self.atualizar()

    def atualizar(self):
        categoria = self.filtro.get()
        if categoria == TODAS:
            lista = self.transacoes
        else:
            lista = [t for t in self.transacoes if t["categoria"] == categoria]

        self.tabela.delete(*self.tabela.get_children())
        for i, t in enumerate(lista):
            self.tabela.insert("", "end", tags=("par",) if i % 2 else (), values=(
                t["data"].strftime("%d/%m/%Y"),
                t["descricao"],
                t["categoria"],
                formatar_valor(t["valor"]),
            ))

        if lista:
            self.aviso_vazio.place_forget()
        else:
            self.aviso_vazio.config(text="Nenhuma transação encontrada")
            self.aviso_vazio.place(relx=0.5, rely=0.5, anchor="center")

        self.atualizar_cards(lista)
        self.rodape.config(text=f"Mostrando {len(lista)} de {len(self.transacoes)} transações")

    def atualizar_cards(self, lista):
        def mostrar(card, valor, detalhe=" "):
            self.cards[card][0].config(text=valor)
            self.cards[card][1].config(text=detalhe)

        if not lista:
            for card in self.cards:
                mostrar(card, "-")
            return

        total = sum(t["valor"] for t in lista)
        datas = [t["data"] for t in lista]
        maior = max(lista, key=lambda t: t["valor"])

        mostrar("Transações", str(len(lista)))
        mostrar("Total gasto", formatar_valor(total),
                f"média de {formatar_valor(total / len(lista))}")
        mostrar("Período", min(datas).strftime("%d/%m/%y"),
                f"até {max(datas).strftime('%d/%m/%y')}")
        mostrar("Maior gasto", formatar_valor(maior["valor"]), maior["descricao"])


if __name__ == "__main__":
    raiz = tk.Tk()
    Janela(raiz)
    raiz.mainloop()
