
# Códigos SNOMED CT identificados no SHRIMP
CONDICOES = {
    "diabético": {
        "code": "73211009",
        "display": "Diabetes mellitus"
    },
    "hipertenso": {
        "code": "38341003",
        "display": "Hypertensive disorder"
    }
}


def criar_conditions(observacao, paciente_id):
    conditions = []

    if not isinstance(observacao, str) or not observacao.strip():
        return conditions

    # Separa observações como "Diabético|Hipertenso"
    termos = observacao.split("|")

    for termo in termos:
        termo = termo.strip().lower()

        if termo not in CONDICOES:
            continue

        conceito = CONDICOES[termo]

        condition = {
            "resourceType": "Condition",
            "code": {
                "coding": [
                    {
                        "system": "http://snomed.info/sct",
                        "code": conceito["code"],
                        "display": conceito["display"]
                    }
                ]
            },
            "subject": {
                "reference": f"Patient/{paciente_id}"
            }
        }

        conditions.append(condition)

    return conditions

import json

if __name__ == "__main__":
    resultado = criar_conditions(
        observacao="Diabético|Hipertenso",
        paciente_id="123"
    )

    print(json.dumps(resultado, indent=2, ensure_ascii=False))
    print(f"\nTotal de condições criadas: {len(resultado)}")
