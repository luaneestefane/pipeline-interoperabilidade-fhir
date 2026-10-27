
import pandas as pd
import json
from pathlib import Path

from criar_patient import criar_patient


# Localiza o arquivo CSV
caminho_csv = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "patients.csv"
)

# Lê os pacientes
df = pd.read_csv(caminho_csv, encoding="cp1252")

total_criados = 0
total_erros = 0

# Percorre todos os pacientes
for indice, paciente in df.iterrows():

    try:
        # Converte a linha do CSV em Patient FHIR
        patient_fhir = criar_patient(paciente)

        total_criados += 1

        # Mostra o primeiro Patient como exemplo
        if total_criados == 1:
            print("\n===== EXEMPLO DE PATIENT FHIR =====")
            print(
                json.dumps(
                    patient_fhir,
                    indent=2,
                    ensure_ascii=False
                )
            )

    except Exception as erro:
        total_erros += 1

        print(
            f"Erro na linha {indice + 1}: {erro}"
        )

# Resumo final
print("\n===== RESUMO DO TESTE =====")
print(f"Total de pacientes no CSV: {len(df)}")
print(f"Patients gerados: {total_criados}")
print(f"Erros encontrados: {total_erros}")
