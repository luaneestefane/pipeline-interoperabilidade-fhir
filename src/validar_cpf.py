
import re


def validar_cpf(cpf):
    cpf = re.sub(r"\D", "", str(cpf))

    if len(cpf) != 11 or len(set(cpf)) == 1:
        return False

    for tamanho in (9, 10):
        soma = sum(
            int(cpf[i]) * (tamanho + 1 - i)
            for i in range(tamanho)
        )

        digito = (soma * 10) % 11

        if digito == 10:
            digito = 0

        if digito != int(cpf[tamanho]):
            return False

    return True

import pandas as pd
from pathlib import Path

# Localiza o CSV dentro do projeto
caminho_csv = Path(__file__).resolve().parent.parent / "data" / "patients.csv"

# Lê os CPFs como texto para preservar zeros à esquerda
df = pd.read_csv(caminho_csv, encoding="cp1252", dtype={"CPF": str})

# Verifica cada CPF
df["CPF_valido"] = df["CPF"].apply(validar_cpf)

# Exibe os resultados
print("Total de pacientes:", len(df))
print("CPFs válidos:", df["CPF_valido"].sum())
print("CPFs inválidos:", (~df["CPF_valido"]).sum())

# Mostra as linhas com CPF inválido
print("\nRegistros com CPF inválido:")
print(df.loc[~df["CPF_valido"], ["Nome", "CPF"]].to_string(index=False))
