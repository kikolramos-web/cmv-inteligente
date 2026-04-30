# =========================
# MODO MANUAL (ATUALIZADO)
# =========================
if opcao == "Manual":
    st.header("🧾 Montagem do Prato")

    estado = st.selectbox("Selecione o Estado", estados)

    num_ingredientes = st.number_input(
        "Quantidade de ingredientes",
        min_value=1,
        max_value=50,
        value=1
    )

    ingredientes = []

    unidades = ["kg", "g", "L", "ml", "un"]

    for i in range(int(num_ingredientes)):
        st.subheader(f"Ingrediente {i+1}")

        nome = st.selectbox(
            f"Produto {i+1}",
            options=[""] + produtos_base,
            key=f"nome_{i}"
        )

        unidade = st.selectbox(
            f"Unidade {i+1}",
            unidades,
            key=f"unidade_{i}"
        )

        quantidade = st.number_input(
            f"Quantidade {i+1}",
            min_value=0.0,
            step=0.01,
            key=f"qtd_{i}"
        )

        # =========================
        # CONVERSÃO
        # =========================
        if unidade == "g":
            quantidade_convertida = quantidade / 1000
        elif unidade == "ml":
            quantidade_convertida = quantidade / 1000
        else:
            quantidade_convertida = quantidade

        preco_auto = None
        if nome:
            preco_auto = buscar_preco(nome, estado, df_precos)

        # =========================
        # PREÇO COM R$
        # =========================
        if preco_auto:
            st.success(f"💰 Preço automático: {formatar_real(preco_auto)}")
            preco = preco_auto
        else:
            preco = st.number_input(
                f"Preço unitário {i+1} (R$)",
                min_value=0.0,
                step=0.01,
                key=f"preco_{i}"
            )
            st.caption(f"Valor informado: {formatar_real(preco)}")

        if nome:
            ingredientes.append({
                "produto": nome,
                "quantidade": quantidade_convertida,
                "preco": preco,
                "unidade": unidade
            })

    if st.button("Calcular CMV"):
        if ingredientes:
            df = pd.DataFrame(ingredientes)
            df["custo"] = df["quantidade"] * df["preco"]

            custo_total = df["custo"].sum()

            st.subheader("📊 Resultado")
            st.dataframe(df)

            st.success(f"💰 Custo total: {formatar_real(custo_total)}")

            # PORÇÃO
            porcoes = st.number_input("Número de porções", min_value=1, value=1)
            custo_por_porcao = custo_total / porcoes

            st.write(f"🍽️ Custo por porção: {formatar_real(custo_por_porcao)}")

            # CMV
            cmv_percentual = st.slider("CMV desejado (%)", 10, 80, 30)
            cmv = cmv_percentual / 100

            preco_venda = custo_total / cmv

            st.info(f"💡 Preço de venda: {formatar_real(preco_venda)}")

            # INDICADOR
            if cmv <= 0.30:
                st.success("🟢 CMV saudável")
            elif cmv <= 0.50:
                st.warning("🟡 CMV médio")
            else:
                st.error("🔴 CMV alto")

        else:
            st.warning("Adicione ingredientes.")