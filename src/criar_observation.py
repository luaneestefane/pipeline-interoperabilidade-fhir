
def criar_observation_gestacao(observacao, paciente_id, status=None):
    # Verifica se existe informação clínica
    if not isinstance(observacao, str) or not observacao.strip():
        return None

    # Separa observações combinadas por |
    termos = [
        termo.strip().lower()
        for termo in observacao.split("|")
    ]

    # Só cria Observation quando houver "Gestante"
    if "gestante" not in termos:
        return None

    # O status precisa ser definido antes da criação
    if status is None:
        raise ValueError(
            "Defina o status da Observation antes de criá-la."
        )

    observation = {
        "resourceType": "Observation",
        "status": status,
        "code": {
            "coding": [
                {
                    "system": "http://loinc.org",
                    "code": "82810-3",
                    "display": "Pregnancy status"
                }
            ]
        },
        "subject": {
            "reference": f"Patient/{paciente_id}"
        },
        "valueCodeableConcept": {
            "coding": [
                {
                    "system": "http://snomed.info/sct",
                    "code": "77386006",
                    "display": "Pregnant"
                }
            ]
        }
    }

    return observation

import json

if __name__ == "__main__":
    resultado = criar_observation_gestacao(
        observacao="Gestante|Diabético",
        paciente_id="123",
        status="unknown"
    )

    print(json.dumps(resultado, indent=2, ensure_ascii=False))

