
import json
from pathlib import Path

import pandas as pd
from kafka import KafkaProducer

from criar_patient import criar_patient


# 1. Configurações do Kafka
SERVIDOR_KAFKA = "localhost:9092"
TOPICO = "pacientes-fhir"


# 2. Localiza o arquivo CSV
CAMINHO_CSV = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "patients.csv"
)


# 3. Lê os pacientes do CSV
df = pd.read_csv(
    CAMINHO_CSV,
    encoding="cp1252",
    dtype={"CPF": str}
)


# 4. Cria o Producer
producer = KafkaProducer(
    bootstrap_servers=SERVIDOR_KAFKA,
    value_serializer=lambda mensagem: json.dumps(
        mensagem,
        ensure_ascii=False
    ).encode("utf-8")
)


# 5. Contadores
patients_enviados = 0
patients_com_erros = 0


try:
    # 6. Percorre todos os pacientes do CSV
    for indice, paciente in df.iterrows():

        try:
            # Converte a linha do CSV em Patient FHIR
            patient_fhir = criar_patient(paciente)

            # Envia o Patient ao Kafka
            resultado = producer.send(
                TOPICO,
                value=patient_fhir
            )

            # Aguarda confirmação do Kafka
            confirmacao = resultado.get(timeout=30)

            patients_enviados += 1

            print(
                f"Paciente {indice + 1}: enviado com sucesso! "
                f"Offset: {confirmacao.offset}"
            )

        except Exception as erro:
            patients_com_erros += 1

            print(
                f"Paciente {indice + 1}: erro no envio: {erro}"
            )

finally:
    # 7. Fecha o Producer
    producer.close()


# 8. Resumo final
print("\n===== RESUMO DO PRODUCER =====")
print(f"Total de pacientes no CSV: {len(df)}")
print(f"Patients enviados: {patients_enviados}")
print(f"Patients com erros: {patients_com_erros}")
