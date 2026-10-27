
import json

from buscar_patient_id import buscar_patient_id
from criar_condition import criar_conditions
from cadastrar_conditions import cadastrar_conditions


# 1. CPF fictício do paciente
cpf = "12345678900"

# 2. Busca o ID no HAPI FHIR
paciente_id = buscar_patient_id(cpf)

# 3. Define condições clínicas de exemplo
observacao = "Diabético|Hipertenso"

# 4. Cria os recursos Condition
conditions = criar_conditions(
    observacao,
    paciente_id
)

# 5. Exibe os resultados
print(f"CPF: {cpf}")
print(f"Patient ID: {paciente_id}")

print("\n===== CONDITIONS GERADAS =====")

for condition in conditions:
    print(json.dumps(
        condition,
        indent=2,
        ensure_ascii=False
    ))

print(f"\nTotal de Conditions: {len(conditions)}")

import requests

URL_VALIDACAO = "http://localhost:8082/fhir/Condition/$validate"

print("\n===== VALIDAÇÃO DAS CONDITIONS =====")

for condition in conditions:

    resposta = requests.post(
        URL_VALIDACAO,
        json=condition,
        headers={
            "Content-Type": "application/fhir+json",
            "Accept": "application/fhir+json"
        },
        timeout=30
    )

    resultado = resposta.json()

    diagnostico = condition["code"]["coding"][0]["display"]

    print(f"\nDiagnóstico: {diagnostico}")
    print(f"HTTP: {resposta.status_code}")

    for issue in resultado.get("issue", []):
        print(f"Severidade: {issue.get('severity')}")
        print(f"Mensagem: {issue.get('diagnostics', '')}")
# 6. Cadastra as Conditions no HAPI FHIR
print("\n===== CADASTRO DAS CONDITIONS =====")

cadastrar_conditions(conditions)