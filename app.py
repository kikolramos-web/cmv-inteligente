import pandas as pd
import streamlit as st

st.set_page_config(page_title="CMV Inteligente", layout="centered")

st.title("📊 CMV Inteligente")

# =============================
# CARREGAR CSV (FORÇADO E SEGURO)
# =============================
try:
    try:
        df = pd.read_csv("precos.csv", sep=",")
        if len(df.columns) == 1:
            raise Exception("Separador errado")
    except:
        df = pd.read_csv("precos.csv", sep=";")

    # padronizar colunas
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
# LIMPEZA
# =============================
df = df.dropna(subset=["produto", "preco", "estado"])
df["preco"] = df["preco"].astype(float)

# =============================
# FILTRO
# =============================
estado = st.selectbox("Selecione o Estado", sorted(df["estado"].unique()))
df_estado = df[df["estado"] == estado]

produto = st.selectbox("Selecione o Produto", sorted(df_estado["produto"].unique()))
dados = df_estado[df_estado["produto"] == produto].iloc[0]

preco = dados["preco"]
unidade = dados["unidade"]

# =============================
# ENTRADA
# =============================
quantidade = st.number_input(f"Quantidade ({unidade})", min_value=0.0, step=0.1)

# =============================
# RESULTADO
# =============================
custo = preco * quantidade

st.markdown("### 💰 Resultado")
st.write(f"Produto: {produto}")
st.write(f"Preço: R$ {preco:.2f} por {unidade}")
st.write(f"Quantidade: {quantidade}")
st.write(f"Custo total: R$ {custo:.2f}")

# =============================
# BASE
# =============================
with st.expander("Ver base"):
    st.dataframe(df_estado)