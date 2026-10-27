
from pathlib import Path

import pandas as pd

from buscar_patient_id import buscar_patient_id
from criar_condition import criar_conditions
from cadastrar_conditions import cadastrar_conditions


# Localização do CSV
CAMINHO_CSV = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "patients.csv"
)

# Leitura dos pacientes
df = pd.read_csv(
    CAMINHO_CSV,
    encoding="cp1252",
    dtype={"CPF": str}
)

total_conditions = 0
pacientes_com_conditions = 0
erros = 0

print("===== PROCESSAMENTO DAS CONDITIONS =====")

for indice, paciente in df.iterrows():

    observacao = paciente["Observação"]

    # Ignora pacientes sem observação clínica
    if pd.isna(observacao):
        continue

    # Identifica os diagnósticos reconhecidos
    # antes de consultar o HAPI FHIR
    conditions = criar_conditions(
        observacao,
        paciente_id="temporario"
    )

    if not conditions:
        continue

    try:
        # Busca o ID real do paciente no HAPI FHIR
        cpf = "".join(
            caractere
            for caractere in str(paciente["CPF"])
            if caractere.isdigit()
        )

        paciente_id = buscar_patient_id(cpf)

        # Cria novamente as Conditions com o ID correto
        conditions = criar_conditions(
            observacao,
            paciente_id
        )

        # Cadastra as Conditions no HAPI FHIR
        cadastrar_conditions(conditions)

        pacientes_com_conditions += 1
        total_conditions += len(conditions)

        print(
            f"Paciente {indice + 1}: "
            f"{len(conditions)} Condition(s) processada(s)."
        )

    except Exception as excecao:
        erros += 1
        print(f"Paciente {indice + 1}: erro - {excecao}")


print("\n===== RESUMO FINAL =====")
print(f"Pacientes com Conditions: {pacientes_com_conditions}")
print(f"Conditions processadas: {total_conditions}")
print(f"Pacientes com erros: {erros}")
