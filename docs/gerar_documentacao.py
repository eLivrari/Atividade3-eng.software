"""Gera docs/documentacao.html a partir do repositório (histórico de commits incluso)."""
import html
import subprocess
import sys
from pathlib import Path

REPO = Path(sys.argv[1])
SAIDA = Path(sys.argv[2])


def git(*args):
    return subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True, check=True).stdout


commits = []
for linha in git("log", "--format=%h|%an|%ad|%s", "--date=short").strip().splitlines():
    h, autor, data, msg = linha.split("|", 3)
    stat = git("show", "--shortstat", "--format=", h).strip()
    arquivos = git("show", "--name-only", "--format=", h).split()
    commits.append((h, autor, data, msg, stat, arquivos))

e = html.escape


def linhas_commits():
    out = []
    for h, autor, data, msg, stat, arquivos in commits:
        arqs = ", ".join(f"<code>{e(a)}</code>" for a in arquivos[:6])
        if len(arquivos) > 6:
            arqs += f" e mais {len(arquivos) - 6}"
        stat = stat.replace("files changed", "arquivos").replace("file changed", "arquivo") \
            .replace("insertions(+)", "inserções").replace("insertion(+)", "inserção") \
            .replace("deletions(-)", "remoções").replace("deletion(-)", "remoção")
        out.append(f"<tr><td><code>{h}</code></td><td style='white-space:nowrap'>{e(data)}</td><td>{e(autor)}</td>"
                   f"<td><b>{e(msg)}</b><div class='arqs'>{arqs}</div><div class='stat'>{e(stat)}</div></td></tr>")
    return "\n".join(out)


autores = {}
for c in commits:
    autores[c[1]] = autores.get(c[1], 0) + 1
resumo_autores = ", ".join(f"{e(a)} ({n})" for a, n in autores.items())

pytest = subprocess.run([sys.executable, "-m", "pytest", "tests/test_carregar_csv.py", "-v", "-p", "no:cacheprovider"],
                        cwd=REPO, capture_output=True, text=True).stdout
testes = [l.split("::")[1].split(" ")[0] for l in pytest.splitlines() if "::" in l and "PASSED" in l]
resumo_pytest = pytest.strip().splitlines()[-1].strip("= ")

demo = subprocess.run([sys.executable, "main.py", "exemplos/extrato_completo.csv"], cwd=REPO,
                      capture_output=True, text=True).stdout.splitlines()
demo_txt = "\n".join(demo[:8] + ["..."] + demo[-3:])
erros = "\n".join(
    "$ python3 main.py " + arq + "\n" + subprocess.run([sys.executable, "main.py", arq], cwd=REPO,
                                                        capture_output=True, text=True).stdout.strip()
    for arq in ["exemplos/extrato_sem_coluna.csv", "exemplos/extrato_valor_invalido.csv", "extrato.pdf"])

ARQ_SVG = """
<svg viewBox="0 0 720 300" class="diag" style="width:82%" xmlns="http://www.w3.org/2000/svg">
<defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0L10,5L0,10z" fill="#334"/></marker></defs>
<rect x="10" y="120" width="100" height="50" rx="25" class="ext"/><text x="60" y="142" class="t">Usuário</text><text x="60" y="158" class="s">terminal</text>
<rect x="150" y="105" width="140" height="80" rx="6" class="ui"/><text x="220" y="128" class="t">Interface</text>
<text x="220" y="146" class="s">main.py (terminal)</text><text x="220" y="160" class="s">interface.py (janela)</text>
<rect x="330" y="20" width="370" height="265" rx="8" class="grupo"/><text x="515" y="40" class="t">analisador.py: regras de negócio</text>
<rect x="350" y="55" width="330" height="62" rx="6" class="h1"/><text x="515" y="78" class="t">Leitor de extrato (História 1)</text>
<text x="515" y="96" class="s">criar_leitor() → LeitorCSV.ler() · ErroExtrato</text>
<rect x="350" y="130" width="330" height="62" rx="6" class="h"/><text x="515" y="153" class="t">Totalizador (História 2)</text>
<text x="515" y="171" class="s">gastos_por_categoria() · gastos_por_mes()</text>
<rect x="350" y="205" width="330" height="62" rx="6" class="h"/><text x="515" y="228" class="t">Verificador de limites (História 3)</text>
<text x="515" y="246" class="s">verificar_limites()</text>
<line x1="110" y1="145" x2="148" y2="145" class="l" marker-end="url(#a)"/>
<line x1="290" y1="125" x2="348" y2="86" class="l" marker-end="url(#a)"/>
<line x1="290" y1="145" x2="348" y2="161" class="l" marker-end="url(#a)"/>
<line x1="290" y1="165" x2="348" y2="236" class="l" marker-end="url(#a)"/>
</svg>"""

