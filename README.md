MODELO DE BRIEFING & DESCOBERTA DE PRODUTO
Alinhamento Estratégico: Turma de Marketing de Empresas & Ciência de Dados / Dev

Identificação da Squad: Sweet Code
Empresa / Cliente (Marketing): Sabor entre camadas (S&C)
Integrantes de Marketing (Stakeholders): Ana Paula,Érica, Daniele
Integrantes de Ciência de Dados / Dev: Lúcia, Maria Eduarda, Larissa
Data do Alinhamento: 22/09/2026

1. Contexto e Problema de Negócio (Business Discovery)
Visão Geral da Empresa:
A empresa atua no ramo de confeitaria tradicional e fit. Produz e confecciona bolos caseiros e de
aniversário, trufas, tortas salgadas e outros produtos de confeitaria.
O público-alvo é a comunidade em geral, atendendo clientes que desejam produtos para consumo
próprio, comemorações, aniversários e outras ocasiões especiais.

A Dor Principal (Gargalo de Marketing/Vendas):
A principal dificuldade atual da empresa é a perda de tempo com agendamentos, principalmente
devido à necessidade de organizar os pedidos, verificar datas disponíveis e controlar o prazo necessário
para produção dos produtos.
Esse problema é ainda mais relevante para bolos de aniversário e produtos personalizados, que
precisam de tempo para produção, decoração e organização da entrega ou retirada.

Objetivo Esperado:
Desenvolver um aplicativo para visualização de produtos, realização de pedidos, agendamentos e
controle de pagamentos, facilitando e tornando mais rápido o atendimento ao cliente.
A ferramenta deverá contribuir para:
Facilitar o agendamento de encomendas;
Organizar os pedidos da empresa;
Mostrar as datas e horários disponíveis;
Apresentar produtos à pronta entrega;
Facilitar o controle dos pagamentos;
Aumentar a praticidade do atendimento;
Contribuir para o aumento das vendas;
Melhorar a visualização dos produtos oferecidos pela empresa.
2. A Solução Proposta (Product Vision)
Nome do Conceito da Ferramenta:
Catálogo e Sistema de Agendamento — Sabor entre Camadas
Descrição Breve (Elevator Pitch):
A ferramenta facilita o agendamento de encomendas, permitindo que o cliente visualize os produtos,
consulte datas disponíveis e realize seu pedido de forma rápida e organizada.

O sistema também auxilia a empresa no controle dos pedidos, pagamentos e disponibilidade de datas,
considerando o prazo mínimo necessário para a produção dos produtos personalizados.
Usuário Final Principal:
( x) O próprio cliente final da empresa
( x ) A equipe interna de Marketing/Vendas
3. Engenharia de Requisitos (Escopo do Protótipo)
Requisitos Funcionais (O que o sistema DEVE FAZER):
RF01 — Cadastro e visualização
O sistema deve permitir que o usuário informe:
Nome;
E-mail;
Telefone;
Endereço;
Forma de pagamento;
Produto desejado;
Quantidade;
Kilos;
Data e horário desejados;
Observações do pedido.
Solicitar entrega ou retirada do produto;
O sistema também deverá permitir que o usuário visualize os produtos disponíveis.
RF02 — Agendamento com antecedência mínima
O sistema deve permitir que o usuário realize agendamentos com no mínimo 48 horas de
antecedência em relação à data e horário desejados para entrega ou retirada.
Essa regra é necessária porque alguns produtos, principalmente bolos de aniversário e produtos
personalizados, precisam de tempo para produção, decoração e organização da entrega.
RF03 — Disponibilidade de datas e horários
O sistema deve apresentar ao cliente somente as datas e horários disponíveis para novos pedidos e
agendamentos.
RF04 — Alteração do pedido
O sistema deve permitir que o usuário edite o pedido, incluindo produtos, quantidade, data, horário e
observações, desde que a alteração seja realizada dentro do prazo mínimo de 48 horas de
antecedência.
RF05 — Cancelamento
O sistema deve permitir o cancelamento do pedido dentro do prazo mínimo de 48 horas de
antecedência.
Caso o cancelamento seja realizado dentro do prazo estabelecido, o sistema deverá processar a
devolução do valor pago conforme a política definida pela empresa.
Após o prazo de 48 horas, será aplicada uma taxa de 50% sobre o valor pago, sendo os 50%
restantes devolvidos ao usuário.
RF06 — Produtos à pronta entrega
O sistema deve permitir a visualização dos produtos disponíveis para pronta entrega.

