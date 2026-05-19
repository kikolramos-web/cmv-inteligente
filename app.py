import streamlit as st
import pandas as pd
import os
import json
import plotly.express as px

# ---------------------------------
# CONFIGURAÇÃO DA PÁGINA
# ---------------------------------
st.set_page_config(
    page_title="CMV Inteligente PRO",
    layout="wide"
)

# ---------------------------------
# ESTILO VISUAL
# ---------------------------------
st.markdown("""
<style>

.main {
    background-color: #f7f7f7;
}

.stApp {
    background-color: #f7f7f7;
}

h1, h2, h3 {
    color: #2c3e50;
}

div[data-testid="stMetric"] {
    background-color: #ffffff;
    border-radius: 15px;
    padding: 15px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.stButton>button {
    background-color: #a8dadc;
    color: #1d3557;
    border-radius: 10px;
    border: none;
    font-weight: bold;
    padding: 10px 20px;
}

.stButton>button:hover {
    background-color: #8ecae6;
    color: black;
}

[data-testid="stSidebar"] {
    background-color: #edf6f9;
}

.block-container {
    padding-top: 2rem;
}

</style>
""", unsafe_allow_html=True)

# ---------------------------------
# TÍTULO
# ---------------------------------
st.title("🍽️ CMV Inteligente PRO")

# ---------------------------------
# ARQUIVOS
# ---------------------------------
ARQ_PRECOS = "base_precos.csv"
ARQ_PRATOS = "pratos.csv"

# ---------------------------------
# SESSION STATE
# ---------------------------------
if "qtd_ingredientes" not in st.session_state:
    st.session_state.qtd_ingredientes = 1

if "modo_edicao" not in st.session_state:
    st.session_state.modo_edicao = False

if "prato_editando" not in st.session_state:
    st.session_state.prato_editando = ""

# ---------------------------------
# FUNÇÃO BASE PADRÃO
# ---------------------------------
def criar_base_padrao():

    df_init = pd.DataFrame({
        "Estado": [
            "DF", "DF", "DF",
            "SP", "SP", "SP",
            "RJ", "RJ",
            "MG", "MG",
            "BA", "BA",
            "GO", "GO",
            "PR", "PR",
            "SC", "SC",
            "RS", "RS"
        ],
        "Produto": [
            "arroz", "feijao", "frango",
            "arroz", "feijao", "frango",
            "arroz", "carne",
            "feijao", "frango",
            "arroz", "carne",
            "arroz", "frango",
            "feijao", "carne",
            "arroz", "frango",
            "feijao", "carne"
        ],
        "Preco": [
            5.50, 7.00, 12.00,
            5.20, 6.80, 11.50,
            5.80, 26.00,
            6.50, 11.00,
            5.70, 25.50,
            5.40, 11.80,
            6.70, 24.50,
            5.60, 11.30,
            6.90, 25.00
        ]
    })

    df_init.to_csv(ARQ_PRECOS, index=False)
    return df_init

# ---------------------------------
# CARREGAR BASE
# ---------------------------------
if not os.path.exists(ARQ_PRECOS):
    df_precos = criar_base_padrao()

else:

    try:
        df_precos = pd.read_csv(ARQ_PRECOS)

        if df_precos.empty:
            df_precos = criar_base_padrao()

        df_precos.columns = df_precos.columns.str.strip().str.capitalize()

        colunas_esperadas = ["Estado", "Produto", "Preco"]

        if not all(col in df_precos.columns for col in colunas_esperadas):
            df_precos = criar_base_padrao()

    except:
        df_precos = criar_base_padrao()

# ---------------------------------
# SIDEBAR
# ---------------------------------
st.sidebar.title("📌 Menu")

estados = sorted(df_precos["Estado"].unique())

estado = st.sidebar.selectbox(
    "📍 Estado",
    estados
)

# ---------------------------------
# FILTRO
# ---------------------------------
df_estado = df_precos[df_precos["Estado"] == estado]

produtos_lista = sorted(df_estado["Produto"].unique())

# ---------------------------------
# CADASTRAR INGREDIENTE
# ---------------------------------
st.subheader("➕ Cadastrar / Atualizar Ingrediente")

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

        produto_limpo = novo_produto.strip().lower()

        existe = (
            (df_precos["Estado"] == estado) &
            (df_precos["Produto"] == produto_limpo)
        )

        if existe.any():

            df_precos.loc[existe, "Preco"] = novo_preco

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

        df_precos.to_csv(ARQ_PRECOS, index=False)

        st.success("✅ Ingrediente salvo com sucesso!")
        st.rerun()

    else:
        st.warning("Digite o nome do produto.")

# ---------------------------------
# EDITAR PRATO
# ---------------------------------
st.subheader("✏️ Editar Prato")

if os.path.exists(ARQ_PRATOS):

    try:

        df_pratos_existentes = pd.read_csv(ARQ_PRATOS)

        if not df_pratos_existentes.empty:

            lista_pratos = df_pratos_existentes["Prato"].unique().tolist()

            prato_selecionado = st.selectbox(
                "Selecione um prato salvo",
                [""] + lista_pratos
            )

            if st.button("Carregar Prato"):

                if prato_selecionado:

                    prato_data = df_pratos_existentes[
                        df_pratos_existentes["Prato"] == prato_selecionado
                    ].iloc[0]

                    ingredientes_salvos = json.loads(
                        prato_data["Ingredientes"]
                    )

                    st.session_state.qtd_ingredientes = len(
                        ingredientes_salvos
                    )

                    for i, item in enumerate(ingredientes_salvos):

                        st.session_state[f"produto_{i}"] = item["produto"]

                        st.session_state[f"quantidade_{i}"] = item["quantidade"]

                        st.session_state[f"unidade_{i}"] = item.get(
                            "unidade",
                            "kg"
                        )

                    st.session_state["preco_venda"] = float(
                        prato_data["Venda"]
                    )

                    st.session_state["nome_prato"] = prato_data["Prato"]

                    st.success("✅ Prato carregado!")
                    st.rerun()

    except:
        st.warning("Erro ao carregar pratos.")

