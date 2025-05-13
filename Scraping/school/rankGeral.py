import pandas as pd

# Carregar os dados
df = pd.read_excel("C:\\Users\\artio\\Documents\\aaa\\rank.xlsx")

# Filtrar para remover linhas com média = 0 ou índice de segurança ausente ou igual a 0
df = df[(df["media"] > 0) & (df["indice"] > 0)]

# Normalizar a média escolar (quanto maior, melhor)
df["media_norm"] = (df["media"] - df["media"].min()) / (df["media"].max() - df["media"].min())

# Normalizar o índice de segurança (quanto menor, melhor → inverter)
df["seguranca_norm"] = 1 - (df["indice"] - df["indice"].min()) / (df["indice"].max() - df["indice"].min())

# Calcular score combinado (ajustar pesos se quiser)
df["score"] = 0.5 * df["media_norm"] + 0.5 * df["seguranca_norm"]

# Ranking global
df["ranking"] = df["score"].rank(ascending=False, method="min")

# Quartis (1º quartil = melhor grupo)
df["quartil"] = pd.qcut(df["score"], 4, labels=["4º quartil", "3º quartil", "2º quartil", "1º quartil"])

# Ranking distrital (ranking local dentro de cada distrito)
df["ranking_distrital"] = df.groupby("ID_DISTRITO")["score"].rank(ascending=False, method="min")

# Ordenar por distrito e ranking distrital (opcional, apenas para melhor visualização)
df = df.sort_values(["ID_DISTRITO", "ranking_distrital"])

# Guardar o resultado num novo ficheiro Excel
df.to_excel("C:\\Users\\artio\\Documents\\aaa\\rank_completo.xlsx", index=False)
