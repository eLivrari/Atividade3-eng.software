# Sprint 2: Histórias de Usuário
## História 1: Carregar o extrato em CSV - Enzo Livrari

Como estudante que baixa o extrato do banco em planilha, quero carregar esse arquivo CSV no sistema, para não ter que digitar meus gastos um por um.

Critérios de aceitação:

1. Um arquivo com as colunas data, descricao, categoria e valor é lido e cada linha vira uma transação.
2. A data no formato DD/MM/AAAA é convertida para data, então 05/03/2026 vira 5 de março de 2026.
3. Valores com vírgula decimal são aceitos, então 12,50 vira 12.5.
4. Se faltar alguma das quatro colunas, o sistema mostra um erro dizendo qual coluna está faltando.
5. Se o valor de uma linha não for número, o sistema mostra um erro dizendo o número da linha.
