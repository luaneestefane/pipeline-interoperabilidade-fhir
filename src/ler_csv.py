
from pathlib import Path
import pandas as pd

# Localiza a pasta principal do projeto
PASTA_PROJETO = Path(__file__).resolve().parent.parent

# Localiza o arquivo CSV
CAMINHO_CSV = PASTA_PROJETO / "data" / "patients.csv"

# Lê o CSV utilizando Pandas
df = pd.read_csv(CAMINHO_CSV, encoding="cp1252")

# Exibe informações dos dados
print("Quantidade de registros:", len(df))

print("\nColunas encontradas:")
print(df.columns.tolist())

print("\nPrimeiros 5 registros:")
print(df.head())