CLASSES_SVG = """
<svg viewBox="0 0 720 360" class="diag" xmlns="http://www.w3.org/2000/svg">
<defs>
<marker id="her" viewBox="0 0 12 12" refX="11" refY="6" markerWidth="12" markerHeight="12" orient="auto"><path d="M0,0L12,6L0,12z" fill="#fff" stroke="#334"/></marker>
<marker id="dep" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0L10,5L0,10" fill="none" stroke="#334"/></marker>
</defs>
<g>
<rect x="240" y="10" width="250" height="106" class="cls"/>
<text x="365" y="28" class="s i">«abstract»</text><text x="365" y="44" class="t">LeitorExtrato</text>
<line x1="240" y1="52" x2="490" y2="52" class="l"/>
<text x="250" y="72" class="m">+ ler(caminho)</text>
<text x="250" y="88" class="m i">+ extrair_linhas(arquivo)</text>
<text x="250" y="104" class="m">+ validar_colunas(cabecalho)</text>
</g>
<g>
<rect x="240" y="200" width="250" height="60" class="cls"/>
<text x="365" y="220" class="t">LeitorCSV</text>
<line x1="240" y1="228" x2="490" y2="228" class="l"/>
<text x="250" y="248" class="m">+ extrair_linhas(arquivo)</text>
</g>
<line x1="365" y1="200" x2="365" y2="118" class="l" marker-end="url(#her)"/>
<g>
<rect x="10" y="150" width="200" height="130" class="cls mod"/>
<text x="110" y="168" class="s i">«módulo analisador»</text><text x="110" y="184" class="t">Factory</text>
<line x1="10" y1="192" x2="210" y2="192" class="l"/>
<text x="20" y="208" class="m">LEITORES = {".csv": LeitorCSV}</text>
<text x="20" y="226" class="m">criar_leitor(caminho)</text>
<text x="20" y="244" class="m">ler_extrato(caminho)</text>
<text x="20" y="262" class="m">ler_csv(caminho)</text>
</g>
<line x1="210" y1="230" x2="238" y2="230" class="l d" marker-end="url(#dep)"/><text x="224" y="222" class="s">cria</text>
<g>
<rect x="540" y="30" width="170" height="40" class="cls"/><text x="625" y="55" class="t">ValueError</text>
<rect x="540" y="130" width="170" height="40" class="cls"/><text x="625" y="155" class="t">ErroExtrato</text>
</g>
<line x1="625" y1="130" x2="625" y2="72" class="l" marker-end="url(#her)"/>
<line x1="490" y1="110" x2="538" y2="145" class="l d" marker-end="url(#dep)"/><text x="528" y="108" class="s">lança</text>
<g>
<rect x="540" y="200" width="170" height="80" class="cls mod"/>
<text x="625" y="218" class="s i">«funções»</text>
<text x="550" y="238" class="m">converter_data()</text>
<text x="550" y="254" class="m">converter_valor()</text>
<text x="550" y="270" class="m">criar_transacao()</text>
</g>
<line x1="490" y1="122" x2="580" y2="198" class="l d" marker-end="url(#dep)"/><text x="548" y="178" class="s">usa</text>
<text x="20" y="320" class="s" style="text-anchor:start">Seta vazada: herança. Seta tracejada: dependência.</text>
</svg>"""

