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
# FILTRO
# =============================
estado = st.selectbox("📍 Estado", sorted(df["estado"].unique()))
df_estado = df[df["estado"] == estado]

# =============================
# MONTAGEM DO PRATO
# =============================
st.subheader("🧾 Montagem do Prato")

ingredientes = df_estado["produto"].unique()
itens = []

num_itens = st.number_input("Quantidade de ingredientes", min_value=1, max_value=10, value=1)

for i in range(num_itens):
    col1, col2, col3 = st.columns(3)

    with col1:
        produto = st.selectbox(f"Produto {i+1}", ingredientes, key=f"prod_{i}")

    preco = df_estado[df_estado["produto"] == produto]["preco"].values[0]
    unidade = df_estado[df_estado["produto"] == produto]["unidade"].values[0]

    with col2:
        quantidade = st.number_input(f"Qtd ({unidade})", min_value=0.0, step=0.1, key=f"qtd_{i}")

    custo = preco * quantidade

    with col3:
        st.metric("Custo", f"R$ {custo:.2f}")

    itens.append(custo)

# =============================
# RESULTADO
# =============================
total = sum(itens)

st.markdown("---")
st.markdown("## 💰 Resultado do Prato")

st.metric("Custo Total", f"R$ {total:.2f}")

# =============================
# MARGEM
# =============================
st.subheader("📈 Margem de Lucro")

margem = st.slider("Margem (%)", 0, 100, 70)

if total > 0 and margem < 100:
    preco_venda = total / (1 - margem/100)
else:
    preco_venda = 0

st.metric("💵 Preço sugerido", f"R$ {preco_venda:.2f}")

# =============================
# ALERTA INTELIGENTE
# =============================
if total == 0:
    st.warning("⚠️ Informe a quantidade dos ingredientes para calcular o custo.")

# =============================
# BASE
# =============================
with st.expander("📋 Ver base de preços"):
    st.dataframe(df_estado)