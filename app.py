import streamlit as st
import pandas as pd

st.set_page_config(page_title="CMV Inteligente", layout="centered")

st.title("🍽️ CMV Inteligente PRO")

# -------------------------------
# RESET
# -------------------------------
if st.button("🔄 Resetar aplicação"):
    st.session_state.clear()
    st.rerun()

# -------------------------------
# SELETOR DE MODO (ESSENCIAL)
# -------------------------------
modo = st.radio(
    "Escolha o modo de entrada:",
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

        nome = st.text_input(f"Nome {i}", key=f"nome_{i}")
        quantidade = st.number_input(f"Quantidade (kg/un) {i}", key=f"qtd_{i}")
        custo = st.number_input(f"Custo unitário (R$) {i}", key=f"custo_{i}")

        if nome:
            total = quantidade * custo
            ingredientes.append({
                "Ingrediente": nome,
                "Quantidade": quantidade,
                "Custo Unitário": custo,
                "Custo Total": total
            })

    if ingredientes:
        df = pd.DataFrame(ingredientes)

        st.subheader("📊 Resultado")
        st.dataframe(df)

        custo_total = df["Custo Total"].sum()
        custo_unitario = custo_total / len(df)

        st.success(f"💰 Custo Total: R$ {custo_total:.2f}")
        st.info(f"📌 Custo Médio por Ingrediente: R$ {custo_unitario:.2f}")

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

        # Validação básica
        colunas_esperadas = ["Ingrediente", "Quantidade", "Custo Unitário"]

        if all(col in df.columns for col in colunas_esperadas):

            df["Custo Total"] = df["Quantidade"] * df["Custo Unitário"]

            st.subheader("📊 Resultado")
            st.dataframe(df)

            custo_total = df["Custo Total"].sum()
            custo_unitario = custo_total / len(df)

            st.success(f"💰 Custo Total: R$ {custo_total:.2f}")
            st.info(f"📌 Custo Médio por Ingrediente: R$ {custo_unitario:.2f}")

        else:
            st.error("❌ A planilha precisa ter as colunas: Ingrediente, Quantidade, Custo Unitário")

    else:
        st.warning("📎 Envie uma planilha para continuar")