SEQ_SVG = """
<svg viewBox="0 0 720 380" class="diag" xmlns="http://www.w3.org/2000/svg">
<defs><marker id="s" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0L10,5L0,10z" fill="#334"/></marker></defs>
""" + "".join(
    f'<rect x="{x-60}" y="10" width="120" height="34" rx="4" class="cls"/><text x="{x}" y="32" class="t">{n}</text>'
    f'<line x1="{x}" y1="44" x2="{x}" y2="370" class="l d"/>'
    for x, n in [(70, "main / interface"), (220, "ler_extrato"), (370, "criar_leitor"), (520, "LeitorCSV"), (660, "funções")]
) + "".join(
    f'<line x1="{a}" y1="{y}" x2="{b}" y2="{y}" class="l{" d" if r else ""}" marker-end="url(#s)"/>'
    f'<text x="{(a+b)/2}" y="{y-6}" class="s">{t}</text>'
    for a, b, y, t, r in [
        (70, 220, 75, "ler_extrato(caminho)", 0),
        (220, 370, 105, "criar_leitor(caminho)", 0),
        (370, 520, 135, "LeitorCSV()  [extensão .csv]", 0),
        (370, 220, 160, "leitor", 1),
        (220, 520, 190, "ler(caminho)", 0),
        (520, 520, 0, "", 0),
        (520, 660, 280, "criar_transacao(registro, linha)", 0),
        (660, 520, 310, "transação ou ErroExtrato(\"Linha N…\")", 1),
        (520, 70, 350, "lista de transações  /  ValueError → \"Erro: …\"", 1),
    ] if a != b
) + """
<path d="M520,212 h40 v20 h-38" class="l" fill="none" marker-end="url(#s)"/><text x="566" y="226" class="s" style="text-anchor:start">extrair_linhas()</text>
<path d="M520,240 h40 v20 h-38" class="l" fill="none" marker-end="url(#s)"/><text x="566" y="254" class="s" style="text-anchor:start">validar_colunas()</text>
</svg>"""

PRINT = REPO / "docs" / "interface.png"
if PRINT.exists():
    PRINT_INTERFACE = f'<img src="{PRINT.resolve().as_uri()}" style="width:85%;border:1px solid #ccc"><p class="leg">Figura 4: interface gráfica com o extrato de exemplo.</p>'
else:
    PRINT_INTERFACE = ""

