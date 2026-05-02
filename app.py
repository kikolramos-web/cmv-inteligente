import streamlit as st
import pandas as pd
from io import BytesIO

st.set_page_config(page_title="CMV Inteligente PRO", layout="centered")

st.title("🍽️ CMV Inteligente PRO")

arquivo = st.file_uploader("📂 Envie sua ficha técnica (.xlsx)", type=["xlsx"])

if arquivo:

    try:
        file_bytes = BytesIO(arquivo.read())
        df = pd.read_excel(file_bytes, engine="openpyxl")

        # ==============================
        # Normalizar colunas
        # ==============================
        df.columns = df.columns.str.strip().str.lower()

        colunas_esperadas = {'prato', 'ingrediente', 'quantidade', 'unidade', 'custo_unitario'}
        faltando = colunas_esperadas - set(df.columns)

        if faltando:
            st.error(f"❌ Faltando colunas: {faltando}")
            st.stop()

        # ==============================
        # Garantir números
        # ==============================
        df['quantidade'] = pd.to_numeric(df['quantidade'], errors='coerce')
        df['custo_unitario'] = pd.to_numeric(df['custo_unitario'], errors='coerce')

        if df[['quantidade', 'custo_unitario']].isnull().any().any():
            st.error("❌ Valores inválidos em quantidade ou custo_unitario")
            st.stop()

        # ==============================
        # Cálculo
        # ==============================
        df['custo_total'] = df['quantidade'] * df['custo_unitario']

        resumo = df.groupby('prato')['custo_total'].sum().reset_index()
        resumo = resumo.rename(columns={'custo_total': 'cmv_prato'})

        # ==============================
        # INPUT DE PREÇO
        # ==============================
        st.subheader("💰 Definir preço de venda")

        preco_venda = st.number_input(
            "Preço de venda por prato (R$)",
            min_value=0.0,
            step=1.0
        )

        if preco_venda > 0:
            resumo['margem_%'] = ((preco_venda - resumo['cmv_prato']) / preco_venda) * 100

            def classificar(m):
                if m < 60:
                    return "🔴 Baixa"
                elif m < 70:
                    return "🟡 Média"
                else:
                    return "🟢 Ideal"

            resumo['status'] = resumo['margem_%'].apply(classificar)

        # ==============================
        # FORMATAR EM R$
        # ==============================
        df['custo_unitario'] = df['custo_unitario'].apply(lambda x: f"R$ {x:,.2f}")
        df['custo_total'] = df['custo_total'].apply(lambda x: f"R$ {x:,.2f}")

        resumo['cmv_prato'] = resumo['cmv_prato'].apply(lambda x: f"R$ {x:,.2f}")

        # ==============================
        # EXIBIÇÃO
        # ==============================
        st.success("✅ Planilha carregada com sucesso!")

        st.subheader("📊 Dados importados")
        st.dataframe(df)

        st.subheader("💰 CMV por prato")
        st.dataframe(resumo)

    except Exception as e:
        st.error(f"❌ Erro ao processar: {e}")