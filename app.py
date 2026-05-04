import streamlit as st
import pandas as pd
import sqlite3

st.set_page_config(page_title="CMV Inteligente PRO", layout="centered")

st.title("🍽️ CMV Inteligente PRO")
st.write("🔥 VERSÃO BASE VIVA 3.0 🔥")

# -------------------------------
# BANCO DE DADOS
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
# DADOS INICIAIS AUTOMÁTICOS
# -------------------------------
cursor.execute("SELECT COUNT(*) FROM precos")
if cursor.fetchone()[0] == 0:
    dados = [
        ("arroz branco", "DF", 5.80),
        ("arroz branco", "SP", 5.20),
        ("feijao", "DF", 8.50),
        ("feijao", "SP", 7.00),
        ("frango", "SP", 18.00),
        ("carne", "SP", 28.00),
        ("batata", "SP", 6.00),
    ]

    cursor.executemany(
        "INSERT INTO precos (produto, estado, preco) VALUES (?, ?, ?)",
        dados
    )
    conn.commit()

# -------------------------------
# FUNÇÕES
# -------------------------------
def carregar_base():
    df = pd.read_sql("SELECT * FROM precos", conn)
    return df

def salvar(produto, estado, preco):
    cursor.execute(
        "INSERT INTO precos (produto, estado, preco) VALUES (?, ?, ?)",
        (produto.lower(), estado, preco)
    )
    conn.commit()

# -------------------------------
# MENU PRINCIPAL
# -------------------------------
menu = st.radio(
    "Escolha uma opção:",
    ["Montar Prato", "Cadastrar Produto"]
)

# -------------------------------
# CARREGA BASE
# -------------------------------
base = carregar_base()

# -------------------------------
# CADASTRAR PRODUTO
# -------------------------------
if menu == "Cadastrar Produto":

    st.subheader("📦 Cadastro de Produto")

    produto = st.text_input("Nome do produto")
    estado = st.selectbox("Estado", ["DF", "SP", "RJ", "MG", "GO"])
    preco = st.number_input("Preço (R$)", min_value=0.0)

    if st.button("Salvar produto"):
        if produto and preco > 0:
            salvar(produto, estado, preco)
            st.success("✅ Produto cadastrado!")
            st.rerun()
        else:
            st.warning("Preencha corretamente")

    st.subheader("📊 Base atual")
    st.dataframe(base)

# -------------------------------
# MONTAR PRATO
# -------------------------------
else:

    st.subheader("🧾 Montagem do Prato")

    estado = st.selectbox(
        "Selecione o Estado",
        sorted(base["estado"].unique())
    )

    qtd = st.number_input("Quantidade de itens", min_value=1)

    itens = []

    for i in range(int(qtd)):
        st.markdown(f"### Item {i+1}")

        produto = st.selectbox(
            f"Produto {i}",
            sorted(base["produto"].unique()),
            key=f"prod_{i}"
        )

        quantidade = st.number_input(
            f"Quantidade {i}",
            key=f"qtd_{i}"
        )

        preco = base[
            (base["produto"] == produto) &
            (base["estado"] == estado)
        ]["preco"]

        if not preco.empty:
            custo = float(preco.values[0])
        else:
            custo = 0.0

        st.write(f"💰 Custo unitário: R$ {custo:.2f}")

        total = quantidade * custo

        itens.append({
            "Produto": produto,
            "Quantidade": quantidade,
            "Custo Unitário": custo,
            "Custo Total": total
        })

    if itens:
        df = pd.DataFrame(itens)

        st.subheader("📊 Resultado")
        st.dataframe(df)

        custo_total = df["Custo Total"].sum()

        st.success(f"💰 Custo Total: R$ {custo_total:.2f}")

        # IA simples
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