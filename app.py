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

try:
    base_precos = carregar_base()
except:
    st.error("❌ base_precos.csv não encontrado.")
    st.stop()

# -------------------------------
# RESET
# -------------------------------
if st.button("🔄 Resetar aplicação"):
    st.session_state.clear()
    st.rerun()

# -------------------------------
# FILTROS PRINCIPAIS
# -------------------------------
estado = st.selectbox(
    "📍 Selecione o Estado",
    sorted(base_precos["estado"].dropna().unique())
)

modo = st.radio(
    "Modo de uso:",
    ["Manual", "Planilha"]
)

st.divider()

# -------------------------------
# FUNÇÃO DE IA (SIMPLES)
# -------------------------------
def calcular_preco(custo_total, margem):
    if margem >= 1:
        return 0
    return custo_total / (1 - margem)

# -------------------------------
# MODO MANUAL
# -------------------------------
if modo == "Manual":

    st.subheader("🧾 Montagem do Prato")

    qtd = st.number_input("Quantidade de itens", min_value=1, step=1)

    ingredientes = []

    for i in range(int(qtd)):
        st.markdown(f"### Item {i+1}")

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

        st.success(f"💰 Custo Total: R$ {custo_total:.2f}")

        # -------------------------------
        # IA DE PREÇO
        # -------------------------------
        st.subheader("🤖 Inteligência de Preço")

        margem = st.slider(
            "Margem desejada (%)",
            10, 90, 30
        ) / 100

        preco_venda = calcular_preco(custo_total, margem)
        lucro = preco_venda - custo_total

        st.success(f"💰 Preço sugerido: R$ {preco_venda:.2f}")
        st.info(f"📈 Lucro estimado: R$ {lucro:.2f}")

        # ALERTAS
        if margem < 0.2:
            st.warning("⚠️ Margem muito baixa")
        elif margem > 0.6:
            st.info("💡 Margem alta — pode impactar vendas")
        else:
            st.success("✅ Margem saudável")

# -------------------------------
# MODO PLANILHA
# -------------------------------
else:

    st.subheader("📂 Upload da Planilha")

    arquivo = st.file_uploader("Envie (.xlsx)", type=["xlsx"])

    if arquivo:

        df = pd.read_excel(arquivo)
        st.dataframe(df)

        colunas = ["Produto", "Quantidade", "Custo Unitário"]

        if all(col in df.columns for col in colunas):

            df["Custo Total (R$)"] = df["Quantidade"] * df["Custo Unitário"]

            custo_total = df["Custo Total (R$)"].sum()

            st.success(f"💰 Custo Total: R$ {custo_total:.2f}")

            # IA
            st.subheader("🤖 Inteligência de Preço")

            margem = st.slider(
                "Margem desejada (%)",
                10, 90, 30
            ) / 100

            preco_venda = calcular_preco(custo_total, margem)
            lucro = preco_venda - custo_total

            st.success(f"💰 Preço sugerido: R$ {preco_venda:.2f}")
            st.info(f"📈 Lucro estimado: R$ {lucro:.2f}")

        else:
            st.error("❌ Planilha precisa ter: Produto, Quantidade, Custo Unitário")

    else:
        st.warning("📎 Envie uma planilha")