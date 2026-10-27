
from pathlib import Path
import pandas as pd

from criar_condition import criar_conditions

# Localiza o CSV
caminho_csv = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "patients.csv"
)

# Lê os dados
df = pd.read_csv(caminho_csv, encoding="cp1252")

total_conditions = 0
pacientes_com_conditions = 0

# Percorre os 50 pacientes
for indice, paciente in df.iterrows():

    # ID temporário, somente para teste
    paciente_id = str(indice + 1)

    conditions = criar_conditions(
        paciente["Observação"],
        paciente_id
    )

    if conditions:
        pacientes_com_conditions += 1

    total_conditions += len(conditions)

    for condition in conditions:
        codigo = condition["code"]["coding"][0]

        print(
            f"Paciente {paciente_id} | "
            f"{codigo['display']} | "
            f"SNOMED: {codigo['code']}"
        )

print("\n--- RESUMO ---")
print("Total de pacientes:", len(df))
print("Pacientes com diabetes ou hipertensão:", pacientes_com_conditions)
print("Recursos Condition criados:", total_conditions)