pagina = f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<title>Analisador de Gastos Pessoais: Documentação Sprint 4</title>
<style>
@page {{ size: A4; margin: 18mm 16mm; }}
body {{ font-family: "DejaVu Sans", sans-serif; font-size: 10.5pt; color: #1d2330; line-height: 1.45; }}
h1 {{ font-size: 24pt; margin: 0 0 6px; color: #1c3d6e; }}
h2 {{ font-size: 15pt; color: #1c3d6e; border-bottom: 2px solid #1c3d6e; padding-bottom: 3px; margin-top: 22px; break-after: avoid; }}
h3 {{ font-size: 12pt; margin: 14px 0 4px; break-after: avoid; }}
.capa {{ height: 255mm; display: flex; flex-direction: column; justify-content: center; break-after: page; }}
.capa .sub {{ font-size: 14pt; color: #4a5568; }}
.capa .info {{ margin-top: 40px; font-size: 11pt; }}
table {{ border-collapse: collapse; width: 100%; margin: 6px 0 10px; font-size: 9.5pt; }}
th, td {{ border: 1px solid #c8cfdb; padding: 4px 6px; vertical-align: top; text-align: left; }}
th {{ background: #e8eef8; }}
tr {{ break-inside: avoid; }}
code {{ font-family: "DejaVu Sans Mono", monospace; font-size: 8.8pt; background: #f1f3f7; padding: 0 2px; }}
pre {{ font-family: "DejaVu Sans Mono", monospace; font-size: 8.3pt; background: #f4f6fa; border: 1px solid #d6dbe5; padding: 8px; white-space: pre-wrap; break-inside: avoid; }}
.arqs {{ font-size: 8pt; color: #4a5568; margin-top: 2px; }}
.stat {{ font-size: 8pt; color: #2f7a4b; }}
.diag {{ width: 100%; border: 1px solid #d6dbe5; background: #fbfcfe; break-inside: avoid; margin: 6px 0; }}
.diag .t {{ font: bold 13px "DejaVu Sans"; text-anchor: middle; fill: #1d2330; }}
.diag .s {{ font: 10.5px "DejaVu Sans"; text-anchor: middle; fill: #3b4556; }}
.diag .m {{ font: 10.5px "DejaVu Sans Mono"; fill: #1d2330; }}
.diag .i {{ font-style: italic; }}
.diag .l {{ stroke: #334; stroke-width: 1.3; }}
.diag .d {{ stroke-dasharray: 5 4; }}
.diag .cls {{ fill: #fff; stroke: #334; }}
.diag .mod {{ fill: #f6f1e4; }}
.diag .ext {{ fill: #eef1f6; stroke: #334; }}
.diag .ui {{ fill: #e4effb; stroke: #2b5d9c; }}
.diag .grupo {{ fill: #f7f9fc; stroke: #8a96aa; stroke-dasharray: 4 3; }}
.diag .h {{ fill: #fff; stroke: #8a96aa; }}
.diag .h1 {{ fill: #e6f4ea; stroke: #2f7a4b; stroke-width: 2; }}
.leg {{ font-size: 9pt; color: #4a5568; margin-top: -2px; }}
.pb {{ break-before: page; }}
</style></head><body>

<section class="capa">
  <div class="sub">Engenharia de Software · Sprint 4</div>
  <h1>Analisador de Gastos Pessoais</h1>
  <div class="sub">Refatoração, padrões de projeto e diagramas</div>
  <div class="info">
    <b>Integrantes:</b> Enzo Livrari, Guilherme Rozzi, André Sheiji<br>
    <b>História 1:</b> Carregar o extrato em CSV (Enzo Livrari)<br>
    <b>Branch:</b> <code>historia-1</code>, último commit <code>{commits[0][0]}</code> ({commits[0][2]})
  </div>
</section>

<h2>1. Descrição do sistema</h2>
<p>Muita gente baixa o extrato do banco ou da fatura do cartão em planilha, mas não consegue ver direito onde o dinheiro está indo. Nosso sistema é feito para pessoas físicas, principalmente estudantes e jovens que estão começando a controlar o orçamento. A entrada é um arquivo CSV com as transações (data, descrição, categoria e valor). O sistema lê e valida o arquivo, soma os gastos por categoria e por mês, compara com limites que o usuário define e destaca as maiores despesas.</p>
<p>Segundo a Peic/CNC (Diário do Comércio, dez. 2025), 79,2% das famílias estavam endividadas em novembro de 2025, contra 77% em novembro de 2024.</p>

<h2>2. História 1: Carregar o extrato em CSV</h2>
<p><i>Como estudante que baixa o extrato do banco em planilha, quero carregar esse arquivo CSV no sistema, para não ter que digitar meus gastos um por um.</i></p>
<table><tr><th>#</th><th>Critério de aceitação</th></tr>
<tr><td>1</td><td>Um arquivo com as colunas data, descricao, categoria e valor é lido e cada linha vira uma transação.</td></tr>
<tr><td>2</td><td>A data no formato DD/MM/AAAA é convertida para data, então 05/03/2026 vira 5 de março de 2026.</td></tr>
<tr><td>3</td><td>Valores com vírgula decimal são aceitos, então 12,50 vira 12.5.</td></tr>
<tr><td>4</td><td>Se faltar alguma das quatro colunas, o sistema mostra um erro dizendo qual coluna está faltando.</td></tr>
<tr><td>5</td><td>Se o valor de uma linha não for número, o sistema mostra um erro dizendo o número da linha.</td></tr>
</table>

<h2>3. Arquitetura</h2>
<p>O sistema tem a parte de interface (<code>main.py</code> no terminal e <code>interface.py</code> com janela) e a parte de regras (<code>analisador.py</code>). As regras não fazem <code>print</code>: recebem dados, devolvem dados e lançam <code>ValueError</code> quando algo está errado. Quem mostra a mensagem para o usuário é a interface.</p>
{ARQ_SVG}
<p class="leg">Figura 1: diagrama de componentes. Em verde, a parte da história 1.</p>

<h2>4. Refatoração da História 1</h2>
<p>Na Sprint 3 (commit <code>e21e96c</code>) a leitura era uma função só, <code>ler_csv</code>. Ela passava nos testes, mas tinha alguns problemas:</p>
<table>
<tr><th>Antes</th><th>Depois</th></tr>
<tr><td>Data inválida (ex.: 31/02/2026) dava o erro do Python, em inglês e sem a linha</td><td><i>Linha 3: data inválida '31/02/2026'</i></td></tr>
<tr><td>O número da linha era contado na mão e ficava errado se tivesse linha em branco no arquivo</td><td>Usa <code>leitor.line_num</code>, que é a linha real</td></tr>
<tr><td>Arquivo vazio ou linha com campos faltando quebravam o programa (<code>TypeError</code>)</td><td>Mostram uma mensagem de erro</td></tr>
<tr><td>CSV salvo pelo Excel não achava a coluna <code>data</code> (por causa do BOM)</td><td>Abre com <code>utf-8-sig</code></td></tr>
<tr><td>CSV separado por <code>;</code> era recusado</td><td>Aceita <code>,</code> e <code>;</code></td></tr>
<tr><td><code>main()</code> era chamado direto no arquivo</td><td>Fica dentro de <code>if __name__ == "__main__"</code></td></tr>
</table>
<p>As transações continuam sendo um <code>dict</code> com <code>data</code>, <code>descricao</code>, <code>categoria</code> e <code>valor</code>, então nada muda para as histórias 2 e 3.</p>

<h2>5. Padrões de projeto</h2>
<p><b>Template Method</b> (<code>LeitorExtrato.ler</code>): a leitura sempre segue os mesmos passos (abrir o arquivo, validar as colunas e converter as linhas). A classe <code>LeitorCSV</code> só implementa o passo que muda, <code>extrair_linhas</code>.</p>
<p><b>Factory</b> (<code>criar_leitor</code>): escolhe o leitor pela extensão do arquivo usando o dicionário <code>LEITORES</code>. Se um dia o sistema for ler OFX, é só criar um <code>LeitorOFX</code> e adicionar no dicionário.</p>
{CLASSES_SVG}
<p class="leg">Figura 2: diagrama de classes da história 1.</p>

<h3>Fluxo de uma leitura</h3>
{SEQ_SVG}
<p class="leg">Figura 3: diagrama de sequência ao abrir um extrato. Seta cheia é chamada, tracejada é retorno.</p>

<h2 class="pb">6. Interface gráfica</h2>
<p>Além do terminal, a história 1 agora tem uma janela feita com tkinter (<code>interface.py</code>). O botão <b>Abrir extrato...</b> abre a seleção de arquivo, as transações aparecem numa tabela (data, descrição, categoria e valor) e embaixo aparecem a quantidade de transações e o total. Se o arquivo tiver problema, a mesma mensagem do terminal aparece numa caixa de erro. A janela usa a mesma função <code>ler_extrato</code> do <code>main.py</code>, então nenhuma regra foi duplicada.</p>
{PRINT_INTERFACE}

<h2>7. Testes e exemplos</h2>
<p>Os testes de <code>tests/test_carregar_csv.py</code> cobrem os 5 critérios de aceitação. Resultado: <b>{e(resumo_pytest)}</b>. Os testes das histórias 2 e 3 já existem, mas as funções delas ainda não foram implementadas.</p>
<p>O arquivo <code>exemplos/extrato_completo.csv</code> tem {len(demo) - 2} transações de janeiro a junho de 2026, em 9 categorias, com uma coluna a mais (<code>forma_pagamento</code>) que o leitor ignora.</p>
<pre>$ python3 main.py exemplos/extrato_completo.csv
{e(demo_txt)}</pre>
<pre>{e(erros)}</pre>

<h2 class="pb">8. Histórico de commits</h2>
<p>Branch <code>historia-1</code>, do mais recente ao mais antigo. {len(commits)} commits: {resumo_autores}.</p>
<table><tr><th style="width:62px">Commit</th><th style="width:84px">Data</th><th style="width:70px">Autor</th><th>Mensagem e arquivos</th></tr>
{linhas_commits()}
</table>

<h2>9. Como executar</h2>
<pre>python3 interface.py                                # interface gráfica (precisa do python3-tk)
python3 main.py exemplos/extrato_completo.csv       # terminal
python3 -m pytest tests/test_carregar_csv.py -v     # testes da história 1</pre>
</body></html>"""

SAIDA.write_text(pagina, encoding="utf-8")
print("ok", SAIDA)
