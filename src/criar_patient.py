
from datetime import datetime
import pandas as pd


def criar_patient(paciente):

    # 1. Nome completo
    nome = str(paciente["Nome"]).strip()

    # 2. CPF: mantém somente os números
    cpf = "".join(
        caractere
        for caractere in str(paciente["CPF"])
        if caractere.isdigit()
    )

    # 3. Gênero
    generos = {
        "masculino": "male",
        "feminino": "female"
    }

    genero_csv = str(paciente["Gênero"]).strip().lower()
    genero_fhir = generos.get(genero_csv, "unknown")

    # 4. Data de nascimento
    data_nascimento = datetime.strptime(
        str(paciente["Data de Nascimento"]).strip(),
        "%d/%m/%Y"
    ).strftime("%Y-%m-%d")

    # 5. Telefone
    telefone = str(paciente["Telefone"]).strip()

    # 6. País de nascimento
    pais = str(paciente["País de Nascimento"]).strip().lower()

    if pais not in ("brasil", "brazil"):
        raise ValueError(
            f"País de nascimento não mapeado: {pais}"
        )

    # 7. Recurso FHIR Patient
    patient = {
        "resourceType": "Patient",

        "identifier": [
            {
                "type": {
                    "coding": [
                        {
                            "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
                            "code": "TAX",
                            "display": "Tax ID number"
                        }
                    ]
                },
                "value": cpf
            }
        ],

        "name": [
            {
                "text": nome
            }
        ],

        "gender": genero_fhir,

        "birthDate": data_nascimento,

        "telecom": [
            {
                "system": "phone",
                "value": telefone
            }
        ],

        "extension": [
            {
                "url": "http://www.saude.gov.br/fhir/r4/StructureDefinition/BRPais-1.0",
                "valueCodeableConcept": {
                    "coding": [
                        {
                            "system": "http://www.saude.gov.br/fhir/r4/CodeSystem/BRPais",
                            "code": "10",
                            "display": "BRASIL"
                        }
                    ]
                }
            }
        ]
    }

    return patient
