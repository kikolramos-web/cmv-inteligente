import pandas as pd

BASE_PRECOS = {
    "file de frango": [16.5, 18.9, 17.8, 19.2],
    "arroz tipo 1": [5.5, 6.2, 6.8],
    "tomate": [4.0, 5.5, 6.0],
    "oleo de soja": [6.5, 7.2, 8.0]
}

def buscar_preco_medio(produto):
    produto = produto.lower()
    if produto in BASE_PRECOS:
        valores = BASE_PRECOS[produto]
        return round(sum(valores) / len(valores), 2)
    return None

df = pd.read_excel("cardapio.xlsx")

resultados = []

for prato in df["Prato"].unique():
    df_prato = df[df["Prato"] == prato]

    custo_total = 0

    for _, row in df_prato.iterrows():
        preco = buscar_preco_medio(row["Ingrediente"])
        if preco is None:
            continue

        preco_unitario = preco / 1000
        custo = preco_unitario * row["Quantidade"]
        custo_total += custo

    preco_venda = custo_total / (1 - 0.7)

    resultados.append({
        "Prato": prato,
        "CMV": round(custo_total, 2),
        "Preço Sugerido": round(preco_venda, 2)
    })

df_final = pd.DataFrame(resultados)
df_final.to_excel("resultado_cardapio.xlsx", index=False)

print("Cardápio calculado com sucesso!")
