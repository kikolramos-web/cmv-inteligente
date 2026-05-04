import streamlit as st
import pandas as pd

st.set_page_config(page_title="CMV Inteligente PRO", layout="centered")

st.title("🍽️ CMV Inteligente PRO")

# -------------------------------
# CARREGAR BASE
# -------------------------------
@st.cache_data
def carregar_base():
    df = pd.read_csv("base_precos.csv")
    df.columns = df.columns.str.strip().str.lower()
    return df

base_precos = carregar_base()

# -------------------------------
# RESET
# -------------------------------
if st.button("🔄 Resetar aplicação"):
    st.session_state.clear()
    st.rerun()

# -------------------------------
# ESTADO (AGORA FUNCIONA)
# -------------------------------
estado = st.selectbox(
    "📍 Selecione o Estado",
    sorted(base_precos["estado"].dropna().unique())
)

# -------------------------------
# MODO
# -------------------------------
modo = st.radio(
    "Escolha o modo:",
    ["Manual", "Planilha"]
)

st.divider()

# -------------------------------
# MODO MANUAL
# -------------------------------
if modo == "Manual":

    st.subheader("🧾 Montagem do Prato")

    qtd = st.number_input("Quantidade de ingredientes", min_value=1, step=1)

    ingredientes = []

    for i in range(int(qtd)):
        st.markdown(f"### Ingrediente {i+1}")

        nome = st.text_input(f"Produto {i}", key=f"nome_{i}")
        quantidade = st.number_input(f"Quantidade {i}", key=f"qtd_{i}")

        nome_base = nome.lower().strip()

        preco_base = base_precos[
            (base_precos["produto"] == nome_base) &
            (base_precos["estado"] == estado)
        ]["preco"]

        if not preco_base.empty:
            custo_default = float(preco_base.values[0])
        else:
            custo_default = 0.0

        custo = st.number_input(
            f"Custo unitário (R$) {i}",
            value=custo_default,
            key=f"custo_{i}"
        )

        if nome:
            total = quantidade * custo
            ingredientes.append({
                "Produto": nome,
                "Quantidade": quantidade,
                "Custo Unitário (R$)": custo,
                "Custo Total (R$)": total
            })

    if ingredientes:
        df = pd.DataFrame(ingredientes)

        st.subheader("📊 Resultado")
        st.dataframe(df)

        custo_total = df["Custo Total (R$)"].sum()
        custo_unitario = custo_total / len(df)

        st.success(f"💰 Custo Total: R$ {custo_total:.2f}")
        st.info(f"📌 Custo Médio por Item: R$ {custo_unitario:.2f}")

# -------------------------------
# MODO PLANILHA
# -------------------------------
else:

    st.subheader("📂 Upload da Planilha")

    arquivo = st.file_uploader(
        "Envie sua planilha (.xlsx)",
        type=["xlsx"]
    )

    if arquivo is not None:

        df = pd.read_excel(arquivo)

        st.subheader("📊 Dados carregados")
        st.dataframe(df)

        colunas_esperadas = ["Produto", "Quantidade", "Custo Unitário"]

        if all(col in df.columns for col in colunas_esperadas):

            df["Custo Total (R$)"] = df["Quantidade"] * df["Custo Unitário"]

            st.subheader("📊 Resultado")
            st.dataframe(df)

            custo_total = df["Custo Total (R$)"].sum()
            custo_unitario = custo_total / len(df)

            st.success(f"💰 Custo Total: R$ {custo_total:.2f}")
            st.info(f"📌 Custo Médio por Item: R$ {custo_unitario:.2f}")

        else:
            st.error("❌ A planilha precisa ter: Produto, Quantidade, Custo Unitário")

    else:
        st.warning("📎 Envie uma planilha para continuar")