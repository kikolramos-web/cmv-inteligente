import pandas as pd
import streamlit as st

st.set_page_config(page_title="CMV Inteligente", layout="centered")

st.title("📊 CMV Inteligente")

# =============================
# CARREGAR BASE DE PREÇOS
# =============================
try:
    df = pd.read_csv("precos.csv")
except:
    st.error("Erro ao carregar o arquivo precos.csv")
    st.stop()

# =============================
# FILTRO POR ESTADO
# =============================
estado = st.selectbox("Selecione o Estado", df["estado"].unique())

df_estado = df[df["estado"] == estado]

# =============================
# FILTRO POR PRODUTO
# =============================
produto = st.selectbox("Selecione o Produto", df_estado["produto"].unique())

dados_produto = df_estado[df_estado["produto"] == produto].iloc[0]

preco = dados_produto["preco"]
unidade = dados_produto["unidade"]

# =============================
# ENTRADA DE QUANTIDADE
# =============================
st.subheader("📦 Cálculo de Custo")

quantidade = st.number_input(
    f"Quantidade em ({unidade})",
    min_value=0.0,
    step=0.1
)

# =============================
# CÁLCULO DO CUSTO
# =============================
custo = preco * quantidade

st.markdown("### 💰 Resultado")

st.write(f"**Produto:** {produto}")
st.write(f"**Preço unitário:** R$ {preco:.2f} por {unidade}")
st.write(f"**Quantidade:** {quantidade} {unidade}")
st.write(f"**Custo total:** R$ {custo:.2f}")

# =============================
# MOSTRAR BASE (OPCIONAL)
# =============================
with st.expander("📋 Ver base de preços"):
    st.dataframe(df_estado)