# Sprint 2: Histórias de Usuário
## História 1: Carregar o extrato em CSV - Enzo Livrari

Como estudante que baixa o extrato do banco em planilha, quero carregar esse arquivo CSV no sistema, para não ter que digitar meus gastos um por um.

Critérios de aceitação:

1. Um arquivo com as colunas data, descricao, categoria e valor é lido e cada linha vira uma transação.
2. A data no formato DD/MM/AAAA é convertida para data, então 05/03/2026 vira 5 de março de 2026.
3. Valores com vírgula decimal são aceitos, então 12,50 vira 12.5.
4. Se faltar alguma das quatro colunas, o sistema mostra um erro dizendo qual coluna está faltando.
5. Se o valor de uma linha não for número, o sistema mostra um erro dizendo o número da linha.

## História 2: Ver quanto gastei por categoria e por mês

Como jovem começando a controlar o orçamento, quero ver o total que gastei em cada categoria e em cada mês, para entender para onde meu dinheiro está indo.

Critérios de aceitação:

1. O total de cada categoria é a soma dos valores das transações dessa categoria.
2. O total de cada mês é a soma das transações daquele mês, identificado como AAAA-MM.
3. Categorias escritas com maiúscula ou minúscula diferente contam como a mesma, Mercado e mercado por exemplo.
4. Com uma lista vazia de transações, os totais vêm vazios e o sistema não dá erro.

## História 3: Ser avisado quando passar do limite

Como usuário que define quanto pode gastar em cada categoria, quero ser avisado quando passar desse limite, para perceber antes que o gasto saia do controle.

Critérios de aceitação:

1. Uma categoria que gastou mais que o limite gera um alerta com o valor gasto, o limite e quanto passou.
2. Uma categoria que gastou exatamente o limite não gera alerta.
3. Uma categoria que não tem limite definido não gera alerta.
4. Os alertas vêm ordenados do que mais passou do limite para o que menos passou.
5. Um limite negativo é recusado com erro.

## Sobre os testes

Os testes em `tests/` especificam os critérios de aceitação de cada história. As regras ficam em `analisador.py` e a interface de terminal em `main.py` (veja `ARQUITETURA.md`).

Para rodar:

```
pip install pytest
python3 -m pytest -v
```

Para rodar só a história 1:

```
python3 -m pytest tests/test_carregar_csv.py -v
```

## Demonstração no terminal

```
python3 main.py exemplos/extrato.csv                 # História 1: carrega e lista as transações
python3 main.py exemplos/extrato_sem_coluna.csv      # História 1, critério 4: erro com a coluna que falta
python3 main.py exemplos/extrato_valor_invalido.csv  # História 1, critério 5: erro com o número da linha
```
