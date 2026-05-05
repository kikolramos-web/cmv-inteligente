import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="CMV Inteligente PRO", layout="centered")

st.title("🍽️ CMV Inteligente PRO")

# ---------------------------
# ARQUIVOS
# ---------------------------
ARQ_PRECOS = "base_precos.csv"
ARQ_PRATOS = "pratos.csv"

# ---------------------------
# CRIAR BASE INICIAL
# ---------------------------
if not os.path.exists(ARQ_PRECOS):
    df_init = pd.DataFrame({
        "Estado": ["DF","DF","SP","SP","RJ","MG"],
        "Produto": ["arroz","feijao","arroz","frango","carne","frango"],
        "Preco": [5.5,7.0,5.2,11.5,26.0,11.0]
    })
    df_init.to_csv(ARQ_PRECOS, index=False)

df_precos = pd.read_csv(ARQ_PRECOS)

# ---------------------------
# ESTADO
# ---------------------------
estados = sorted(df_precos["Estado"].unique())
estado = st.selectbox("📍 Selecione o Estado", estados)

df_estado = df_precos[df_precos["Estado"] == estado]

# ---------------------------
# CADASTRO DE INGREDIENTE
# ---------------------------
st.subheader("➕ Cadastrar / Atualizar Ingrediente")

col1, col2 = st.columns(2)

with col1:
    novo_produto = st.text_input("Produto")

with col2:
    novo_preco = st.number_input("Preço", min_value=0.0)

if st.button("Salvar Ingrediente"):
    if novo_produto:
        novo = pd.DataFrame({
            "Estado":[estado],
            "Produto":[novo_produto.lower()],
            "Preco":[novo_preco]
        })

        df_precos = pd.concat([df_precos, novo], ignore_index=True)
        df_precos.to_csv(ARQ_PRECOS, index=False)

        st.success("✅ Ingrediente salvo!")
        st.rerun()
    else:
        st.warning("Digite um produto")

# ---------------------------
# MONTAGEM DO PRATO
# ---------------------------
st.subheader("🧾 Montagem do Prato")

qtd = st.number_input("Quantidade de ingredientes", 1, 10, 1)

ingredientes = []
custos = []

for i in range(qtd):
    st.markdown(f"### Ingrediente {i+1}")

    produtos_lista = df_estado["Produto"].unique()

    produto = st.selectbox(f"Produto {i+1}", produtos_lista, key=f"prod_{i}")

    preco_base = df_estado[df_estado["Produto"] == produto]["Preco"].values[0]

    quantidade = st.number_input(f"Quantidade {i+1}", min_value=0.0, value=1.0, key=f"qtd_{i}")

    custo = preco_base * quantidade

    st.write(f"💰 Preço base: R$ {preco_base:.2f}")
    st.write(f"➡️ Custo: R$ {custo:.2f}")

    ingredientes.append(produto)
    custos.append(custo)

# ---------------------------
# RESULTADO
# ---------------------------
st.subheader("📊 Resultado")

custo_total = sum(custos)

preco_venda = st.number_input("Preço de venda", min_value=0.0)

cmv = (custo_total / preco_venda * 100) if preco_venda > 0 else 0

st.markdown(f"### 💵 Custo Total: R$ {custo_total:.2f}")
st.markdown(f"### 📈 CMV: {cmv:.2f}%")

# Sugestão inteligente
if custo_total > 0:
    preco_ideal = custo_total / 0.4  # alvo CMV 40%
    st.info(f"💡 Preço sugerido (CMV 40%): R$ {preco_ideal:.2f}")

if cmv > 60:
    st.error("⚠️ CMV alto!")
elif cmv > 40:
    st.warning("⚠️ CMV médio")
elif cmv > 0:
    st.success("🔥 CMV saudável")

# ---------------------------
# SALVAR PRATO
# ---------------------------
st.subheader("💾 Salvar Prato")

nome = st.text_input("Nome do prato")

if st.button("Salvar Prato"):
    if nome:
        novo_prato = pd.DataFrame({
            "Prato":[nome],
            "Estado":[estado],
            "Custo":[custo_total],
            "Venda":[preco_venda],
            "CMV":[cmv]
        })

        if os.path.exists(ARQ_PRATOS):
            novo_prato.to_csv(ARQ_PRATOS, mode='a', header=False, index=False)
        else:
            novo_prato.to_csv(ARQ_PRATOS, index=False)

        st.success("✅ Prato salvo!")
    else:
        st.warning("Digite o nome")

# ---------------------------
# HISTÓRICO
# ---------------------------
st.subheader("📚 Histórico")

if os.path.exists(ARQ_PRATOS):
    df_hist = pd.read_csv(ARQ_PRATOS)

    st.dataframe(df_hist)

    if st.button("📊 Ver Estatísticas"):
        st.write("Média CMV:", df_hist["CMV"].mean())
        st.write("Custo médio:", df_hist["Custo"].mean())
else:
    st.info("Sem dados ainda")