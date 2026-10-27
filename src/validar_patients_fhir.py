
import pandas as pd
import requests
from pathlib import Path

from criar_patient import criar_patient


# 1. Endereço do servidor HAPI FHIR
URL_VALIDACAO = "http://localhost:8082/fhir/Patient/$validate"

# 2. Localiza o CSV
caminho_csv = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "patients.csv"
)

# 3. Lê os pacientes
df = pd.read_csv(caminho_csv, encoding="cp1252")

validos = 0
invalidos = 0

# 4. Percorre os 50 pacientes
for indice, paciente in df.iterrows():

    try:
        # Converte a linha do CSV em Patient FHIR
        patient_json = criar_patient(paciente)

        # Envia o recurso para validação no HAPI FHIR
        resposta = requests.post(
            URL_VALIDACAO,
            json=patient_json,
            headers={
                "Content-Type": "application/fhir+json",
                "Accept": "application/fhir+json"
            },
            timeout=30
        )

        # A resposta deve ser um OperationOutcome
        resposta.raise_for_status()
        resultado = resposta.json()

        if resultado.get("resourceType") != "OperationOutcome":
            raise ValueError(
                "Resposta inesperada do servidor FHIR."
            )

        # Verifica se existem erros de validação
        problemas = resultado.get("issue", [])

        erros = [
            problema
            for problema in problemas
            if problema.get("severity") in ("error", "fatal")
        ]

        if erros:
            invalidos += 1
            print(f"\nPaciente da linha {indice + 1}: INVÁLIDO")

            for erro in erros:
                print(erro.get("diagnostics", erro.get("code")))
        else:
            validos += 1

    except Exception as erro:
        invalidos += 1
        print(f"\nFalha na linha {indice + 1}: {erro}")

# 5. Resumo
print("\n===== VALIDAÇÃO HAPI FHIR R4 =====")
print(f"Total de pacientes: {len(df)}")
print(f"Patients sem erros de validação: {validos}")
print(f"Patients com erros ou falhas: {invalidos}")
