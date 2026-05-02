import streamlit as st
import pandas as pd

st.set_page_config(page_title="CMV Inteligente PRO", layout="centered")

st.title("🍽️ CMV Inteligente PRO")

# ==============================
# Upload da planilha
# ==============================
arquivo = st.file_uploader("📂 Envie sua ficha técnica (.xlsx)", type=["xlsx"])

if arquivo:

    try:
        df = pd.read_excel(arquivo)

        # ==============================
        # Normalizar colunas
        # ==============================
        df.columns = df.columns.str.strip().str.lower()

        colunas_esperadas = {'prato', 'ingrediente', 'quantidade', 'unidade', 'custo_unitario'}

        faltando = colunas_esperadas - set(df.columns)

        # ==============================
        # Validação de colunas
        # ==============================
        if faltando:
            st.error(f"❌ Formato inválido. Faltando colunas: {faltando}")
            st.stop()

        # ==============================
        # Validação de dados
        # ==============================
        try:
            df['quantidade'] = pd.to_numeric(df['quantidade'])
            df['custo_unitario'] = pd.to_numeric(df['custo_unitario'])
        except:
            st.error("❌ Valores inválidos em 'quantidade' ou 'custo_unitario'")
            st.stop()

        # remover linhas vazias
        df = df.dropna(subset=['prato', 'ingrediente'])

        # ==============================
        # Cálculo do custo
        # ==============================
        df['custo_total'] = df['quantidade'] * df['custo_unitario']

        resumo = df.groupby('prato')['custo_total'].sum().reset_index()
        resumo = resumo.rename(columns={'custo_total': 'cmv_prato'})

        # ==============================
        # Exibir resultados
        # ==============================
        st.success("✅ Planilha carregada com sucesso!")

        st.subheader("📊 Dados importados")
        st.dataframe(df)

        st.subheader("💰 CMV por prato")
        st.dataframe(resumo)

    except Exception as e:
        st.error(f"❌ Erro ao processar arquivo: {e}")