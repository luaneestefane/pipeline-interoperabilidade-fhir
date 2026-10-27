
import pandas as pd
import json
from pathlib import Path
from criar_observation import criar_observation_gestacao

# Localiza o CSV na pasta data
caminho_csv = Path(__file__).resolve().parent.parent / "data" / "patients.csv"

# Lê os 50 pacientes
df = pd.read_csv(caminho_csv, encoding="cp1252")

total_observations = 0

for indice, paciente in df.iterrows():
    observacao = paciente["Observação"]

    # ID temporário utilizado somente no teste
    paciente_id = str(indice + 1)

    resultado = criar_observation_gestacao(
        observacao=observacao,
        paciente_id=paciente_id,
        status="unknown"
    )

    if resultado is not None:
        total_observations += 1

        print(f"\nPaciente: {paciente['Nome']}")
        print(json.dumps(resultado, indent=2, ensure_ascii=False))

print("\n===== RESUMO DO TESTE =====")
print(f"Total de pacientes: {len(df)}")
print(f"Observations de gestação geradas: {total_observations}")
