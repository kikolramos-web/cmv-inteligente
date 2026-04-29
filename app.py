import pandas as pd
import streamlit as st

st.set_page_config(page_title="CMV Inteligente PRO", layout="centered")

st.title("🍽️ CMV Inteligente PRO")

# =============================
# CARREGAR BASE
# =============================
try:
    df = pd.read_csv("precos.csv", sep=",")
    df.columns = df.columns.str.strip().str.lower()
except:
    st.error("Erro ao carregar precos.csv")
    st.stop()

# =============================
# FILTRO POR ESTADO
# =============================
estado = st.selectbox("Selecione o Estado", sorted(df["estado"].unique()))
df_estado = df[df["estado"] == estado]

# =============================
# MONTAGEM DO PRATO
# =============================
st.subheader("🧾 Montagem do Prato")

ingredientes = df_estado["produto"].unique()

itens = []

num_itens = st.number_input("Quantidade de ingredientes", min_value=1, max_value=10, value=1)

for i in range(num_itens):
    st.markdown(f"### Ingrediente {i+1}")

    col1, col2 = st.columns(2)

    with col1:
        produto = st.selectbox(f"Produto {i+1}", ingredientes, key=f"prod_{i}")

    with col2:
        quantidade = st.number_input(f"Qtd ({produto})", min_value=0.0, step=0.1, key=f"qtd_{i}")

    preco = df_estado[df_estado["produto"] == produto]["preco"].values[0]
    unidade = df_estado[df_estado["produto"] == produto]["unidade"].values[0]

    custo = preco * quantidade

    itens.append({
        "produto": produto,
        "quantidade": quantidade,
        "unidade": unidade,
        "preco": preco,
        "custo": custo
    })

# =============================
# CÁLCULO TOTAL
# =============================
st.markdown("## 💰 Resultado do Prato")

total = sum(item["custo"] for item in itens)

for item in itens:
    st.write(f"{item['produto']} → {item['quantidade']} {item['unidade']} = R$ {item['custo']:.2f}")

st.markdown(f"### 🔹 Custo total do prato: R$ {total:.2f}")

# =============================
# MARGEM E PREÇO DE VENDA
# =============================
st.subheader("📈 Definir Margem")

margem = st.slider("Margem de lucro (%)", 0, 100, 70)

preco_venda = total / (1 - margem/100) if margem < 100 else 0

st.markdown(f"### 💵 Preço sugerido de venda: R$ {preco_venda:.2f}")

# =============================
# BASE DE DADOS
# =============================
with st.expander("📋 Ver base de preços"):
    st.dataframe(df_estado)