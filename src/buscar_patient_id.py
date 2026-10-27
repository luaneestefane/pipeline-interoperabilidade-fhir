
import requests


URL_PATIENT = "http://localhost:8082/fhir/Patient"


def buscar_patient_id(cpf):

    # 1. Consulta o paciente pelo CPF
    resposta = requests.get(
        URL_PATIENT,
        params={"identifier": cpf},
        headers={"Accept": "application/fhir+json"},
        timeout=30
    )

    # 2. Verifica se a consulta foi bem-sucedida
    resposta.raise_for_status()

    # 3. Converte a resposta JSON em um dicionário Python
    resultado = resposta.json()

    # 4. Obtém a lista de pacientes encontrados
    pacientes = resultado.get("entry", [])

    # 5. Verifica se encontrou exatamente um paciente
    if len(pacientes) != 1:
        raise ValueError(
            f"CPF {cpf}: encontrados {len(pacientes)} pacientes."
        )

    # 6. Obtém o ID do Patient no HAPI FHIR
    paciente_id = pacientes[0]["resource"]["id"]

    # 7. Devolve o ID encontrado
    return paciente_id
if __name__ == "__main__":

    cpf = "12345678900"

    paciente_id = buscar_patient_id(cpf)

    print(f"CPF pesquisado: {cpf}")
    print(f"ID encontrado no HAPI FHIR: {paciente_id}")