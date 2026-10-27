
import requests


URL_CONDITION = "http://localhost:8082/fhir/Condition"

HEADERS = {
    "Content-Type": "application/fhir+json",
    "Accept": "application/fhir+json"
}


def cadastrar_conditions(conditions):

    criadas = 0
    existentes = 0

    for condition in conditions:

        # 1. Identifica o paciente e o diagnóstico
        paciente = condition["subject"]["reference"]
        codigo = condition["code"]["coding"][0]["code"]

        # 2. Consulta se a Condition já existe
        resposta_busca = requests.get(
            URL_CONDITION,
            params={
                "subject": paciente,
                "code": f"http://snomed.info/sct|{codigo}"
            },
            headers=HEADERS,
            timeout=30
        )

        resposta_busca.raise_for_status()

        resultado = resposta_busca.json()

        # 3. Verifica se o diagnóstico já está cadastrado
        if resultado.get("total", 0) > 0:

            existentes += 1

            print(
                f"Condition {codigo} já existe "
                f"para {paciente}."
            )

            continue

        # 4. Cadastra a Condition
        resposta_cadastro = requests.post(
            URL_CONDITION,
            json=condition,
            headers=HEADERS,
            timeout=30
        )

        resposta_cadastro.raise_for_status()

        criadas += 1

        print(
            f"Condition {codigo} cadastrada "
            f"para {paciente}."
        )

    # 5. Exibe o resumo
    print("\n===== RESUMO DAS CONDITIONS =====")
    print(f"Conditions criadas: {criadas}")
    print(f"Conditions já existentes: {existentes}")
