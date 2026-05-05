import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="CMV Inteligente PRO", layout="centered")

st.title("🍽️ CMV Inteligente PRO")

ARQ_PRECOS = "base_precos.csv"
ARQ_PRATOS = "pratos.csv"


# ---------------------------
# FUNÇÃO BASE PADRÃO
# ---------------------------
def criar_base_padrao():
    df_init = pd.DataFrame({
        "Estado": [
            "DF", "DF", "DF",
            "SP", "SP", "SP",
            "RJ", "RJ",
            "MG", "MG",
            "BA", "BA",
            "GO", "GO",
            "PR", "PR",
            "SC", "SC",
            "RS", "RS"
        ],
        "Produto": [
            "arroz", "feijao", "frango",
            "arroz", "feijao", "frango",
            "arroz", "carne",
            "feijao", "frango",
            "arroz", "carne",
            "arroz", "frango",
            "feijao", "carne",
            "arroz", "frango",
            "feijao", "carne"
        ],
        "Preco": [
            5.50, 7.00, 12.00,
            5.20, 6.80, 11.50,
            5.80, 26.00,
            6.50, 11.00,
            5.70, 25.50,
            5.40, 11.80,
            6.70, 24.50,
            5.60, 11.30,
            6.90, 25.00
        ]
    })
    df_init.to_csv(ARQ_PRECOS, index=False)
    return df_init


# ---------------------------
# CARREGAR BASE DE PREÇOS
# ---------------------------
if not os.path.exists(ARQ_PRECOS):
    df_precos = criar_base_padrao()
else:
    try:
        df_precos = pd.read_csv(ARQ_PRECOS)

        if df_precos.empty:
            df_precos = criar_base_padrao()

        df_precos.columns = df_precos.columns.str.strip().str.capitalize()

        colunas_esperadas = ["Estado", "Produto", "Preco"]

        if not all(col in df_precos.columns for col in colunas_esperadas):
            df_precos = criar_base_padrao()

    except Exception:
        df_precos = criar_base_padrao()


# ---------------------------
# ESTADO
# ---------------------------
estados = sorted(df_precos["Estado"].unique())
estado = st.selectbox("📍 Selecione o Estado", estados)

df_estado = df_precos[df_precos["Estado"] == estado]


# ---------------------------
# CADASTRAR INGREDIENTE
# ---------------------------
st.subheader("➕ Cadastrar / Atualizar Ingrediente")

col1, col2 = st.columns(2)

with col1:
    novo_produto = st.text_input("Produto")

with col2:
    novo_preco = st.number_input("Preço", min_value=0.0)

if st.button("Salvar Ingrediente"):
    if novo_produto.strip():
        produto_limpo = novo_produto.strip().lower()

        existe = (
            (df_precos["Estado"] == estado) &
            (df_precos["Produto"] == produto_limpo)
        )

        if existe.any():
            df_precos.loc[existe, "Preco"] = novo_preco
        else:
            novo = pd.DataFrame({
                "Estado": [estado],
                "Produto": [produto_limpo],
                "Preco": [novo_preco]
            })
            df_precos = pd.concat([df_precos, novo], ignore_index=True)

        df_precos.to_csv(ARQ_PRECOS, index=False)

        st.success("✅ Ingrediente salvo com sucesso!")
        st.rerun()
    else:
        st.warning("Digite o nome do produto.")


# ---------------------------
# MONTAGEM DO PRATO
# ---------------------------
st.subheader("🧾 Montagem do Prato")

qtd = st.number_input("Quantidade de ingredientes", 1, 10, 1)

ingredientes = []
custos = []

produtos_lista = sorted(df_estado["Produto"].unique())

for i in range(qtd):
    st.markdown(f"### Ingrediente {i + 1}")

    produto = st.selectbox(
        f"Produto {i + 1}",
        produtos_lista,
        key=f"produto_{i}"
    )

    preco_base = float(
        df_estado[df_estado["Produto"] == produto]["Preco"].values[0]
    )

    quantidade = st.number_input(
        f"Quantidade {i + 1}",
        min_value=0.0,
        value=1.0,
        key=f"quantidade_{i}"
    )

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

preco_venda = st.number_input(
    "Preço de venda do prato",
    min_value=0.0,
    value=0.0
)

cmv = (custo_total / preco_venda * 100) if preco_venda > 0 else 0

st.markdown(f"### 💵 Custo Total: R$ {custo_total:.2f}")
st.markdown(f"### 📈 CMV: {cmv:.2f}%")

if custo_total > 0:
    preco_ideal = custo_total / 0.40
    st.info(f"💡 Preço sugerido para CMV de 40%: R$ {preco_ideal:.2f}")

if cmv > 60:
    st.error("⚠️ CMV muito alto.")
elif cmv > 40:
    st.warning("⚠️ CMV moderado.")
elif cmv > 0:
    st.success("🔥 Excelente margem!")


# ---------------------------
# SALVAR PRATO
# ---------------------------
st.subheader("💾 Salvar Prato")

nome_prato = st.text_input("Nome do prato")

if st.button("Salvar Prato"):
    if nome_prato.strip():
        novo_prato = pd.DataFrame({
            "Prato": [nome_prato.strip()],
            "Estado": [estado],
            "Custo": [round(custo_total, 2)],
            "Venda": [round(preco_venda, 2)],
            "CMV": [round(cmv, 2)]
        })

        if os.path.exists(ARQ_PRATOS):
            novo_prato.to_csv(
                ARQ_PRATOS,
                mode="a",
                header=False,
                index=False
            )
        else:
            novo_prato.to_csv(ARQ_PRATOS, index=False)

        st.success("✅ Prato salvo com sucesso!")
    else:
        st.warning("Digite o nome do prato.")


# ---------------------------
# HISTÓRICO
# ---------------------------
st.subheader("📚 Histórico de Pratos")

if os.path.exists(ARQ_PRATOS):
    try:
        df_hist = pd.read_csv(ARQ_PRATOS)

        if not df_hist.empty:
            st.dataframe(df_hist)

            st.markdown("### 📌 Estatísticas")

            st.write(f"CMV médio: {df_hist['CMV'].mean():.2f}%")
            st.write(f"Custo médio: R$ {df_hist['Custo'].mean():.2f}")
        else:
            st.info("Nenhum prato salvo ainda.")
    except Exception:
        st.warning("Não foi possível ler o histórico.")
else:
    st.info("Nenhum prato salvo ainda.")