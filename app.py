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

/* FUNDO */
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

/* TÍTULOS */
h1 {
    color: #f8fafc;
    font-weight: 800;
}

h2, h3 {
    color: #e2e8f0;
}

/* TEXTOS */
p, label, span {
    color: #cbd5e1 !important;
}

/* TABS */
.stTabs [data-baseweb="tab"] {
    background-color: #1e293b;
    color: #cbd5e1;
    border-radius: 12px;
    padding: 10px 18px;
    font-weight: 600;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(90deg, #2563eb, #3b82f6) !important;
    color: white !important;
}

/* INPUTS */
.stTextInput input,
.stNumberInput input {
    background-color: #1e293b !important;
    color: white !important;
    border-radius: 12px !important;
}

/* SELECTBOX */
.stSelectbox div[data-baseweb="select"] {
    background-color: #1e293b !important;
    border-radius: 12px !important;
}

/* BOTÕES */
.stButton>button {
    background: linear-gradient(90deg, #2563eb, #1d4ed8);
    color: white;
    border-radius: 12px;
    border: none;
    padding: 0.7rem 1.4rem;
    font-weight: 700;
}

.stButton>button:hover {
    transform: scale(1.02);
}

/* MÉTRICAS */
div[data-testid="stMetric"] {
    background: #111827;
    border-radius: 18px;
    padding: 20px;
    border: 1px solid #1e40af;
}

/* DATAFRAME */
[data-testid="stDataFrame"] {
    border-radius: 14px;
    overflow: hidden;
}

/* ESPAÇAMENTO */
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# TÍTULO
# =====================================================

st.title("🍽️ CMV Inteligente PRO")

st.markdown("""
Sistema inteligente para cálculo de CMV, margem e engenharia de cardápio.
""")

# =====================================================
# ARQUIVOS
# =====================================================

ARQ_RESTAURANTES = "restaurantes.csv"
ARQ_PRODUTOS = "produtos.csv"
ARQ_PRATOS = "pratos.csv"

# =====================================================
# FUNÇÕES
# =====================================================

def carregar_csv(arquivo, colunas):

    if os.path.exists(arquivo):

        try:
            df = pd.read_csv(arquivo)

            if not df.empty:
                return df

        except:
            pass

    return pd.DataFrame(columns=colunas)

# =====================================================
# BASES
# =====================================================

df_restaurantes = carregar_csv(
    ARQ_RESTAURANTES,
    ["Restaurante"]
)

df_produtos = carregar_csv(
    ARQ_PRODUTOS,
    ["Produto", "Categoria", "Unidade", "Preco"]
)

df_pratos = carregar_csv(
    ARQ_PRATOS,
    [
        "Restaurante",
        "Prato",
        "Ingredientes",
        "Custo",
        "Venda",
        "Lucro",
        "CMV"
    ]
)

# =====================================================
# SIDEBAR
# =====================================================

st.sidebar.title("📌 Painel")

lista_restaurantes = []

if not df_restaurantes.empty:
    lista_restaurantes = sorted(
        df_restaurantes["Restaurante"].unique()
    )

if lista_restaurantes:

    restaurante_selecionado = st.sidebar.selectbox(
        "🍽️ Restaurante",
        lista_restaurantes
    )

else:

    restaurante_selecionado = None

    st.sidebar.warning(
        "Cadastre um restaurante."
    )

# =====================================================
# DASHBOARD SUPERIOR
# =====================================================

if not df_pratos.empty:

    if restaurante_selecionado:

        df_dashboard = df_pratos[
            df_pratos["Restaurante"]
            ==
            restaurante_selecionado
        ]

    else:

        df_dashboard = df_pratos

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

        col4.metric(
            "🔥 Lucro Médio",
            f"R$ {df_dashboard['Lucro'].mean():.2f}"
        )

# =====================================================
# TABS
# =====================================================

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏢 Restaurantes",
    "📦 Produtos",
    "🍽️ Montagem",
    "📊 Dashboard",
    "📚 Histórico"
])

# =====================================================
# TAB RESTAURANTES
# =====================================================

with tab1:

    st.subheader("Cadastro de Restaurantes")

    novo_restaurante = st.text_input(
        "Nome do Restaurante"
    )

    if st.button("Salvar Restaurante"):

        if novo_restaurante.strip():

            novo_df = pd.DataFrame({

                "Restaurante": [
                    novo_restaurante.strip()
                ]

            })

            df_restaurantes = pd.concat(
                [df_restaurantes, novo_df],
                ignore_index=True
            )

            df_restaurantes.drop_duplicates(
                inplace=True
            )

            df_restaurantes.to_csv(
                ARQ_RESTAURANTES,
                index=False
            )

            st.success(
                "✅ Restaurante salvo!"
            )

            st.rerun()

    st.subheader("📋 Restaurantes")

    st.dataframe(
        df_restaurantes,
        use_container_width=True
    )

# =====================================================
# TAB PRODUTOS
# =====================================================

