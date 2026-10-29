# Analisador de Gastos Pessoais

## Integrantes

- Enzo Livrari
- Guilherme Rozzi
- André Sheiji

## Descrição do sistema

Muita gente baixa o extrato do banco ou da fatura do cartão em planilha, mas não consegue ver direito onde o dinheiro está indo. Nosso sistema é feito para pessoas físicas, principalmente estudantes e jovens que estão começando a controlar o orçamento. A entrada é um arquivo CSV com as transações (data, descrição, categoria e valor). O sistema lê e valida o arquivo, soma os gastos por categoria e por mês, compara com limites que o usuário define e destaca as maiores despesas. A saída é um relatório em texto com esses resultados, também disponível em JSON. Tudo roda em Python, pelo terminal.

## Pesquisa

Referência: DIÁRIO DO COMÉRCIO. Endividamento das famílias recuou em novembro. São Paulo, dez. 2025. Matéria sobre a Pesquisa de Endividamento e Inadimplência do Consumidor (Peic), da CNC. Disponível em: diariodocomercio.com.br.

Resumo: A Peic é feita todo mês pela Confederação Nacional do Comércio e mostra quantas famílias têm dívidas a vencer, como cartão de crédito, cheque especial, carnê, consignado, empréstimo pessoal e financiamento de carro ou casa. Segundo a matéria, em novembro de 2025 eram 79,2% das famílias endividadas, contra 77% em novembro de 2024. Em outubro de 2025 o índice tinha chegado a 79,5%, o maior desde 2010. A própria pesquisa fala em forte pressão sobre o orçamento das famílias e a CNC esperava que 2025 terminasse com mais endividamento e mais inadimplência que 2024. Isso mostra que o problema é real: com quase 8 em cada 10 famílias devendo, saber para onde vai cada gasto é uma necessidade. Nosso sistema trabalha nisso, transformando um extrato difícil de ler em um relatório por categoria e por mês, com alertas quando um limite é passado.