# ---------------------------------
# MONTAGEM DO PRATO
# ---------------------------------
st.subheader("🧾 Montagem do Prato")

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

    st.markdown(f"### Ingrediente {i + 1}")

    col1, col2, col3 = st.columns(3)

    produto_padrao = (
        st.session_state.get(f"produto_{i}", produtos_lista[0])
        if produtos_lista else ""
    )

    if produto_padrao not in produtos_lista and produtos_lista:
        produto_padrao = produtos_lista[0]

    index_produto = (
        produtos_lista.index(produto_padrao)
        if produto_padrao in produtos_lista else 0
    )

    with col1:

        produto = st.selectbox(
            f"Produto {i+1}",
            produtos_lista,
            index=index_produto,
            key=f"produto_{i}"
        )

    with col2:

        quantidade = st.number_input(
            f"Quantidade {i+1}",
            min_value=0.0,
            value=float(
                st.session_state.get(f"quantidade_{i}", 1.0)
            ),
            key=f"quantidade_{i}"
        )

    with col3:

        unidade = st.selectbox(
            f"Unidade {i+1}",
            ["kg", "g", "lt", "ml", "un"],
            key=f"unidade_{i}"
        )

    preco_base = float(
        df_estado[df_estado["Produto"] == produto]["Preco"].values[0]
    )

    custo = preco_base * quantidade

    st.info(
        f"💰 Preço base: R$ {preco_base:.2f} | "
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

# ---------------------------------
# RESULTADOS
# ---------------------------------
st.subheader("📊 Resultado")

custo_total = sum(custos)

preco_venda = st.number_input(
    "Preço de venda do prato",
    min_value=0.0,
    value=float(
        st.session_state.get("preco_venda", 0.0)
    ),
    key="preco_venda"
)

cmv = (
    (custo_total / preco_venda) * 100
    if preco_venda > 0 else 0
)

lucro = preco_venda - custo_total

col1, col2, col3 = st.columns(3)

col1.metric(
    "💵 Custo Total",
    f"R$ {custo_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
)

col2.metric(
    "📈 CMV",
    f"{cmv:.2f}%"
)

col3.metric(
    "🔥 Lucro",
    f"R$ {lucro:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
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

# ---------------------------------
# SALVAR PRATO
# ---------------------------------
st.subheader("💾 Salvar Prato")

nome_prato = st.text_input(
    "Nome do prato",
    value=st.session_state.get("nome_prato", "")
)

if st.button("Salvar Prato"):

    if nome_prato.strip():

        novo_prato = pd.DataFrame({

            "Prato": [nome_prato.strip()],
            "Estado": [estado],
            "Ingredientes": [json.dumps(ingredientes_json)],
            "Custo": [round(custo_total, 2)],
            "Venda": [round(preco_venda, 2)],
            "CMV": [round(cmv, 2)]

        })

        if os.path.exists(ARQ_PRATOS):

            df_existente = pd.read_csv(ARQ_PRATOS)

            if nome_prato.strip() in df_existente["Prato"].values:

                df_existente = df_existente[
                    df_existente["Prato"] != nome_prato.strip()
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
                    mode="a",
                    header=False,
                    index=False
                )

        else:

            novo_prato.to_csv(
                ARQ_PRATOS,
                index=False
            )

        st.success("✅ Prato salvo com sucesso!")

    else:
        st.warning("Digite o nome do prato.")

# ---------------------------------
# HISTÓRICO
# ---------------------------------
st.subheader("📚 Histórico de Pratos")

if os.path.exists(ARQ_PRATOS):

    try:

        df_hist = pd.read_csv(ARQ_PRATOS)

        if not df_hist.empty:

            # DASHBOARD
            st.subheader("📊 Dashboard CMV")

            fig = px.bar(
                df_hist,
                x="Prato",
                y="CMV",
                color="CMV",
                text="CMV",
                title="CMV por Prato"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

            # FORMATAÇÃO
            df_hist_exibir = df_hist.copy()

            df_hist_exibir["Custo"] = df_hist_exibir["Custo"].apply(
                lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            )

            df_hist_exibir["Venda"] = df_hist_exibir["Venda"].apply(
                lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            )

            df_hist_exibir["CMV"] = df_hist_exibir["CMV"].apply(
                lambda x: f"{x:.2f}%"
            )

            st.dataframe(
                df_hist_exibir[
                    ["Prato", "Estado", "Custo", "Venda", "CMV"]
                ],
                use_container_width=True
            )

            # ESTATÍSTICAS
            st.subheader("📌 Estatísticas")

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "📈 CMV Médio",
                f"{df_hist['CMV'].mean():.2f}%"
            )

            col2.metric(
                "💰 Custo Médio",
                f"R$ {df_hist['Custo'].mean():.2f}"
            )

            col3.metric(
                "🍽️ Total de Pratos",
                len(df_hist)
            )

        else:
            st.info("Nenhum prato salvo ainda.")

    except:
        st.warning("Não foi possível carregar histórico.")

else:
    st.info("Nenhum prato salvo ainda.")