with tab2:

    st.subheader("Banco Mestre de Produtos")

    col1, col2 = st.columns(2)

    with col1:

        produto = st.text_input(
            "Produto"
        )

        categoria = st.text_input(
            "Categoria"
        )

    with col2:

        unidade = st.selectbox(
            "Unidade",
            ["kg", "g", "lt", "ml", "un"]
        )

        preco = st.number_input(
            "Preço Base",
            min_value=0.0,
            format="%.2f"
        )

    if st.button("Salvar Produto"):

        if produto.strip():

            novo_produto = pd.DataFrame({

                "Produto": [
                    produto.strip().lower()
                ],

                "Categoria": [
                    categoria.strip()
                ],

                "Unidade": [
                    unidade
                ],

                "Preco": [
                    preco
                ]

            })

            df_produtos = pd.concat(
                [df_produtos, novo_produto],
                ignore_index=True
            )

            df_produtos.drop_duplicates(
                subset=["Produto"],
                keep="last",
                inplace=True
            )

            df_produtos.to_csv(
                ARQ_PRODUTOS,
                index=False
            )

            st.success(
                "✅ Produto salvo!"
            )

            st.rerun()

    st.subheader("📦 Produtos Cadastrados")

    st.dataframe(
        df_produtos,
        use_container_width=True
    )

# =====================================================
# TAB MONTAGEM
# =====================================================

with tab3:

    st.subheader("Montagem de Prato")

    if restaurante_selecionado is None:

        st.warning(
            "Cadastre um restaurante primeiro."
        )

    elif df_produtos.empty:

        st.warning(
            "Cadastre produtos primeiro."
        )

    else:

        nome_prato = st.text_input(
            "Nome do Prato"
        )

        qtd_ingredientes = st.number_input(
            "Quantidade de Ingredientes",
            1,
            20,
            1
        )

        ingredientes_json = []

        custos = []

        produtos_lista = sorted(
            df_produtos["Produto"].unique()
        )

        for i in range(qtd_ingredientes):

            st.markdown(
                f"### Ingrediente {i+1}"
            )

            col1, col2 = st.columns(2)

            with col1:

                produto_escolhido = st.selectbox(
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

            linha = df_produtos[
                df_produtos["Produto"]
                ==
                produto_escolhido
            ]

            preco_base = float(
                linha["Preco"].values[0]
            )

            unidade_base = (
                linha["Unidade"].values[0]
            )

            custo = preco_base * quantidade

            custos.append(custo)

            ingredientes_json.append({

                "produto": produto_escolhido,
                "quantidade": quantidade,
                "unidade": unidade_base,
                "preco_base": preco_base,
                "custo": round(custo, 2)

            })

            st.info(
                f"""
                💰 Preço Base: R$ {preco_base:.2f}
                
                📦 Quantidade: {quantidade} {unidade_base}
                
                ➡️ Custo: R$ {custo:.2f}
                """
            )

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

        margem = (
            (lucro / preco_venda) * 100
            if preco_venda > 0 else 0
        )

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "💵 Custo",
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

        col4.metric(
            "💎 Margem",
            f"{margem:.2f}%"
        )

        preco_ideal = (
            custo_total / 0.35
            if custo_total > 0 else 0
        )

        st.info(
            f"""
            💡 Preço ideal para CMV de 35%:
            R$ {preco_ideal:.2f}
            """
        )

        if cmv > 60:
            st.error("⚠️ CMV muito alto")

        elif cmv > 40:
            st.warning("⚠️ CMV moderado")

        else:
            st.success("🔥 Excelente margem")

        if st.button("Salvar Prato"):

            if nome_prato.strip():

                novo_prato = pd.DataFrame({

                    "Restaurante": [
                        restaurante_selecionado
                    ],

                    "Prato": [
                        nome_prato.strip()
                    ],

                    "Ingredientes": [
                        json.dumps(
                            ingredientes_json
                        )
                    ],

                    "Custo": [
                        round(custo_total, 2)
                    ],

                    "Venda": [
                        round(preco_venda, 2)
                    ],

                    "Lucro": [
                        round(lucro, 2)
                    ],

                    "CMV": [
                        round(cmv, 2)
                    ]

                })

                df_pratos = pd.concat(
                    [df_pratos, novo_prato],
                    ignore_index=True
                )

                df_pratos.to_csv(
                    ARQ_PRATOS,
                    index=False
                )

                st.success(
                    "✅ Prato salvo!"
                )

                st.rerun()

# =====================================================
# TAB DASHBOARD
# =====================================================

with tab4:

    st.subheader("Dashboard Executivo")

    if not df_pratos.empty:

        if restaurante_selecionado:

            df_dash = df_pratos[
                df_pratos["Restaurante"]
                ==
                restaurante_selecionado
            ]

        else:

            df_dash = df_pratos

        if not df_dash.empty:

            fig1 = px.bar(
                df_dash,
                x="Prato",
                y="CMV",
                color="CMV",
                text="CMV",
                template="plotly_dark",
                title="CMV por prato"
            )

            st.plotly_chart(
                fig1,
                use_container_width=True
            )

            fig2 = px.bar(
                df_dash,
                x="Prato",
                y="Lucro",
                color="Lucro",
                text="Lucro",
                template="plotly_dark",
                title="Lucro por prato"
            )

            st.plotly_chart(
                fig2,
                use_container_width=True
            )

            fig3 = px.pie(
                df_dash,
                names="Prato",
                values="Venda",
                hole=0.5,
                template="plotly_dark",
                title="Participação em vendas"
            )

            st.plotly_chart(
                fig3,
                use_container_width=True
            )

        else:

            st.info(
                "Nenhum prato encontrado."
            )

# =====================================================
# TAB HISTÓRICO
# =====================================================

with tab5:

    st.subheader("Histórico de Pratos")

    if not df_pratos.empty:

        if restaurante_selecionado:

            df_hist = df_pratos[
                df_pratos["Restaurante"]
                ==
                restaurante_selecionado
            ]

        else:

            df_hist = df_pratos

        st.dataframe(
            df_hist,
            use_container_width=True
        )

    else:

        st.info(
            "Nenhum histórico encontrado."
        )