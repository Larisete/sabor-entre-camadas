import streamlit as st
import pandas as pd
import json
import re
from datetime import datetime, date, time, timedelta
from pathlib import Path


# ============================================================
# CONFIGURAÇÕES
# ============================================================

st.set_page_config(
    page_title="Sabor entre Camadas | Gestão de Pedidos",
    page_icon="🍰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# IDENTIDADE VISUAL - SABOR ENTRE CAMADAS
# ==========================================

st.markdown("""
<style>

/* Fundo */
.stApp {
    background-color: #FCE4EF;
    color: #6B183D;
}

/* Menu lateral */
[data-testid="stSidebar"] {
    background-color: #F8C5DC;
}

/* Títulos */
h1, h2, h3 {
    color: #6B183D !important;
    font-family: 'Trebuchet MS', sans-serif;
}

/* Botões */
.stButton > button {
    background-color: #FF1493;
    color: white !important;
    border: none;
    border-radius: 12px;
    padding: 10px 22px;
    font-weight: bold;
    transition: 0.3s;
}

.stButton > button:hover {
    background-color: #C90069;
    color: white !important;
    transform: scale(1.02);
}

/* Campos de texto */
.stTextInput input,
.stNumberInput input,
.stDateInput input,
.stTimeInput input,
.stTextArea textarea {
    background-color: white;
    color: #6B183D;
    border: 1px solid #E88AB5;
    border-radius: 10px;
}

/* Caixas de seleção */
.stSelectbox div[data-baseweb="select"] {
    background-color: white;
    border-radius: 10px;
}

/* Cartões e métricas */
div[data-testid="stMetric"] {
    background-color: white;
    border: 1px solid #F2A7C8;
    padding: 18px;
    border-radius: 15px;
}

div[data-testid="stMetricValue"] {
    color: #FF1493;
    font-weight: bold;
}

/* Divisórias */
hr {
    border-color: #E88AB5;
}

/* Links */
a {
    color: #C90069 !important;
}

</style>
""", unsafe_allow_html=True)

NOME_SISTEMA = "Sabor entre Camadas — Gestão de Pedidos"
CLIENTE = "Sabor entre Camadas"
SQUAD = "Squad de Desenvolvimento"
VERSAO = "1.0"

# Arquivo local para persistência do protótipo
ARQUIVO_PEDIDOS = Path("pedidos.json")


# ============================================================
# CATÁLOGO DE PRODUTOS
# ============================================================

PRODUTOS = {
    "Bolo de aniversário": {
        "preco": 120.00,
        "unidade": "kg",
        "pronta_entrega": False
    },
    "Bolo de chocolate": {
        "preco": 100.00,
        "unidade": "kg",
        "pronta_entrega": False
    },
    "Bolo de morango": {
        "preco": 110.00,
        "unidade": "kg",
        "pronta_entrega": False
    },
    "Bolo personalizado": {
        "preco": 150.00,
        "unidade": "kg",
        "pronta_entrega": False
    },
    "Cupcake": {
        "preco": 8.00,
        "unidade": "unidade",
        "pronta_entrega": True
    },
    "Brigadeiro": {
        "preco": 3.50,
        "unidade": "unidade",
        "pronta_entrega": True
    },
    "Beijinho": {
        "preco": 3.50,
        "unidade": "unidade",
        "pronta_entrega": True
    },
    "Brownie": {
        "preco": 8.00,
        "unidade": "unidade",
        "pronta_entrega": True
    }
}


# ============================================================
# FUNÇÕES DE PERSISTÊNCIA
# ============================================================

def carregar_pedidos():
    """Carrega os pedidos armazenados no arquivo JSON."""

    if not ARQUIVO_PEDIDOS.exists():
        return []

    try:
        with open(ARQUIVO_PEDIDOS, "r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)

        if isinstance(dados, list):
            return dados

        return []

    except (json.JSONDecodeError, OSError):
        return []


def salvar_pedidos(pedidos):
    """Salva a lista de pedidos em JSON."""

    try:
        with open(
            ARQUIVO_PEDIDOS,
            "w",
            encoding="utf-8"
        ) as arquivo:

            json.dump(
                pedidos,
                arquivo,
                ensure_ascii=False,
                indent=4
            )

        return True

    except OSError:
        return False


# ============================================================
# SESSION STATE
# ============================================================

if "pedidos" not in st.session_state:
    st.session_state.pedidos = carregar_pedidos()


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def gerar_numero_pedido():
    """Gera um número de pedido único."""

    hoje = datetime.now()

    prefixo = f"PED{hoje.strftime('%Y%m%d')}"

    pedidos_hoje = [
        pedido
        for pedido in st.session_state.pedidos
        if pedido.get("numero_pedido", "").startswith(prefixo)
    ]

    sequencia = len(pedidos_hoje) + 1

    return f"{prefixo}{sequencia:03d}"


def validar_email(email):
    """Valida formato básico de e-mail."""

    padrao = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

    return bool(re.match(padrao, email))


def validar_telefone(telefone):
    """Valida telefone brasileiro de forma simples."""

    numeros = re.sub(r"\D", "", telefone)

    return len(numeros) in (10, 11)


def calcular_limite_48h(data_agendamento, horario_agendamento):
    """Calcula o limite para alteração/cancelamento."""

    data_hora = datetime.combine(
        data_agendamento,
        horario_agendamento
    )

    return data_hora - timedelta(hours=48)


def dentro_do_prazo_48h(data_agendamento, horario_agendamento):
    """Verifica se o pedido ainda está dentro do prazo de 48 horas."""

    limite = calcular_limite_48h(
        data_agendamento,
        horario_agendamento
    )

    return datetime.now() <= limite


def formatar_moeda(valor):
    """Formata valor para padrão brasileiro."""

    return f"R$ {valor:,.2f}".replace(
        ",", "X"
    ).replace(
        ".", ","
    ).replace(
        "X", "."
    )


def calcular_valor(produto, quantidade, kilos):
    """Calcula o valor total do pedido."""

    dados_produto = PRODUTOS[produto]

    preco = dados_produto["preco"]

    if dados_produto["unidade"] == "kg":
        return preco * kilos * quantidade

    return preco * quantidade


def obter_slots_disponiveis(data_agendamento):
    """
    Retorna horários disponíveis.

    Neste protótipo os horários são simulados.
    Em uma aplicação real, eles seriam obtidos do banco
    de dados considerando pedidos já existentes.
    """

    horarios = [
        time(9, 0),    
        time(10, 0),
        time(11, 0),
        time(14, 0),
        time(15, 0),
        time(16, 0),
        time(17, 0),
        time(18, 0),
        time(19, 0)
    ]

    horarios_ocupados = []

    for pedido in st.session_state.pedidos:

        if pedido.get("status_pedido") == "CANCELADO":
            continue

        if pedido.get("data_agendamento") == data_agendamento.isoformat():

            horarios_ocupados.append(
                pedido.get("horario_agendamento")
            )

    horarios_disponiveis = []

    for horario in horarios:

        horario_str = horario.strftime("%H:%M")

        if horario_str not in horarios_ocupados:
            horarios_disponiveis.append(horario)

    return horarios_disponiveis


def processar_pedido(dados):
    """Aplica as regras de negócio para criação de pedido."""

    erros = []

    nome = dados["nome"]
    email = dados["email"]
    telefone = dados["telefone"]
    endereco = dados["endereco"]
    produto = dados["produto"]
    quantidade = dados["quantidade"]
    kilos = dados["kilos"]
    data_agendamento = dados["data_agendamento"]
    horario_agendamento = dados["horario_agendamento"]
    forma_pagamento = dados["forma_pagamento"]
    tipo_entrega = dados["tipo_entrega"]

    # --------------------------------------------------------
    # Validações
    # --------------------------------------------------------

    if not nome.strip():
        erros.append("Informe o nome do cliente.")

    if not email.strip():
        erros.append("Informe o e-mail.")

    elif not validar_email(email):
        erros.append("Informe um e-mail válido.")

    if not telefone.strip():
        erros.append("Informe o telefone.")

    elif not validar_telefone(telefone):
        erros.append("Informe um telefone válido.")

    if tipo_entrega == "Entrega" and not endereco.strip():
        erros.append("Informe o endereço para entrega.")

    if not produto:
        erros.append("Selecione um produto.")

    if quantidade <= 0:
        erros.append("A quantidade deve ser maior que zero.")

    if PRODUTOS.get(produto, {}).get("unidade") == "kg":
        if kilos <= 0:
            erros.append("Informe uma quantidade de quilos maior que zero.")

    # --------------------------------------------------------
    # Regra de 48 horas
    # --------------------------------------------------------

    data_hora_agendamento = datetime.combine(
        data_agendamento,
        horario_agendamento
    )

    limite_48h = datetime.now() + timedelta(hours=48)

    if data_hora_agendamento < limite_48h:
        erros.append(
            "O agendamento precisa ser realizado com "
            "no mínimo 48 horas de antecedência."
        )

    # --------------------------------------------------------
    # Disponibilidade
    # --------------------------------------------------------

    horarios_disponiveis = obter_slots_disponiveis(
        data_agendamento
    )

    if horario_agendamento not in horarios_disponiveis:
        erros.append(
            "O horário selecionado não está disponível."
        )

    # --------------------------------------------------------
    # Resultado
    # --------------------------------------------------------

    if erros:
        return None, erros

    valor_total = calcular_valor(
        produto,
        quantidade,
        kilos
    )

    numero_pedido = gerar_numero_pedido()

    limite_cancelamento = calcular_limite_48h(
        data_agendamento,
        horario_agendamento
    )

    status_pagamento = (
        "PAGO"
        if forma_pagamento == "PIX"
        else "PENDENTE"
    )

    pedido = {
        "cliente_marketing": CLIENTE,
        "versao_briefing": VERSAO,

        "dados_entrada_usuario": {
            "Nome": nome,
            "email": email,
            "telefone": telefone,
            "endereco": endereco,
            "produto": produto,
            "quantidade": quantidade,
            "kilos": kilos,
            "data_agendamento": data_agendamento.isoformat(),
            "horario_agendamento": horario_agendamento.strftime("%H:%M"),
            "forma_pagamento": forma_pagamento,
            "tipo_entrega": tipo_entrega,
            "observacoes": dados["observacoes"]
        },

        "dados_processados": {
            "numero_pedido": numero_pedido,
            "valor_total": valor_total,
            "status_pedido": "AGENDADO",
            "status_pagamento": status_pagamento,
            "data_limite_cancelamento":
                limite_cancelamento.strftime("%Y-%m-%d"),
            "horario_limite_cancelamento":
                limite_cancelamento.strftime("%H:%M")
        },

        "dados_saida_sistema": {
            "resultado": "PEDIDO_AGENDADO",
            "mensagem": "Pedido realizado com sucesso.",
            "data_entrega": data_agendamento.isoformat(),
            "horario_entrega":
                horario_agendamento.strftime("%H:%M"),
            "valor_total": valor_total
        },

        "criado_em": datetime.now().isoformat()
    }

    return pedido, []


# ============================================================
# CANCELAMENTO
# ============================================================

def calcular_cancelamento(pedido):
    """
    Calcula o valor da devolução conforme a regra do briefing.

    Dentro de 48h:
        devolução de 100%.

    Após o limite:
        devolução de 50%.
    """

    dados_processados = pedido["dados_processados"]

    valor = float(
        dados_processados["valor_total"]
    )

    data_agendamento = datetime.strptime(
        pedido["dados_entrada_usuario"]["data_agendamento"],
        "%Y-%m-%d"
    ).date()

    horario_agendamento = datetime.strptime(
        pedido["dados_entrada_usuario"]["horario_agendamento"],
        "%H:%M"
    ).time()

    limite = calcular_limite_48h(
        data_agendamento,
        horario_agendamento
    )

    agora = datetime.now()

    if agora <= limite:

        percentual_devolucao = 1.0
        taxa = 0.0

    else:

        percentual_devolucao = 0.5
        taxa = 0.5

    devolucao = valor * percentual_devolucao

    return {
        "valor_original": valor,
        "taxa": valor * taxa,
        "percentual_devolucao":
            percentual_devolucao * 100,
        "valor_devolucao": devolucao
    }


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.image(
        "https://cdn-icons-png.flaticon.com/512/3081/3081840.png",
        width=80
    )

    st.title("🍰 Sabor entre Camadas")

    st.caption("Sistema de Gestão de Pedidos")

    st.divider()

    st.markdown("### 👥 Squad")

    st.write(f"**Equipe:** {SQUAD}")

    st.write("**Versão:** 1.0")

    st.divider()

    st.markdown("### 🏢 Cliente")

    st.write(f"**Empresa:** {CLIENTE}")

    st.write(
        "**Segmento:** Marketing / Alimentação"
    )

    st.divider()

    st.markdown("### 📌 Regras")

    st.info(
        """
        **Agendamento**
        
        Mínimo de 48 horas de antecedência.
        
        **Cancelamento**
        
        • Dentro do prazo: 100% de devolução
        
        • Após o prazo: 50% de devolução
        """
    )


# ============================================================
# CABEÇALHO
# ============================================================

st.title("🍰 Sabor entre Camadas")

st.subheader("Sistema de Gestão de Pedidos")

st.markdown(
    "Protótipo desenvolvido com **Python + Streamlit** "
    "para gerenciamento de pedidos, agendamentos e vendas."
)

st.divider()


# ============================================================
# MÉTRICAS
# ============================================================

pedidos = st.session_state.pedidos

pedidos_validos = [
    pedido
    for pedido in pedidos
    if pedido.get("dados_processados", {}).get(
        "status_pedido"
    ) != "CANCELADO"
]

vendas_total = sum(
    pedido.get("dados_processados", {}).get(
        "valor_total",
        0
    )
    for pedido in pedidos_validos
)

pedidos_agendados = len(pedidos_validos)

pedidos_cancelados = len([
    pedido
    for pedido in pedidos
    if pedido.get("dados_processados", {}).get(
        "status_pedido"
    ) == "CANCELADO"
])

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "📦 Pedidos",
    pedidos_agendados
)

col2.metric(
    "💰 Vendas",
    formatar_moeda(vendas_total)
)

col3.metric(
    "❌ Cancelados",
    pedidos_cancelados
)

col4.metric(
    "🍰 Produtos",
    len(PRODUTOS)
)


# ============================================================
# ABAS
# ============================================================

aba_novo, aba_produtos, aba_pedidos, aba_cancelamento, aba_relatorio = st.tabs(
    [
        "➕ Novo Pedido",
        "🍰 Produtos",
        "📦 Pedidos",
        "❌ Cancelamento",
        "📊 Relatório"
    ]
)


# ============================================================
# ABA — NOVO PEDIDO
# ============================================================

with aba_novo:

    st.header("Novo Pedido")

    st.write(
        "Preencha os dados abaixo para realizar um novo "
        "agendamento."
    )

    with st.form("form_novo_pedido"):

        st.subheader("👤 Dados do Cliente")

        col1, col2 = st.columns(2)

        with col1:

            nome = st.text_input(
                "Nome *",
                placeholder="Nome completo"
            )

            email = st.text_input(
                "E-mail *",
                placeholder="cliente@email.com"
            )

            telefone = st.text_input(
                "Telefone *",
                placeholder="(61) 99999-9999"
            )

        with col2:

            endereco = st.text_area(
                "Endereço",
                placeholder="Informe o endereço para entrega"
            )

            tipo_entrega = st.selectbox(
                "Tipo de atendimento *",
                [
                    "Entrega",
                    "Retirada"
                ]
            )

        st.divider()

        st.subheader("🍰 Dados do Pedido")

        col1, col2 = st.columns(2)

        with col1:

            produto = st.selectbox(
                "Produto *",
                list(PRODUTOS.keys())
            )

            quantidade = st.number_input(
                "Quantidade *",
                min_value=1,
                value=1,
                step=1
            )

        with col2:

            unidade_produto = PRODUTOS[produto]["unidade"]

            if unidade_produto == "kg":

                kilos = st.number_input(
                    "Quilos *",
                    min_value=0.5,
                    value=1.0,
                    step=0.5
                )

            else:

                kilos = 0.0

                st.number_input(
                    "Quilos",
                    value=0.0,
                    disabled=True
                )

        st.divider()

        st.subheader("📅 Agendamento")

        data_minima = (
            datetime.now() + timedelta(hours=48)
        ).date()

        data_agendamento = st.date_input(
            "Data desejada *",
            min_value=data_minima,
            value=data_minima
        )

        horarios_disponiveis = obter_slots_disponiveis(
            data_agendamento
        )

        if horarios_disponiveis:

            horarios_formatados = [
                horario.strftime("%H:%M")
                for horario in horarios_disponiveis
            ]

            horario_selecionado = st.selectbox(
                "Horário disponível *",
                horarios_formatados
            )

            horario_agendamento = datetime.strptime(
                horario_selecionado,
                "%H:%M"
            ).time()

        else:

            horario_agendamento = None

            st.warning(
                "Não existem horários disponíveis "
                "para esta data."
            )

        st.divider()

        st.subheader("💳 Pagamento")

        forma_pagamento = st.selectbox(
            "Forma de pagamento *",
            [
                "PIX",
                "Cartão de crédito",
                "Cartão de débito",
                "Dinheiro"
            ]
        )

        observacoes = st.text_area(
            "Observações",
            placeholder=(
                "Ex.: Bolo de chocolate com decoração azul"
            )
        )

        st.divider()

        enviar = st.form_submit_button(
            "✅ Confirmar Pedido",
            use_container_width=True
        )

    # --------------------------------------------------------
    # PROCESSAMENTO
    # --------------------------------------------------------

    if enviar:

        if horario_agendamento is None:

            st.error(
                "Não é possível realizar o pedido "
                "sem um horário disponível."
            )

        else:

            dados = {
                "nome": nome,
                "email": email,
                "telefone": telefone,
                "endereco": endereco,
                "produto": produto,
                "quantidade": quantidade,
                "kilos": kilos,
                "data_agendamento": data_agendamento,
                "horario_agendamento": horario_agendamento,
                "forma_pagamento": forma_pagamento,
                "tipo_entrega": tipo_entrega,
                "observacoes": observacoes
            }

            pedido, erros = processar_pedido(dados)

            if erros:

                st.error(
                    "Não foi possível realizar o pedido."
                )

                for erro in erros:
                    st.warning(f"⚠️ {erro}")

            else:

                st.session_state.pedidos.append(
                    pedido
                )

                salvar_pedidos(
                    st.session_state.pedidos
                )

                st.success(
                    "🎉 Pedido realizado com sucesso!"
                )

                st.subheader(
                    "Resumo do Pedido"
                )

                dados_processados = pedido[
                    "dados_processados"
                ]

                c1, c2, c3 = st.columns(3)

                c1.metric(
                    "Número do Pedido",
                    dados_processados[
                        "numero_pedido"
                    ]
                )

                c2.metric(
                    "Valor Total",
                    formatar_moeda(
                        dados_processados[
                            "valor_total"
                        ]
                    )
                )

                c3.metric(
                    "Pagamento",
                    dados_processados[
                        "status_pagamento"
                    ]
                )

                st.info(
                    f"""
                    **Data:** {data_agendamento.strftime('%d/%m/%Y')}
                    
                    **Horário:** {horario_agendamento.strftime('%H:%M')}
                    
                    **Atendimento:** {tipo_entrega}
                    """
                )

                # JSON
                st.subheader(
                    "📄 Registro JSON"
                )

                st.json(pedido)

                st.download_button(
                    label="⬇️ Baixar pedido em JSON",
                    data=json.dumps(
                        pedido,
                        ensure_ascii=False,
                        indent=4
                    ),
                    file_name=(
                        f"{dados_processados['numero_pedido']}.json"
                    ),
                    mime="application/json"
                )


# ============================================================
# ABA — PRODUTOS
# ============================================================

with aba_produtos:

    st.header("🍰 Produtos Disponíveis")

    st.write(
        "Catálogo de produtos cadastrados no sistema."
    )

    produtos_tabela = []

    for nome_produto, dados in PRODUTOS.items():

        produtos_tabela.append(
            {
                "Produto": nome_produto,
                "Preço": formatar_moeda(
                    dados["preco"]
                ),
                "Unidade": dados["unidade"],
                "Pronta entrega":
                    "Sim"
                    if dados["pronta_entrega"]
                    else "Não"
            }
        )

    df_produtos = pd.DataFrame(
        produtos_tabela
    )

    st.dataframe(
        df_produtos,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    st.subheader("⚡ Produtos à Pronta Entrega")

    pronta_entrega = [
        produto
        for produto, dados in PRODUTOS.items()
        if dados["pronta_entrega"]
    ]

    if pronta_entrega:

        cols = st.columns(4)

        for i, produto_nome in enumerate(
            pronta_entrega
        ):

            produto_dados = PRODUTOS[
                produto_nome
            ]

            with cols[i % 4]:

                st.info(
                    f"""
                    ### {produto_nome}
                    
                    **{formatar_moeda(produto_dados['preco'])}**
                    
                    Unidade: {produto_dados['unidade']}
                    """
                )


# ============================================================
# ABA — PEDIDOS
# ============================================================

with aba_pedidos:

    st.header("📦 Pedidos Cadastrados")

    if not st.session_state.pedidos:

        st.info(
            "Nenhum pedido cadastrado ainda."
        )

    else:

        dados_tabela = []

        for pedido in st.session_state.pedidos:

            entrada = pedido[
                "dados_entrada_usuario"
            ]

            processado = pedido[
                "dados_processados"
            ]

            dados_tabela.append(
                {
                    "Pedido":
                        processado["numero_pedido"],

                    "Cliente":
                        entrada["Nome"],

                    "Produto":
                        entrada["produto"],

                    "Data":
                        entrada["data_agendamento"],

                    "Horário":
                        entrada["horario_agendamento"],

                    "Valor":
                        formatar_moeda(
                            processado["valor_total"]
                        ),

                    "Pedido":
                        processado["status_pedido"],

                    "Pagamento":
                        processado["status_pagamento"]
                }
            )

        df_pedidos = pd.DataFrame(
            dados_tabela
        )

        st.dataframe(
            df_pedidos,
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        st.subheader("🔎 Detalhes do Pedido")

        numeros_pedidos = [
            pedido[
                "dados_processados"
            ]["numero_pedido"]
            for pedido in st.session_state.pedidos
        ]

        pedido_selecionado = st.selectbox(
            "Selecione um pedido",
            numeros_pedidos
        )

        pedido_detalhes = next(
            (
                pedido
                for pedido in st.session_state.pedidos
                if pedido[
                    "dados_processados"
                ]["numero_pedido"] == pedido_selecionado
            ),
            None
        )

        if pedido_detalhes:

            entrada = pedido_detalhes[
                "dados_entrada_usuario"
            ]

            processado = pedido_detalhes[
                "dados_processados"
            ]

            col1, col2 = st.columns(2)

            with col1:

                st.write(
                    f"**Cliente:** {entrada['Nome']}"
                )

                st.write(
                    f"**E-mail:** {entrada['email']}"
                )

                st.write(
                    f"**Telefone:** {entrada['telefone']}"
                )

                st.write(
                    f"**Produto:** {entrada['produto']}"
                )

                st.write(
                    f"**Quantidade:** {entrada['quantidade']}"
                )

            with col2:

                st.write(
                    f"**Data:** {entrada['data_agendamento']}"
                )

                st.write(
                    f"**Horário:** {entrada['horario_agendamento']}"
                )

                st.write(
                    f"**Pagamento:** {processado['status_pagamento']}"
                )

                st.write(
                    f"**Status:** {processado['status_pedido']}"
                )

                st.write(
                    f"**Valor:** "
                    f"{formatar_moeda(processado['valor_total'])}"
                )

            st.write(
                f"**Observações:** "
                f"{entrada.get('observacoes', '-')}"
            )

            st.download_button(
                "⬇️ Exportar pedido JSON",
                data=json.dumps(
                    pedido_detalhes,
                    ensure_ascii=False,
                    indent=4
                ),
                file_name=f"{pedido_selecionado}.json",
                mime="application/json"
            )


# ============================================================
# ABA — CANCELAMENTO
# ============================================================

with aba_cancelamento:

    st.header("❌ Cancelamento de Pedido")

    if not st.session_state.pedidos:

        st.info(
            "Não existem pedidos para cancelar."
        )

    else:

        pedidos_ativos = [
            pedido
            for pedido in st.session_state.pedidos
            if pedido[
                "dados_processados"
            ]["status_pedido"] != "CANCELADO"
        ]

        if not pedidos_ativos:

            st.info(
                "Não existem pedidos ativos."
            )

        else:

            numeros = [
                pedido[
                    "dados_processados"
                ]["numero_pedido"]
                for pedido in pedidos_ativos
            ]

            numero_cancelamento = st.selectbox(
                "Pedido para cancelar",
                numeros
            )

            pedido_cancelar = next(
                pedido
                for pedido in pedidos_ativos
                if pedido[
                    "dados_processados"
                ]["numero_pedido"]
                == numero_cancelamento
            )

            entrada = pedido_cancelar[
                "dados_entrada_usuario"
            ]

            st.info(
                f"""
                **Cliente:** {entrada['Nome']}
                
                **Produto:** {entrada['produto']}
                
                **Data:** {entrada['data_agendamento']}
                
                **Horário:** {entrada['horario_agendamento']}
                """
            )

            calculo = calcular_cancelamento(
                pedido_cancelar
            )

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "Valor pago",
                formatar_moeda(
                    calculo["valor_original"]
                )
            )

            col2.metric(
                "Devolução",
                formatar_moeda(
                    calculo["valor_devolucao"]
                )
            )

            col3.metric(
                "Taxa",
                formatar_moeda(
                    calculo["taxa"]
                )
            )

            if calculo[
                "percentual_devolucao"
            ] == 100:

                st.success(
                    "Cancelamento dentro do prazo de 48 horas. "
                    "O cliente receberá 100% do valor."
                )

            else:

                st.warning(
                    "Cancelamento após o prazo de 48 horas. "
                    "Será aplicada uma taxa de 50%, "
                    "com devolução dos 50% restantes."
                )

            confirmar = st.checkbox(
                "Confirmo o cancelamento deste pedido."
            )

            if st.button(
                "❌ Cancelar Pedido",
                disabled=not confirmar,
                use_container_width=True
            ):

                pedido_cancelar[
                    "dados_processados"
                ]["status_pedido"] = "CANCELADO"

                pedido_cancelar[
                    "dados_processados"
                ]["status_pagamento"] = (
                    "DEVOLUÇÃO PROCESSADA"
                )

                pedido_cancelar[
                    "dados_processados"
                ]["valor_devolucao"] = (
                    calculo["valor_devolucao"]
                )

                pedido_cancelar[
                    "dados_processados"
                ]["taxa_cancelamento"] = (
                    calculo["taxa"]
                )

                salvar_pedidos(
                    st.session_state.pedidos
                )

                st.success(
                    "Pedido cancelado com sucesso!"
                )

                st.rerun()


# ============================================================
# ABA — RELATÓRIO
# ============================================================

with aba_relatorio:

    st.header("📊 Relatório de Vendas")

    if not st.session_state.pedidos:

        st.info(
            "Ainda não existem vendas registradas."
        )

    else:

        registros = []

        for pedido in st.session_state.pedidos:

            entrada = pedido[
                "dados_entrada_usuario"
            ]

            processado = pedido[
                "dados_processados"
            ]

            if processado[
                "status_pedido"
            ] == "CANCELADO":
                continue

            registros.append(
                {
                    "Pedido":
                        processado["numero_pedido"],

                    "Cliente":
                        entrada["Nome"],

                    "Produto":
                        entrada["produto"],

                    "Data":
                        entrada["data_agendamento"],

                    "Horário":
                        entrada["horario_agendamento"],

                    "Forma de pagamento":
                        entrada["forma_pagamento"],

                    "Valor":
                        processado["valor_total"],

                    "Status":
                        processado["status_pedido"]
                }
            )

        if not registros:

            st.info(
                "Não existem vendas válidas para o relatório."
            )

        else:

            df = pd.DataFrame(registros)

            df["Data"] = pd.to_datetime(
                df["Data"]
            )

            # ------------------------------------------------
            # FILTROS
            # ------------------------------------------------

            st.subheader("🔎 Filtros")

            col1, col2 = st.columns(2)

            with col1:

                tipo_periodo = st.selectbox(
                    "Consultar por",
                    [
                        "Dia",
                        "Mês",
                        "Ano",
                        "Todos"
                    ]
                )

            with col2:

                if tipo_periodo == "Dia":

                    data_filtro = st.date_input(
                        "Selecione o dia",
                        value=date.today()
                    )

                elif tipo_periodo == "Mês":

                    data_filtro = st.date_input(
                        "Selecione um mês",
                        value=date.today()
                    )

                elif tipo_periodo == "Ano":

                    ano_filtro = st.number_input(
                        "Ano",
                        min_value=2020,
                        max_value=2100,
                        value=datetime.now().year
                    )

                else:

                    data_filtro = None

            # ------------------------------------------------
            # APLICA FILTRO
            # ------------------------------------------------

            df_filtrado = df.copy()

            if tipo_periodo == "Dia":

                df_filtrado = df[
                    df["Data"].dt.date
                    == data_filtro
                ]

            elif tipo_periodo == "Mês":

                df_filtrado = df[
                    (df["Data"].dt.year
                     == data_filtro.year)
                    &
                    (df["Data"].dt.month
                     == data_filtro.month)
                ]

            elif tipo_periodo == "Ano":

                df_filtrado = df[
                    df["Data"].dt.year
                    == ano_filtro
                ]

            # ------------------------------------------------
            # MÉTRICAS
            # ------------------------------------------------

            quantidade_vendas = len(
                df_filtrado
            )

            faturamento = df_filtrado[
                "Valor"
            ].sum()

            ticket_medio = (
                faturamento / quantidade_vendas
                if quantidade_vendas > 0
                else 0
            )

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "📦 Vendas",
                quantidade_vendas
            )

            col2.metric(
                "💰 Faturamento",
                formatar_moeda(faturamento)
            )

            col3.metric(
                "🧾 Ticket médio",
                formatar_moeda(ticket_medio)
            )

            st.divider()

            # ------------------------------------------------
            # TABELA
            # ------------------------------------------------

            tabela_relatorio = df_filtrado.copy()

            tabela_relatorio["Data"] = (
                tabela_relatorio["Data"]
                .dt.strftime("%d/%m/%Y")
            )

            tabela_relatorio["Valor"] = (
                tabela_relatorio["Valor"]
                .apply(formatar_moeda)
            )

            st.dataframe(
                tabela_relatorio,
                use_container_width=True,
                hide_index=True
            )

            # ------------------------------------------------
            # GRÁFICO
            # ------------------------------------------------

            if not df_filtrado.empty:

                st.subheader(
                    "📈 Vendas por período"
                )

                vendas_periodo = (
                    df_filtrado
                    .groupby(
                        df_filtrado["Data"]
                        .dt.date
                    )["Valor"]
                    .sum()
                )

                st.bar_chart(
                    vendas_periodo
                )

            # ------------------------------------------------
            # EXPORTAÇÃO
            # ------------------------------------------------

            st.divider()

            csv = df_filtrado.to_csv(
                index=False
            ).encode("utf-8")

            st.download_button(
                "⬇️ Exportar relatório CSV",
                data=csv,
                file_name="relatorio_vendas.csv",
                mime="text/csv"
            )


# ============================================================
# RODAPÉ
# ============================================================

st.divider()

st.caption(
    f"{NOME_SISTEMA} | "
    f"Cliente: {CLIENTE} | "
    f"Versão {VERSAO}"
)
