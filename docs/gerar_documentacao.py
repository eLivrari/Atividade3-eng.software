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
<rect x="150" y="105" width="140" height="80" rx="6" class="ui"/><text x="220" y="128" class="t">main.py (CLI)</text>
<text x="220" y="146" class="s">lê argumentos, trata</text><text x="220" y="160" class="s">erros, formata saída</text>
<rect x="330" y="20" width="370" height="265" rx="8" class="grupo"/><text x="515" y="40" class="t">analisador.py — regras de negócio</text>
<rect x="350" y="55" width="330" height="62" rx="6" class="h1"/><text x="515" y="78" class="t">Leitor de extrato — História 1</text>
<text x="515" y="96" class="s">criar_leitor() → LeitorCSV.ler() · ErroExtrato</text>
<rect x="350" y="130" width="330" height="62" rx="6" class="h"/><text x="515" y="153" class="t">Totalizador — História 2</text>
<text x="515" y="171" class="s">gastos_por_categoria() · gastos_por_mes()</text>
<rect x="350" y="205" width="330" height="62" rx="6" class="h"/><text x="515" y="228" class="t">Verificador de limites — História 3</text>
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
<rect x="240" y="10" width="250" height="120" class="cls"/>
<text x="365" y="28" class="s i">«abstract»</text><text x="365" y="44" class="t">LeitorExtrato</text>
<line x1="240" y1="52" x2="490" y2="52" class="l"/>
<text x="250" y="68" class="m">+ encoding = "utf-8-sig"</text>
<line x1="240" y1="76" x2="490" y2="76" class="l"/>
<text x="250" y="92" class="m">+ ler(caminho) : list  ⟵ template</text>
<text x="250" y="107" class="m i">+ extrair_registros(arquivo) : tuple</text>
<text x="250" y="122" class="m">+ validar_colunas(cabecalho)</text>
</g>
<g>
<rect x="240" y="200" width="250" height="60" class="cls"/>
<text x="365" y="220" class="t">LeitorCSV</text>
<line x1="240" y1="228" x2="490" y2="228" class="l"/>
<text x="250" y="248" class="m">+ extrair_registros(arquivo) : tuple</text>
</g>
<line x1="365" y1="200" x2="365" y2="132" class="l" marker-end="url(#her)"/>
<g>
<rect x="10" y="150" width="200" height="130" class="cls mod"/>
<text x="110" y="168" class="s i">«módulo analisador»</text><text x="110" y="184" class="t">Fábrica / Fachada</text>
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
<text x="20" y="320" class="s" style="text-anchor:start">Seta vazada = herança · seta tracejada = dependência. Para um novo formato (ex.: OFX),</text>
<text x="20" y="336" class="s" style="text-anchor:start">basta criar LeitorOFX(LeitorExtrato) e registrar ".ofx" em LEITORES — nada mais muda.</text>
</svg>"""

SEQ_SVG = """
<svg viewBox="0 0 720 380" class="diag" xmlns="http://www.w3.org/2000/svg">
<defs><marker id="s" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0L10,5L0,10z" fill="#334"/></marker></defs>
""" + "".join(
    f'<rect x="{x-60}" y="10" width="120" height="34" rx="4" class="cls"/><text x="{x}" y="32" class="t">{n}</text>'
    f'<line x1="{x}" y1="44" x2="{x}" y2="370" class="l d"/>'
    for x, n in [(70, "main.py"), (220, "ler_extrato"), (370, "criar_leitor"), (520, "LeitorCSV"), (660, "funções")]
) + "".join(
    f'<line x1="{a}" y1="{y}" x2="{b}" y2="{y}" class="l{" d" if r else ""}" marker-end="url(#s)"/>'
    f'<text x="{(a+b)/2}" y="{y-6}" class="s">{t}</text>'
    for a, b, y, t, r in [
        (70, 220, 75, "ler_extrato(caminho)", 0),
        (220, 370, 105, "criar_leitor(caminho)", 0),
        (370, 520, 135, "LeitorCSV()  [extensão .csv]", 0),
        (370, 220, 160, "leitor", 1),
        (220, 520, 190, "ler(caminho)  — template", 0),
        (520, 520, 0, "", 0),
        (520, 660, 280, "criar_transacao(registro, linha)", 0),
        (660, 520, 310, "transação ou ErroExtrato(\"Linha N…\")", 1),
        (520, 70, 350, "lista de transações  /  ValueError → \"Erro: …\"", 1),
    ] if a != b
) + """
<path d="M520,212 h40 v20 h-38" class="l" fill="none" marker-end="url(#s)"/><text x="566" y="226" class="s" style="text-anchor:start">extrair_registros()</text>
<path d="M520,240 h40 v20 h-38" class="l" fill="none" marker-end="url(#s)"/><text x="566" y="254" class="s" style="text-anchor:start">validar_colunas()</text>
</svg>"""

pagina = f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<title>Analisador de Gastos Pessoais — Documentação Sprint 4</title>
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
  <div class="sub">Engenharia de Software — Entrega final (Sprint 4)</div>
  <h1>Analisador de Gastos Pessoais</h1>
  <div class="sub">Refatoração, padrões de projeto aplicados e diagramas</div>
  <div class="info">
    <b>Integrantes:</b> Enzo Livrari · Guilherme Rozzi · André Sheiji<br>
    <b>Foco deste documento:</b> História 1 — Carregar o extrato em CSV (Enzo Livrari)<br>
    <b>Linguagem:</b> Python 3 · testes com pytest<br>
    <b>Branch:</b> <code>historia-1</code> · último commit <code>{commits[0][0]}</code> ({commits[0][2]})
  </div>
</section>

<h2>1. Descrição do sistema</h2>
<p>Muita gente baixa o extrato do banco ou da fatura do cartão em planilha, mas não consegue ver direito para onde o dinheiro está indo. O sistema é voltado a pessoas físicas — principalmente estudantes e jovens começando a controlar o orçamento. A entrada é um arquivo CSV com as transações (data, descrição, categoria e valor). O sistema lê e valida o arquivo, soma os gastos por categoria e por mês, compara com limites definidos pelo usuário e destaca as maiores despesas, gerando um relatório em texto (ou JSON) no terminal.</p>
<p>Motivação: segundo a Peic/CNC (Diário do Comércio, dez. 2025), 79,2% das famílias brasileiras estavam endividadas em novembro de 2025, contra 77% um ano antes. Saber para onde vai cada gasto é uma necessidade real.</p>

<h2>2. História 1 — Carregar o extrato em CSV</h2>
<p><i>Como estudante que baixa o extrato do banco em planilha, quero carregar esse arquivo CSV no sistema, para não ter que digitar meus gastos um por um.</i></p>
<table><tr><th>#</th><th>Critério de aceitação</th><th>Situação</th></tr>
<tr><td>1</td><td>Arquivo com as colunas data, descricao, categoria e valor é lido e cada linha vira uma transação.</td><td>Atendido</td></tr>
<tr><td>2</td><td>Data DD/MM/AAAA é convertida para data (05/03/2026 → 5 de março de 2026).</td><td>Atendido</td></tr>
<tr><td>3</td><td>Valores com vírgula decimal são aceitos (12,50 → 12.5).</td><td>Atendido</td></tr>
<tr><td>4</td><td>Se faltar coluna, o erro diz qual coluna está faltando.</td><td>Atendido (agora lista todas as que faltam)</td></tr>
<tr><td>5</td><td>Se o valor não for número, o erro diz o número da linha.</td><td>Atendido (também para data inválida e linha incompleta)</td></tr>
</table>

<h2>3. Arquitetura</h2>
<p>Duas camadas: a interface de terminal (<code>main.py</code>) e as regras de negócio (<code>analisador.py</code>). As regras não fazem <code>print</code> nem leem do teclado: recebem dados, devolvem dados e, em caso de problema, lançam <code>ValueError</code>. Só a CLI fala com o usuário — por isso cada regra é testável isoladamente.</p>
{ARQ_SVG}
<p class="leg">Figura 1 — Diagrama de componentes. Em verde, o componente refatorado nesta sprint.</p>

<h2>4. Refatoração da História 1</h2>
<p>A versão da Sprint 3 (<code>e21e96c</code>) tinha uma única função <code>ler_csv</code> que fazia tudo. Ela funcionava nos casos dos critérios, mas apresentava os problemas abaixo, corrigidos no commit <code>82d49bf</code>:</p>
<table>
<tr><th>Problema na versão anterior</th><th>Efeito</th><th>Correção</th></tr>
<tr><td>Data inválida (ex.: 31/02/2026) estourava o erro cru do <code>strptime</code></td><td>Mensagem em inglês e sem o número da linha</td><td><code>converter_data</code> gera <i>"Linha 3: data inválida '31/02/2026' (use DD/MM/AAAA)"</i></td></tr>
<tr><td>Contador manual de linhas (<code>numero_linha += 1</code>)</td><td>Com linha em branco no meio do arquivo, o erro apontava a linha errada</td><td>Usa <code>leitor.line_num</code>, que é a linha real do arquivo</td></tr>
<tr><td>Arquivo vazio</td><td><code>TypeError</code> (fieldnames era <code>None</code>) e o programa quebrava</td><td>Erro claro: <i>"O arquivo está vazio ou sem cabeçalho"</i></td></tr>
<tr><td>Linha com menos campos que o cabeçalho</td><td><code>TypeError</code> ao converter <code>None</code></td><td><i>"Linha 2: faltam campos (categoria, valor)"</i></td></tr>
<tr><td>Só a primeira coluna faltante era informada</td><td>Usuário corrigia uma e esbarrava na próxima</td><td>Lista todas: <i>"Estão faltando as colunas 'descricao', 'categoria'"</i></td></tr>
<tr><td>Arquivo salvo pelo Excel (UTF-8 com BOM)</td><td>A coluna <code>data</code> virava <code>\\ufeffdata</code> e era dada como faltando</td><td>Abre com <code>utf-8-sig</code></td></tr>
<tr><td>Bancos brasileiros exportam com <code>;</code></td><td>Arquivo inteiro rejeitado</td><td>Detecta o separador (<code>,</code> ou <code>;</code>) pelo cabeçalho</td></tr>
<tr><td>Cabeçalho "Data", espaços nos campos, valor "R$ 1.234,56"</td><td>Coluna não encontrada / valor inválido</td><td>Cabeçalho normalizado, campos com <code>strip()</code>, prefixo <code>R$</code> aceito</td></tr>
<tr><td>Mensagem de valor inválido mostrava o texto já alterado</td><td>"1.2,3" aparecia como "12.3"</td><td>Mostra o texto original da planilha</td></tr>
<tr><td><code>main()</code> chamado direto no módulo</td><td>Importar <code>main.py</code> (ex.: em teste) executava o programa</td><td><code>if __name__ == "__main__"</code> e código de saída 0/1</td></tr>
</table>
<p>O contrato com as Histórias 2 e 3 foi mantido: cada transação continua sendo um <code>dict</code> com <code>data</code>, <code>descricao</code>, <code>categoria</code> e <code>valor</code>, a função <code>ler_csv</code> continua existindo, e os erros continuam sendo <code>ValueError</code> (<code>ErroExtrato</code> é subclasse). Colunas extras do arquivo (ex.: <code>forma_pagamento</code>) são ignoradas.</p>

<h2>5. Padrões de projeto aplicados</h2>
<table>
<tr><th>Padrão</th><th>Onde</th><th>Por que foi usado</th></tr>
<tr><td><b>Template Method</b></td><td><code>LeitorExtrato.ler()</code></td><td>Define o passo a passo fixo da leitura — abrir o arquivo, extrair os registros, validar as colunas, converter cada linha. Só o passo <code>extrair_registros()</code> varia por formato e é implementado pelas subclasses.</td></tr>
<tr><td><b>Factory Method</b></td><td><code>criar_leitor()</code> + registro <code>LEITORES</code></td><td>Escolhe o leitor pela extensão do arquivo. A CLI não conhece as classes concretas. Para aceitar OFX, basta criar <code>LeitorOFX</code> e registrar <code>".ofx"</code> (princípio aberto/fechado).</td></tr>
<tr><td><b>Facade</b></td><td><code>ler_extrato()</code>, <code>ler_csv()</code></td><td>Quem usa (CLI, testes, Histórias 2 e 3) chama uma função e recebe a lista de transações, sem lidar com classes. <code>ler_csv</code> preserva a API da Sprint 2.</td></tr>
</table>
{CLASSES_SVG}
<p class="leg">Figura 2 — Diagrama de classes da História 1.</p>

<h3>Fluxo de uma leitura</h3>
{SEQ_SVG}
<p class="leg">Figura 3 — Diagrama de sequência de <code>python3 main.py extrato.csv</code>. Setas cheias são chamadas, tracejadas são retornos.</p>

<h2 class="pb">6. Testes</h2>
<p>Os testes em <code>tests/test_carregar_csv.py</code> especificam os critérios de aceitação (testes 1 a 5) e os casos cobertos pela refatoração. Resultado: <b>{e(resumo_pytest)}</b>.</p>
<table><tr><th>Teste</th><th>Teste</th></tr>
{"".join(f"<tr><td><code>{e(a)}</code></td><td><code>{e(b)}</code></td></tr>" for a, b in zip(testes[0::2], testes[1::2] + [""]))}
</table>
<p>Observação: <code>tests/test_totais.py</code> e <code>tests/test_limites.py</code> (Histórias 2 e 3) já especificam o comportamento, mas as funções <code>gastos_por_categoria</code>, <code>gastos_por_mes</code> e <code>verificar_limites</code> ainda não estão implementadas em <code>analisador.py</code>.</p>

<h3>Extrato de exemplo ampliado</h3>
<p><code>exemplos/extrato_completo.csv</code>: janeiro a junho de 2026, {len(demo) - 2} transações em 9 categorias (Moradia, Alimentação, Mercado, Transporte, Lazer, Saúde, Educação, Assinaturas, Vestuário), contas fixas e gastos variáveis, valores no formato brasileiro (<code>"1.200,00"</code>) e uma coluna extra <code>forma_pagamento</code> (Pix, boleto, débito, crédito), que o leitor ignora.</p>
<pre>$ python3 main.py exemplos/extrato_completo.csv
{e(demo_txt)}</pre>
<pre>{e(erros)}</pre>

<h2 class="pb">7. Histórico de commits</h2>
<p>Branch <code>historia-1</code>, do mais recente ao mais antigo. Total: {len(commits)} commits — {resumo_autores}.</p>
<table><tr><th style="width:62px">Commit</th><th style="width:84px">Data</th><th style="width:70px">Autor</th><th>Mensagem, arquivos e alterações</th></tr>
{linhas_commits()}
</table>

<h2>8. Como executar</h2>
<pre>pip install pytest
python3 -m pytest tests/test_carregar_csv.py -v     # testes da História 1
python3 main.py exemplos/extrato_completo.csv       # extrato de 6 meses
python3 main.py exemplos/extrato_sem_coluna.csv     # erro: coluna faltando
python3 main.py exemplos/extrato_valor_invalido.csv # erro: linha com valor inválido</pre>
</body></html>"""

SAIDA.write_text(pagina, encoding="utf-8")
print("ok", SAIDA)
