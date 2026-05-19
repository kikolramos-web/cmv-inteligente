import streamlit as st
import pandas as pd
import os
import json
import plotly.express as px

# =====================================================
# CONFIGURAÇÃO DA PÁGINA
# =====================================================
st.set_page_config(
    page_title="CMV Inteligente PRO",
    page_icon="🍽️",
    layout="wide"
)

# =====================================================
# CSS PREMIUM DARK
# =====================================================
st.markdown("""
<style>

/* FUNDO GERAL */
.stApp {
    background-color: #0f172a;
}

/* SIDEBAR */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #111827, #020617);
    border-right: 1px solid #1e293b;
}

[data-testid="stSidebar"] * {
    color: #f8fafc;
}

/* TITULOS */
h1 {
    color: #f8fafc;
    font-weight: 800;
    font-size: 2.8rem;
}

h2, h3 {
    color: #e2e8f0;
    font-weight: 700;
}

/* TEXTOS */
p, label, span {
    color: #cbd5e1 !important;
}

/* TABS */
.stTabs [data-baseweb="tab-list"] {
    gap: 10px;
}

.stTabs [data-baseweb="tab"] {
    background-color: #1e293b;
    color: #cbd5e1;
    border-radius: 12px;
    padding: 12px 20px;
    font-weight: 600;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(90deg, #2563eb, #3b82f6) !important;
    color: white !important;
}

/* MÉTRICAS */
div[data-testid="stMetric"] {
    background: #111827;
    border-radius: 20px;
    padding: 20px;
    border: 1px solid #1e40af;
    box-shadow: 0 4px 20px rgba(0,0,0,0.35);
}

/* LABELS */
.stTextInput label,
.stNumberInput label,
.stSelectbox label {
    color: #f8fafc !important;
    font-weight: 600;
}

/* INPUTS */
.stTextInput input,
.stNumberInput input {
    background-color: #1e293b !important;
    color: #f8fafc !important;
    border: 1px solid #334155 !important;
    border-radius: 12px !important;
}

/* SELECTBOX */
.stSelectbox div[data-baseweb="select"] {
    background-color: #1e293b !important;
    color: #f8fafc !important;
    border-radius: 12px !important;
    border: 1px solid #334155 !important;
}

/* TEXTO DOS INPUTS */
input, textarea {
    color: #f8fafc !important;
}

/* BOTÕES */
.stButton>button {
    background: linear-gradient(90deg, #2563eb, #1d4ed8);
    color: white;
    border-radius: 12px;
    border: none;
    padding: 0.7rem 1.4rem;
    font-weight: 700;
    transition: 0.3s;
}

.stButton>button:hover {
    background: linear-gradient(90deg, #3b82f6, #2563eb);
    transform: scale(1.02);
    color: white;
}

/* ALERTAS */
.stSuccess,
.stWarning,
.stError,
.stInfo {
    border-radius: 14px;
    background-color: #111827 !important;
    color: #f8fafc !important;
}

/* DATAFRAME */
[data-testid="stDataFrame"] {
    border-radius: 15px;
    overflow: hidden;
    border: 1px solid #1e293b;
}

/* TABELA */
table {
    color: white !important;
}

/* ESPAÇAMENTO */
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

/* GRÁFICOS */
.js-plotly-plot {
    border-radius: 18px;
    overflow: hidden;
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# TÍTULO
# =====================================================
st.title("🍽️ CMV Inteligente PRO")

st.markdown("""
Sistema inteligente para cálculo de CMV, análise de margem e engenharia de cardápio.
""")

# =====================================================
# ARQUIVOS
# =====================================================
ARQ_PRECOS = "base_precos.csv"
ARQ_PRATOS = "pratos.csv"

# =====================================================
# SESSION STATE
# =====================================================
if "qtd_ingredientes" not in st.session_state:
    st.session_state.qtd_ingredientes = 1

# =====================================================
# BASE PADRÃO
# =====================================================
def criar_base_padrao():

    df_init = pd.DataFrame({
        "Estado": ["DF", "SP", "RJ"],
        "Produto": ["arroz", "feijao", "frango"],
        "Preco": [5.50, 6.80, 12.00]
    })

    df_init.to_csv(ARQ_PRECOS, index=False)

    return df_init

# =====================================================
# CARREGAR BASE
# =====================================================
if not os.path.exists(ARQ_PRECOS):

    df_precos = criar_base_padrao()

else:

    try:

        df_precos = pd.read_csv(ARQ_PRECOS)

        df_precos.columns = (
            df_precos.columns
            .str.strip()
            .str.capitalize()
        )

        colunas = [
            "Estado",
            "Produto",
            "Preco"
        ]

        if not all(
            col in df_precos.columns
            for col in colunas
        ):
            df_precos = criar_base_padrao()

        if df_precos.empty:
            df_precos = criar_base_padrao()

    except:
        df_precos = criar_base_padrao()

# =====================================================
# SIDEBAR
# =====================================================
st.sidebar.title("📌 Painel")

estados = sorted(
    df_precos["Estado"].unique()
)

estado = st.sidebar.selectbox(
    "📍 Estado",
    estados
)

# =====================================================
# FILTRO
# =====================================================
df_estado = df_precos[
    df_precos["Estado"] == estado
]

produtos_lista = sorted(
    df_estado["Produto"].unique()
)

# =====================================================
# DASHBOARD SUPERIOR
# =====================================================
if os.path.exists(ARQ_PRATOS):

    try:

        df_dashboard = pd.read_csv(ARQ_PRATOS)

        if not df_dashboard.empty:

            col1, col2, col3, col4 = st.columns(4)

            col1.metric(
                "🍽️ Pratos",
                len(df_dashboard)
            )

            col2.metric(
                "📈 CMV Médio",
                f"{df_dashboard['CMV'].mean():.2f}%"
            )

            col3.metric(
                "💰 Custo Médio",
                f"R$ {df_dashboard['Custo'].mean():.2f}"
            )

            lucro_medio = (
                df_dashboard["Venda"].mean()
                -
                df_dashboard["Custo"].mean()
            )

            col4.metric(
                "🔥 Lucro Médio",
                f"R$ {lucro_medio:.2f}"
            )

    except:
        pass

# =====================================================
# TABS
# =====================================================
tab1, tab2, tab3, tab4 = st.tabs([
    "➕ Ingredientes",
    "🧾 Montagem",
    "📊 Dashboard",
    "📚 Histórico"
])

# =====================================================
# TAB INGREDIENTES
# =====================================================
with tab1:

    st.subheader("Cadastro de Ingredientes")

    col1, col2, col3 = st.columns(3)

    with col1:
        novo_produto = st.text_input("Produto")

    with col2:
        novo_preco = st.number_input(
            "Preço",
            min_value=0.0,
            format="%.2f"
        )

    with col3:
        nova_unidade = st.selectbox(
            "Unidade",
            ["kg", "g", "lt", "ml", "un"]
        )

    if st.button("Salvar Ingrediente"):

        if novo_produto.strip():

            produto_limpo = (
                novo_produto
                .strip()
                .lower()
            )

            existe = (
                (df_precos["Estado"] == estado)
                &
                (df_precos["Produto"] == produto_limpo)
            )

            if existe.any():

                df_precos.loc[
                    existe,
                    "Preco"
                ] = novo_preco

            else:

                novo = pd.DataFrame({

                    "Estado": [estado],
                    "Produto": [produto_limpo],
                    "Preco": [novo_preco]

                })

                df_precos = pd.concat(
                    [df_precos, novo],
                    ignore_index=True
                )

            df_precos.to_csv(
                ARQ_PRECOS,
                index=False
            )

            st.success("✅ Ingrediente salvo!")

            st.rerun()

# =====================================================
# TAB MONTAGEM
# =====================================================
with tab2:

    st.subheader("Montagem do Prato")

    qtd = st.number_input(
        "Quantidade de ingredientes",
        1,
        20,
        value=st.session_state.qtd_ingredientes
    )

    st.session_state.qtd_ingredientes = qtd

    ingredientes_json = []
    custos = []

    for i in range(qtd):

        st.markdown(f"### Ingrediente {i+1}")

        col1, col2, col3 = st.columns(3)

        with col1:

            produto = st.selectbox(
                f"Produto {i+1}",
                produtos_lista,
                key=f"produto_{i}"
            )

        with col2:

            quantidade = st.number_input(
                f"Quantidade {i+1}",
                min_value=0.0,
                value=1.0,
                key=f"quantidade_{i}"
            )

        with col3:

            unidade = st.selectbox(
                f"Unidade {i+1}",
                ["kg", "g", "lt", "ml", "un"],
                key=f"unidade_{i}"
            )

        preco_base = float(
            df_estado[
                df_estado["Produto"] == produto
            ]["Preco"].values[0]
        )

        custo = preco_base * quantidade

        st.info(
            f"💰 Preço Base: R$ {preco_base:.2f} | "
            f"📦 Quantidade: {quantidade} {unidade} | "
            f"➡️ Custo: R$ {custo:.2f}"
        )

        ingredientes_json.append({

            "produto": produto,
            "quantidade": quantidade,
            "unidade": unidade,
            "preco_base": preco_base,
            "custo": round(custo, 2)

        })

        custos.append(custo)

    st.subheader("📊 Resultado")

    custo_total = sum(custos)

    preco_venda = st.number_input(
        "Preço de Venda",
        min_value=0.0
    )

    cmv = (
        (custo_total / preco_venda) * 100
        if preco_venda > 0 else 0
    )

    lucro = preco_venda - custo_total

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "💵 Custo Total",
        f"R$ {custo_total:.2f}"
    )

    col2.metric(
        "📈 CMV",
        f"{cmv:.2f}%"
    )

    col3.metric(
        "🔥 Lucro",
        f"R$ {lucro:.2f}"
    )

    if custo_total > 0:

        preco_ideal = custo_total / 0.40

        st.info(
            f"💡 Preço ideal para CMV de 40%: "
            f"R$ {preco_ideal:.2f}"
        )

    if cmv > 60:
        st.error("⚠️ CMV muito alto.")

    elif cmv > 40:
        st.warning("⚠️ CMV moderado.")

    elif cmv > 0:
        st.success("🔥 Excelente margem!")

    st.subheader("💾 Salvar Prato")

    nome_prato = st.text_input(
        "Nome do prato"
    )

    if st.button("Salvar Prato"):

        if nome_prato.strip():

            novo_prato = pd.DataFrame({

                "Prato": [nome_prato],
                "Estado": [estado],
                "Ingredientes": [
                    json.dumps(ingredientes_json)
                ],
                "Custo": [
                    round(custo_total, 2)
                ],
                "Venda": [
                    round(preco_venda, 2)
                ],
                "CMV": [
                    round(cmv, 2)
                ]

            })

            if os.path.exists(ARQ_PRATOS):

                df_existente = pd.read_csv(
                    ARQ_PRATOS
                )

                df_existente = df_existente[
                    df_existente["Prato"] != nome_prato
                ]

                df_final = pd.concat(
                    [df_existente, novo_prato],
                    ignore_index=True
                )

                df_final.to_csv(
                    ARQ_PRATOS,
                    index=False
                )

            else:

                novo_prato.to_csv(
                    ARQ_PRATOS,
                    index=False
                )

            st.success(
                "✅ Prato salvo com sucesso!"
            )

# =====================================================
# TAB DASHBOARD
# =====================================================
with tab3:

    st.subheader("📊 Dashboard Executivo")

    if os.path.exists(ARQ_PRATOS):

        try:

            df_dash = pd.read_csv(
                ARQ_PRATOS
            )

            if not df_dash.empty:

                fig = px.bar(
                    df_dash,
                    x="Prato",
                    y="CMV",
                    color="CMV",
                    text="CMV",
                    template="plotly_dark",
                    title="CMV por prato"
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

                fig2 = px.pie(
                    df_dash,
                    names="Prato",
                    values="Venda",
                    hole=0.5,
                    template="plotly_dark",
                    title="Participação em vendas"
                )

                st.plotly_chart(
                    fig2,
                    use_container_width=True
                )

            else:
                st.info("Nenhum prato salvo.")

        except:
            st.warning("Erro ao carregar dashboard.")

# =====================================================
# TAB HISTÓRICO
# =====================================================
with tab4:

    st.subheader("📚 Histórico")

    if os.path.exists(ARQ_PRATOS):

        try:

            df_hist = pd.read_csv(
                ARQ_PRATOS
            )

            if not df_hist.empty:

                df_exibir = df_hist.copy()

                df_exibir["Custo"] = (
                    df_exibir["Custo"]
                    .apply(lambda x: f"R$ {x:.2f}")
                )

                df_exibir["Venda"] = (
                    df_exibir["Venda"]
                    .apply(lambda x: f"R$ {x:.2f}")
                )

                df_exibir["CMV"] = (
                    df_exibir["CMV"]
                    .apply(lambda x: f"{x:.2f}%")
                )

                st.dataframe(
                    df_exibir[
                        [
                            "Prato",
                            "Estado",
                            "Custo",
                            "Venda",
                            "CMV"
                        ]
                    ],
                    use_container_width=True
                )

            else:
                st.info("Nenhum prato salvo.")

        except:
            st.warning("Erro ao carregar histórico.")

    else:
        st.info("Nenhum histórico encontrado.")