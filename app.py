import streamlit as st
import pandas as pd
import os
import json

st.set_page_config(page_title="CMV Inteligente PRO", layout="centered")

st.title("🍽️ CMV Inteligente PRO")

ARQ_PRECOS = "base_precos.csv"
ARQ_PRATOS = "pratos.csv"


# ---------------------------
# SESSION STATE
# ---------------------------
if "qtd_ingredientes" not in st.session_state:
    st.session_state.qtd_ingredientes = 1

if "modo_edicao" not in st.session_state:
    st.session_state.modo_edicao = False

if "prato_editando" not in st.session_state:
    st.session_state.prato_editando = ""


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


# ---------------------------
# FILTRO POR ESTADO
# ---------------------------
df_estado = df_precos[df_precos["Estado"] == estado]
produtos_lista = sorted(df_estado["Produto"].unique())


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
# EDITAR PRATO
# ---------------------------
st.subheader("✏️ Editar Prato")

if os.path.exists(ARQ_PRATOS):

    try:
        df_pratos_existentes = pd.read_csv(ARQ_PRATOS)

        if not df_pratos_existentes.empty:

            lista_pratos = df_pratos_existentes["Prato"].unique().tolist()

            prato_selecionado = st.selectbox(
                "Selecione um prato salvo",
                [""] + lista_pratos
            )

            if st.button("Carregar Prato"):

                if prato_selecionado:

                    prato_data = df_pratos_existentes[
                        df_pratos_existentes["Prato"] == prato_selecionado
                    ].iloc[0]

                    ingredientes_salvos = json.loads(prato_data["Ingredientes"])

                    st.session_state.qtd_ingredientes = len(ingredientes_salvos)

                    for i, item in enumerate(ingredientes_salvos):
                        st.session_state[f"produto_{i}"] = item["produto"]
                        st.session_state[f"quantidade_{i}"] = item["quantidade"]

                    st.session_state["preco_venda"] = float(prato_data["Venda"])
                    st.session_state["nome_prato"] = prato_data["Prato"]
                    st.session_state["modo_edicao"] = True
                    st.session_state["prato_editando"] = prato_selecionado

                    st.success("✅ Prato carregado com sucesso!")
                    st.rerun()

    except Exception:
        st.warning("Não foi possível carregar pratos salvos.")


# ---------------------------
# MONTAGEM DO PRATO
# ---------------------------
st.subheader("🧾 Montagem do Prato")

qtd = st.number_input(
    "Quantidade de ingredientes",
    1,
    20,
    value=st.session_state.qtd_ingredientes,
    key="qtd_input"
)

st.session_state.qtd_ingredientes = qtd

ingredientes_json = []
custos = []

for i in range(qtd):

    st.markdown(f"### Ingrediente {i + 1}")

    produto_padrao = (
        st.session_state.get(f"produto_{i}", produtos_lista[0])
        if produtos_lista else ""
    )

    if produto_padrao not in produtos_lista and produtos_lista:
        produto_padrao = produtos_lista[0]

    index_produto = (
        produtos_lista.index(produto_padrao)
        if produto_padrao in produtos_lista else 0
    )

    produto = st.selectbox(
        f"Produto {i + 1}",
        produtos_lista,
        index=index_produto,
        key=f"produto_{i}"
    )

    preco_base = float(
        df_estado[df_estado["Produto"] == produto]["Preco"].values[0]
    )

    quantidade = st.number_input(
        f"Quantidade {i + 1}",
        min_value=0.0,
        value=float(st.session_state.get(f"quantidade_{i}", 1.0)),
        key=f"quantidade_{i}"
    )

    custo = preco_base * quantidade

    st.write(f"💰 Preço base: R$ {preco_base:.2f}")
    st.write(f"➡️ Custo: R$ {custo:.2f}")

    ingredientes_json.append({
        "produto": produto,
        "quantidade": quantidade,
        "preco_base": preco_base,
        "custo": round(custo, 2)
    })

    custos.append(custo)


# ---------------------------
# RESULTADO
# ---------------------------
st.subheader("📊 Resultado")

custo_total = sum(custos)

preco_venda = st.number_input(
    "Preço de venda do prato",
    min_value=0.0,
    value=float(st.session_state.get("preco_venda", 0.0)),
    key="preco_venda"
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

nome_prato = st.text_input(
    "Nome do prato",
    value=st.session_state.get("nome_prato", "")
)

if st.button("Salvar Prato"):

    if nome_prato.strip():

        novo_prato = pd.DataFrame({
            "Prato": [nome_prato.strip()],
            "Estado": [estado],
            "Ingredientes": [json.dumps(ingredientes_json)],
            "Custo": [round(custo_total, 2)],
            "Venda": [round(preco_venda, 2)],
            "CMV": [round(cmv, 2)]
        })

        if os.path.exists(ARQ_PRATOS):

            df_existente = pd.read_csv(ARQ_PRATOS)

            if nome_prato.strip() in df_existente["Prato"].values:

                df_existente = df_existente[
                    df_existente["Prato"] != nome_prato.strip()
                ]

                df_final = pd.concat(
                    [df_existente, novo_prato],
                    ignore_index=True
                )

                df_final.to_csv(ARQ_PRATOS, index=False)

            else:

                novo_prato.to_csv(
                    ARQ_PRATOS,
                    mode="a",
                    header=False,
                    index=False
                )

        else:
            novo_prato.to_csv(ARQ_PRATOS, index=False)

        st.success("✅ Prato salvo com sucesso!")

        st.session_state["modo_edicao"] = False
        st.session_state["prato_editando"] = ""

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

            st.dataframe(
                df_hist[["Prato", "Estado", "Custo", "Venda", "CMV"]]
            )

            st.markdown("### 📌 Estatísticas")

            st.write(f"CMV médio: {df_hist['CMV'].mean():.2f}%")
            st.write(f"Custo médio: R$ {df_hist['Custo'].mean():.2f}")

        else:
            st.info("Nenhum prato salvo ainda.")

    except Exception:
        st.warning("Não foi possível ler o histórico.")

else:
    st.info("Nenhum prato salvo ainda.")