RF07 — Pagamento
O sistema deve permitir o registro da forma de pagamento escolhida pelo cliente e apresentar o status
do pagamento.
RF08 — Relatório de vendas
O sistema deve apresentar um relatório final contendo as vendas realizadas, permitindo a consulta por:
Dia;
Mês;
Ano.
Requisitos Não-Funcionais (Restrições e Qualidade):
RNF01 — Formato de Troca
A comunicação e a troca de informações entre as partes do sistema deverão utilizar a estrutura JSON.
RNF02 — Usabilidade
A interface deverá ser simples, clara e intuitiva, permitindo que usuários com diferentes níveis de
conhecimento tecnológico consigam utilizar o sistema.
RNF03 — Identidade Visual
A interface deverá utilizar como cores principais:
Azul-claro
Branco

4. Mapeamento de Dados & Schema JSON (Para os Devs)
Definam os campos obrigatórios que o sistema receberá do Marketing (Entrada) e o que o sistema
retornará após o processamento (Saída):
{
"cliente_marketing": "Sabor entre Camadas",
"versao_briefing": "1.0",
"dados_entrada_usuario": {
"Nome": "Nome do Cliente",
"email": "email@exemplo.com",
"telefone": "(61) 99999-9999",
"endereco": "Endereço do cliente",
"produto": "Bolo de aniversário",
"quantidade": 1,
"data_agendamento": "2026-09-25",
"horario_agendamento": "18:00",
"forma_pagamento": "PIX",
"observacoes": "Bolo de chocolate com decoração azul"
},
"dados_processados": {
"numero_pedido": "PED20260925001",
"valor_total": 120.00,
"status_pedido": "AGENDADO",
"status_pagamento": "PAGO",
"data_limite_cancelamento": "2026-09-23",

"horario_limite_cancelamento": "18:00"
},
"dados_saida_sistema": {
"resultado": "PEDIDO_AGENDADO",
"mensagem": "Pedido realizado com sucesso.",
"data_entrega": "2026-09-25",
"horario_entrega": "18:00",
"valor_total": 120.00
}
}

5. Critérios de Aceite do Marketing (Definition of Done - DoD)
[ ] O formulário/API funcionando sem erros de digitação ou execução.
[ ] A classificação/cálculo correto com base na regra de negócio alinhada hoje.
[ ] Os dados salvos e versionados no repositório do GitHub da squad.

6. Regras de Negócio
RN01 — Antecedência do pedido
Todos os pedidos deverão ser realizados com no mínimo 48 horas de antecedência da
data e horário desejados para entrega ou retirada.
RN02 — Produção dos produtos
O prazo mínimo de 48 horas existe devido ao tempo necessário para produção, preparação e
decoração dos produtos, principalmente bolos de aniversário e encomendas personalizadas.
RN03 — Disponibilidade
O sistema deverá permitir o agendamento somente quando houver disponibilidade de data e
horário para atendimento.
RN04 — Alteração
O cliente poderá alterar o pedido desde que a solicitação seja realizada com pelo menos 48
horas de antecedência.
RN05 — Cancelamento
O cliente poderá cancelar o pedido dentro do prazo mínimo de 48 horas de antecedência.
RN06 — Cancelamento após o prazo
Caso o cancelamento ocorra após o prazo de 48 horas, será aplicada uma taxa de 50%
sobre o valor pago, sendo devolvidos os 50% restantes ao cliente.
RN07 — Pronta entrega
Produtos classificados como pronta entrega poderão possuir regras de disponibilidade
diferentes dos produtos personalizados, conforme a capacidade da empresa.
RN08 — Relatórios
As vendas deverão ser armazenadas de maneira que seja possível gerar relatórios por dia,
mês e ano.
