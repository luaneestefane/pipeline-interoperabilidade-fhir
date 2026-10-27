
import json
import requests

from kafka import KafkaConsumer
from kafka.errors import KafkaError


# 1. Configurações do Kafka
SERVIDOR_KAFKA = "localhost:9092"
TOPICO = "pacientes-fhir"

# 2. Endereço do HAPI FHIR
URL_PATIENT = "http://localhost:8082/fhir/Patient"


# 3. Cria o Consumer
consumer = KafkaConsumer(
    TOPICO,
    bootstrap_servers=SERVIDOR_KAFKA,
    group_id="teste-lote-50-patients-v1",
    auto_offset_reset="earliest",
    enable_auto_commit=False,
    consumer_timeout_ms=60000
)


# 4. Contadores
patients_recebidos = 0
patients_criados = 0
patients_existentes = 0
patients_com_erros = 0
mensagens_ignoradas = 0
mensagens_confirmadas = 0


try:
    print("Consumer iniciado. Aguardando mensagens...")

    # 5. Lê as mensagens do Kafka
    for mensagem in consumer:

        try:
            # Converte a mensagem para JSON
            conteudo = json.loads(
                mensagem.value.decode("utf-8")
            )

            # Verifica se é um recurso Patient
            if not isinstance(conteudo, dict):
                raise ValueError("Mensagem não é um objeto JSON.")

            if conteudo.get("resourceType") != "Patient":
                raise ValueError("Mensagem não é um recurso Patient.")

            patients_recebidos += 1

            print("\n===== PATIENT RECEBIDO =====")
            print(f"Offset: {mensagem.offset}")

            # 6. Obtém o CPF
            cpf = conteudo["identifier"][0]["value"]

            if not isinstance(cpf, str) or not cpf.isdigit():
                raise ValueError("Identificador inválido.")

            # 7. Cadastro condicional no HAPI FHIR
            resposta = requests.post(
                URL_PATIENT,
                json=conteudo,
                headers={
                    "Content-Type": "application/fhir+json",
                    "Accept": "application/fhir+json",
                    "If-None-Exist": f"identifier={cpf}"
                },
                timeout=30
            )

            # 8. Verifica o resultado
            if resposta.status_code == 201:
                patients_criados += 1
                print("Patient cadastrado com sucesso!")

            elif resposta.status_code == 200:
                patients_existentes += 1
                print("Patient já existente.")

            else:
                raise RuntimeError(
                    f"Falha no HAPI FHIR. HTTP {resposta.status_code}: "
                    f"{resposta.text[:500]}"
                )

        except (
            UnicodeDecodeError,
            json.JSONDecodeError,
            KeyError,
            IndexError,
            TypeError,
            ValueError
        ) as erro:

            mensagens_ignoradas += 1
            print(
                f"Offset {mensagem.offset}: "
                f"mensagem inválida - {erro}"
            )

            # Mensagens inválidas são descartadas
            # neste projeto de testes.

        except (requests.RequestException, RuntimeError) as erro:

            patients_com_erros += 1

            print(f"Erro ao cadastrar Patient: {erro}")
            print("Mensagem não confirmada no Kafka.")
            print("Processamento interrompido para permitir nova tentativa.")

            # Interrompe antes de confirmar o offset
            break

        # 9. Confirma o processamento no Kafka
        try:
            consumer.commit()
            mensagens_confirmadas += 1

            print(
                f"Offset {mensagem.offset} "
                "confirmado no Kafka."
            )

        except KafkaError as erro:
            print(f"Erro ao confirmar offset: {erro}")
            break

finally:
    # 10. Fecha a conexão
    consumer.close()

    # 11. Resumo final
    print("\n===== RESUMO DO CONSUMER =====")
    print(f"Patients recebidos: {patients_recebidos}")
    print(f"Patients criados: {patients_criados}")
    print(f"Patients já existentes: {patients_existentes}")
    print(f"Patients com erros: {patients_com_erros}")
    print(f"Mensagens ignoradas: {mensagens_ignoradas}")
    print(f"Mensagens confirmadas: {mensagens_confirmadas}")
