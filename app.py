import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="CMV Inteligente", layout="wide")

# 🎨 ESTILO
st.markdown("""
<style>
body {background-color: #0e1117;}
h1, h2, h3, h4 {color: #ffffff;}
[data-testid="metric-container"] {
    background-color: #1c1f26;
    border-radius: 12px;
    padding: 15px;
}
.stDownloadButton>button {
    background-color: #00c853;
    color: white;
    border-radius: 8px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# HEADER
st.markdown("## 🍽️ CMV Inteligente")
st.markdown("##### Precificação profissional de cardápios em segundos")
st.divider()

# UPLOAD
arquivo = st.file_uploader("📂 Envie seu Excel", type=["xlsx"])

col1, col2 = st.columns(2)

with col1:
    margem = st.slider("💰 Margem de lucro", 0.3, 0.9, 0.7, step=0.01)
    st.caption(f"Margem atual: **{int(margem*100)}%**")

with col2:
    st.info("💡 Pode usar nomes flexíveis nas colunas")

# 🔧 Função para identificar colunas automaticamente
def identificar_coluna(colunas, opcoes):
    for c in colunas:
        nome = c.lower().replace(" ", "").replace("ç", "c")
        for op in opcoes:
            if op in nome:
                return c
    return None

# PROCESSAMENTO
if arquivo:
    with st.spinner("🔄 Processando..."):

        xls = pd.ExcelFile(arquivo)
        abas = xls.sheet_names

        st.caption(f"Abas encontradas: {', '.join(abas)}")

        df_cardapio = None
        df_precos = None

        # 🔍 IDENTIFICAR ABAS
        for aba in abas:
            df_temp = pd.read_excel(arquivo, sheet_name=aba)
            colunas = [c.lower() for c in df_temp.columns]

            if "prato" in colunas and "ingrediente" in colunas:
                df_cardapio = df_temp

            if "ingrediente" in colunas and any("preco" in c or "valor" in c for c in colunas):
                df_precos = df_temp

        if df_cardapio is None:
            st.error("❌ Não encontrei dados de cardápio")
            st.stop()

        if df_precos is None:
            st.error("❌ Não encontrei base de preços")
            st.stop()

        # 🔎 IDENTIFICAR COLUNAS
        col_ing_card = identificar_coluna(df_cardapio.columns, ["ingrediente"])
        col_qtd = identificar_coluna(df_cardapio.columns, ["quantidade", "qtd"])
        col_prato = identificar_coluna(df_cardapio.columns, ["prato"])

        col_ing_preco = identificar_coluna(df_precos.columns, ["ingrediente"])
        col_preco = identificar_coluna(df_precos.columns, ["preco", "valor", "custo"])

        if None in [col_ing_card, col_qtd, col_prato, col_ing_preco, col_preco]:
            st.error("❌ Não consegui identificar todas as colunas automaticamente")
            st.stop()

        # BASE DINÂMICA
        BASE_PRECOS = {
            str(row[col_ing_preco]).lower().strip(): row[col_preco]
            for _, row in df_precos.iterrows()
        }

        def buscar_preco(produto):
            return BASE_PRECOS.get(str(produto).lower().strip())

        resultados = []
        detalhes = []
        sem_preco = set()

        for prato in df_cardapio[col_prato].unique():
            df_prato = df_cardapio[df_cardapio[col_prato] == prato]
            custo_total = 0

            for _, row in df_prato.iterrows():
                preco = buscar_preco(row[col_ing_card])

                if preco:
                    custo = (preco / 1000) * row[col_qtd]
                    custo_total += custo

                    detalhes.append({
                        "Prato": prato,
                        "Ingrediente": row[col_ing_card],
                        "Quantidade": row[col_qtd],
                        "Custo (R$)": round(custo, 2)
                    })
                else:
                    sem_preco.add(row[col_ing_card])

            if custo_total == 0:
                continue

            preco_venda = custo_total / (1 - margem)
            cmv = custo_total / preco_venda

            if cmv > 0.4:
                status = "🔴 CMV Alto"
            elif cmv > 0.3:
                status = "🟡 Atenção"
            else:
                status = "🟢 Saudável"

            resultados.append({
                "Prato": prato,
                "CMV (R$)": round(custo_total, 2),
                "Preço Sugerido (R$)": round(preco_venda, 2),
                "CMV (%)": cmv,
                "Status": status
            })

        df_resultado = pd.DataFrame(resultados)
        df_detalhes = pd.DataFrame(detalhes)

    if sem_preco:
        st.warning(f"⚠️ Sem preço: {', '.join(sem_preco)}")

    st.markdown("### 📊 Resultados")
    st.dataframe(
        df_resultado.style.format({
            "CMV (R$)": "R$ {:.2f}",
            "Preço Sugerido (R$)": "R$ {:.2f}",
            "CMV (%)": "{:.1%}"
        }),
        use_container_width=True
    )

    st.markdown("### 🧾 Detalhes")
    st.dataframe(df_detalhes, use_container_width=True)

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df_resultado.to_excel(writer, index=False, sheet_name='Resultado')
        df_detalhes.to_excel(writer, index=False, sheet_name='Detalhes')

    st.download_button("📥 Baixar Excel", buffer.getvalue(), "cmv_resultado.xlsx")