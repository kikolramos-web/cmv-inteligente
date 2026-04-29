import pandas as pd
import streamlit as st

st.set_page_config(page_title="CMV Inteligente", layout="centered")

st.title("📊 CMV Inteligente")

# =============================
# CARREGAR BASE DE PREÇOS (SUPER ROBUSTO)
# =============================
try:
    df = pd.read_csv("precos.csv", sep=None, engine="python")

    # se veio tudo em uma coluna só, separa manualmente
    if len(df.columns) == 1:
        df = df[df.columns[0]].str.split(",", expand=True)
        df.columns = [
            "produto","categoria","preco","unidade",
            "estado","cidade","fornecedor","data"
        ]

    # padroniza nomes
    df.columns = df.columns.str.strip().str.lower()

except Exception as e:
    st.error("Erro ao carregar o arquivo precos.csv")
    st.write(e)
    st.stop()

# =============================
# VALIDAR COLUNAS
# =============================
colunas_necessarias = ["produto", "preco", "unidade", "estado"]

for col in colunas_necessarias:
    if col not in df.columns:
        st.error(f"Coluna obrigatória não encontrada: {col}")
        st.write("Colunas encontradas:", df.columns)
        st.stop()

# =============================
# LIMPAR DADOS
# =============================
df = df.dropna(subset=["produto", "preco", "estado"])

# garantir tipos corretos
df["preco"] = df["preco"].astype(float)

# =============================
# FILTRO POR ESTADO
# =============================
estado = st.selectbox("Selecione o Estado", sorted(df["estado"].unique()))

df_estado = df[df["estado"] == estado]

# =============================
# FILTRO POR PRODUTO
# =============================
produto = st.selectbox("Selecione o Produto", sorted(df_estado["produto"].unique()))

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
# CÁLCULO
# =============================
custo = preco * quantidade

st.markdown("### 💰 Resultado")

st.write(f"**Produto:** {produto}")
st.write(f"**Preço unitário:** R$ {preco:.2f} por {unidade}")
st.write(f"**Quantidade:** {quantidade} {unidade}")
st.write(f"**Custo total:** R$ {custo:.2f}")

# =============================
# BASE DE DADOS
# =============================
with st.expander("📋 Ver base de preços"):
    st.dataframe(df_estado)