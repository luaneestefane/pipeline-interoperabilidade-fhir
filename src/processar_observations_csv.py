
from pathlib import Path

import pandas as pd
import requests

from buscar_patient_id import buscar_patient_id
from criar_observation import criar_observation_gestacao


# 1. Configurações
URL_OBSERVATION = "http://localhost:8082/fhir/Observation"

CAMINHO_CSV = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "patients.csv"
)

HEADERS = {
    "Content-Type": "application/fhir+json",
    "Accept": "application/fhir+json"
}


# 2. Leitura do CSV
df = pd.read_csv(
    CAMINHO_CSV,
    encoding="cp1252",
    dtype={"CPF": str}
)


# 3. Contadores
observations_criadas = 0
observations_existentes = 0
erros = 0


print("===== PROCESSAMENTO DAS OBSERVATIONS =====")


# 4. Percorre os pacientes do CSV
for indice, paciente in df.iterrows():

    observacao = paciente["Observação"]

    # Identifica pacientes com informação de gestação
    if not isinstance(observacao, str):
        continue

    termos = [
        termo.strip().lower()
        for termo in observacao.split("|")
    ]

    if "gestante" not in termos:
        continue

    try:
        # 5. Obtém o CPF
        cpf = "".join(
            caractere
            for caractere in str(paciente["CPF"])
            if caractere.isdigit()
        )

        # 6. Busca o ID do paciente no HAPI FHIR
        paciente_id = buscar_patient_id(cpf)

        # 7. Cria a Observation
        observation = criar_observation_gestacao(
            observacao=observacao,
            paciente_id=paciente_id,
            status="unknown"
        )

        # 8. Verifica se já existe
        resposta_busca = requests.get(
            URL_OBSERVATION,
            params={
                "subject": f"Patient/{paciente_id}",
                "code": "http://loinc.org|82810-3",
                "value-concept": "http://snomed.info/sct|77386006"
            },
            headers=HEADERS,
            timeout=30
        )

        resposta_busca.raise_for_status()

        resultado = resposta_busca.json()

        if resultado.get("total", 0) > 0:
            observations_existentes += 1

            print(
                f"Paciente {indice + 1}: "
                "Observation já existente."
            )
            continue

        # 9. Cadastra a Observation
        resposta_cadastro = requests.post(
            URL_OBSERVATION,
            json=observation,
            headers=HEADERS,
            timeout=30
        )

        resposta_cadastro.raise_for_status()

        observations_criadas += 1

        print(
            f"Paciente {indice + 1}: "
            "Observation cadastrada com sucesso!"
        )

    except (requests.RequestException, ValueError, KeyError, TypeError) as excecao:
        erros += 1

        print(
            f"Paciente {indice + 1}: erro - {excecao}"
    )


# 10. Resumo
print("\n===== RESUMO FINAL =====")
print(f"Observations criadas: {observations_criadas}")
print(f"Observations já existentes: {observations_existentes}")
print(f"Pacientes com erros: {erros}")
