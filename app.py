import streamlit as st
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