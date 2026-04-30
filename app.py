import streamlit as st
import pandas as pd

st.set_page_config(page_title="CMV Inteligente PRO", layout="centered")

# =========================
# FUNÇÕES
# =========================
def formatar_real(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

@st.cache_data
def carregar_base_precos():
    return pd.read_csv("base_precos.csv")

@st.cache_data
def carregar_produtos():
    return pd.read_csv("produtos_base.csv")["produto"].tolist()

def buscar_preco(produto, estado, df_precos):
    filtro = (
        df_precos["produto"].str.lower().str.contains(produto.lower())
    ) & (df_precos["estado"] == estado)

    resultado = df_precos[filtro]

    if not resultado.empty:
        return float(resultado.iloc[0]["preco"])
    else:
        return None

# =========================
# ESTADOS
# =========================
estados = [
    "AC","AL","AP","AM","BA","CE","DF","ES","GO",
    "MA","MT","MS","MG","PA","PB","PR","PE","PI",
    "RJ","RN","RS","RO","RR","SC","SP","SE","TO"
]

st.title("🍽️ CMV Inteligente PRO")

df_precos = carregar_base_precos()
produtos_base = carregar_produtos()

# =========================
# MENU
# =========================
opcao = st.radio(
    "Escolha o modo:",
    ["Manual", "Importar planilha", "Cadastrar produto"]
)

# =========================
# MODO MANUAL
# =========================
if opcao == "Manual":
    st.header("🧾 Montagem do Prato")

    estado = st.selectbox("Selecione o Estado", estados)

    num_ingredientes = st.number_input(
        "Quantidade de ingredientes",
        min_value=1,
        max_value=50,
        value=1
    )

    ingredientes = []

    for i in range(int(num_ingredientes)):
        st.subheader(f"Ingrediente {i+1}")

        nome = st.selectbox(
            f"Produto {i+1}",
            options=[""] + produtos_base,
            key=f"nome_{i}"
        )

        quantidade = st.number_input(
            f"Quantidade {i+1}",
            min_value=0.0,
            step=0.01,
            key=f"qtd_{i}"
        )

        preco_auto = None
        if nome:
            preco_auto = buscar_preco(nome, estado, df_precos)

        if preco_auto:
            st.success(f"💰 Preço automático: {formatar_real(preco_auto)}")
            preco = preco_auto
        else:
            preco = st.number_input(
                f"Preço unitário {i+1}",
                min_value=0.0,
                step=0.01,
                key=f"preco_{i}"
            )

        if nome:
            ingredientes.append({
                "produto": nome,
                "quantidade": quantidade,
                "preco": preco
            })

    if st.button("Calcular CMV"):
        if ingredientes:
            df = pd.DataFrame(ingredientes)
            df["custo"] = df["quantidade"] * df["preco"]

            custo_total = df["custo"].sum()

            st.subheader("📊 Resultado")
            st.dataframe(df)

            st.success(f"💰 Custo total: {formatar_real(custo_total)}")

            cmv_desejado = 0.30
            preco_venda = custo_total / cmv_desejado

            st.info(f"💡 Preço sugerido (CMV 30%): {formatar_real(preco_venda)}")

        else:
            st.warning("Adicione ingredientes.")

# =========================
# IMPORTAR PLANILHA
# =========================
elif opcao == "Importar planilha":
    st.header("📥 Importar Ficha Técnica")

    uploaded_file = st.file_uploader("Envie Excel", type=["xlsx"])

    if uploaded_file:
        df = pd.read_excel(uploaded_file)

        if all(col in df.columns for col in ["produto","quantidade","unidade","preco_unitario"]):
            df["custo"] = df["quantidade"] * df["preco_unitario"]
            custo_total = df["custo"].sum()

            st.dataframe(df)
            st.success(f"Custo total: {formatar_real(custo_total)}")

        else:
            st.error("Formato inválido.")

# =========================
# CADASTRAR PRODUTO
# =========================
elif opcao == "Cadastrar produto":
    st.header("➕ Novo Produto")

    produto = st.text_input("Nome do produto")
    estado = st.selectbox("Estado", estados)
    preco = st.number_input("Preço", min_value=0.0)

    if st.button("Salvar"):
        # salvar preço
        novo_preco = pd.DataFrame([{
            "produto": produto,
            "estado": estado,
            "preco": preco
        }])

        novo_preco.to_csv("base_precos.csv", mode="a", header=False, index=False)

        # salvar produto base (sem duplicar)
        produtos_existentes = pd.read_csv("produtos_base.csv")["produto"].str.lower().tolist()

        if produto.lower() not in produtos_existentes:
            novo_produto = pd.DataFrame([{"produto": produto}])
            novo_produto.to_csv("produtos_base.csv", mode="a", header=False, index=False)

        st.success("Produto salvo com sucesso!")