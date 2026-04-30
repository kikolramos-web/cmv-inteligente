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
# DADOS INICIAIS
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
# MENU (AGORA CORRETO)
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
    unidades = ["kg", "g", "L", "ml", "un"]

    for i in range(int(num_ingredientes)):
        st.subheader(f"Ingrediente {i+1}")

        nome = st.selectbox(
            f"Produto {i+1}",
            options=[""] + produtos_base,
            key=f"nome_{i}"
        )

        unidade = st.selectbox(
            f"Unidade {i+1}",
            unidades,
            key=f"unidade_{i}"
        )

        quantidade = st.number_input(
            f"Quantidade {i+1}",
            min_value=0.0,
            step=0.01,
            key=f"qtd_{i}"
        )

        # Conversão
        if unidade == "g" or unidade == "ml":
            quantidade_convertida = quantidade / 1000
        else:
            quantidade_convertida = quantidade

        preco_auto = None
        if nome:
            preco_auto = buscar_preco(nome, estado, df_precos)

        if preco_auto:
            st.success(f"💰 Preço automático: {formatar_real(preco_auto)}")
            preco = preco_auto
        else:
            preco = st.number_input(
                f"Preço unitário {i+1} (R$)",
                min_value=0.0,
                step=0.01,
                key=f"preco_{i}"
            )
            st.caption(f"Valor: {formatar_real(preco)}")

        if nome:
            ingredientes.append({
                "produto": nome,
                "quantidade": quantidade_convertida,
                "preco": preco,
                "unidade": unidade
            })

    if st.button("Calcular CMV"):
        if ingredientes:
            df = pd.DataFrame(ingredientes)
            df["custo"] = df["quantidade"] * df["preco"]

            custo_total = df["custo"].sum()

            st.subheader("📊 Resultado")
            st.dataframe(df)

            st.success(f"💰 Custo total: {formatar_real(custo_total)}")

            # Porções
            porcoes = st.number_input("Número de porções", min_value=1, value=1)
            custo_por_porcao = custo_total / porcoes

            st.write(f"🍽️ Custo por porção: {formatar_real(custo_por_porcao)}")

            # CMV
            cmv_percentual = st.slider("CMV desejado (%)", 10, 80, 30)
            cmv = cmv_percentual / 100

            preco_venda = custo_total / cmv

            st.info(f"💡 Preço de venda: {formatar_real(preco_venda)}")

            # Indicador
            if cmv <= 0.30:
                st.success("🟢 CMV saudável")
            elif cmv <= 0.50:
                st.warning("🟡 CMV médio")
            else:
                st.error("🔴 CMV alto")

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
    preco = st.number_input("Preço (R$)", min_value=0.0)

    if st.button("Salvar"):
        novo_preco = pd.DataFrame([{
            "produto": produto,
            "estado": estado,
            "preco": preco
        }])

        novo_preco.to_csv("base_precos.csv", mode="a", header=False, index=False)

        produtos_existentes = pd.read_csv("produtos_base.csv")["produto"].str.lower().tolist()

        if produto.lower() not in produtos_existentes:
            novo_produto = pd.DataFrame([{"produto": produto}])
            novo_produto.to_csv("produtos_base.csv", mode="a", header=False, index=False)

        st.success("Produto salvo com sucesso!")