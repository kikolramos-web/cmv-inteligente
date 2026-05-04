import streamlit as st
import pandas as pd
import sqlite3

st.set_page_config(page_title="CMV Inteligente PRO", layout="centered")

st.title("🍽️ CMV Inteligente PRO")

# -------------------------------
# BANCO DE DADOS (SQLite)
# -------------------------------
conn = sqlite3.connect("base_precos.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS precos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    produto TEXT,
    estado TEXT,
    preco REAL
)
""")
conn.commit()

# -------------------------------
# FUNÇÕES
# -------------------------------
def carregar_base():
    df = pd.read_sql("SELECT * FROM precos", conn)
    df.columns = df.columns.str.lower()
    return df

def salvar_produto(produto, estado, preco):
    cursor.execute(
        "INSERT INTO precos (produto, estado, preco) VALUES (?, ?, ?)",
        (produto.lower(), estado, preco)
    )
    conn.commit()

# -------------------------------
# RESET
# -------------------------------
if st.button("🔄 Resetar aplicação"):
    st.session_state.clear()
    st.rerun()

# -------------------------------
# MENU
# -------------------------------
menu = st.radio(
    "Escolha uma opção:",
    ["Montar Prato", "Cadastrar Produto"]
)

# -------------------------------
# CARREGA BASE
# -------------------------------
base_precos = carregar_base()

# -------------------------------
# CADASTRO
# -------------------------------
if menu == "Cadastrar Produto":

    st.subheader("📦 Cadastro de Produtos")

    produto = st.text_input("Nome do produto")
    estado = st.selectbox("Estado", ["DF", "SP", "RJ", "MG", "GO"])
    preco = st.number_input("Preço (R$)", min_value=0.0)

    if st.button("Salvar"):
        if produto and preco > 0:
            salvar_produto(produto, estado, preco)
            st.success("✅ Produto salvo com sucesso!")
            st.rerun()
        else:
            st.warning("Preencha corretamente")

    if not base_precos.empty:
        st.subheader("📊 Base atual")
        st.dataframe(base_precos)

# -------------------------------
# MONTAR PRATO
# -------------------------------
else:

    st.subheader("🧾 Montagem do Prato")

    if base_precos.empty:
        st.warning("⚠️ Cadastre produtos primeiro")
        st.stop()

    estado = st.selectbox(
        "📍 Selecione o Estado",
        sorted(base_precos["estado"].unique())
    )

    qtd = st.number_input("Quantidade de itens", min_value=1, step=1)

    ingredientes = []

    for i in range(int(qtd)):
        st.markdown(f"### Item {i+1}")

        produto = st.selectbox(
            f"Produto {i}",
            sorted(base_precos["produto"].unique()),
            key=f"prod_{i}"
        )

        quantidade = st.number_input(f"Quantidade {i}", key=f"qtd_{i}")

        preco_base = base_precos[
            (base_precos["produto"] == produto) &
            (base_precos["estado"] == estado)
        ]["preco"]

        if not preco_base.empty:
            custo = float(preco_base.values[0])
        else:
            custo = 0.0

        st.write(f"💰 Preço unitário: R$ {custo:.2f}")

        total = quantidade * custo

        ingredientes.append({
            "Produto": produto,
            "Quantidade": quantidade,
            "Custo Unitário": custo,
            "Custo Total": total
        })

    if ingredientes:
        df = pd.DataFrame(ingredientes)

        st.subheader("📊 Resultado")
        st.dataframe(df)

        custo_total = df["Custo Total"].sum()

        st.success(f"💰 Custo Total: R$ {custo_total:.2f}")

        # IA
        st.subheader("🤖 Inteligência de Preço")

        margem = st.slider("Margem (%)", 10, 90, 30) / 100

        if custo_total > 0:
            preco_venda = custo_total / (1 - margem)
            lucro = preco_venda - custo_total

            st.success(f"💰 Preço sugerido: R$ {preco_venda:.2f}")
            st.info(f"📈 Lucro estimado: R$ {lucro:.2f}")

            if margem < 0.2:
                st.warning("⚠️ Margem baixa")
            elif margem > 0.6:
                st.info("💡 Margem alta")
            else:
                st.success("✅ Margem saudável")