# Pipeline de Interoperabilidade em Saúde — HL7 FHIR R4

**Teste Técnico | Engenheiro de Dados — Especialista em HL7 FHIR**

**Indra Group | Secretaria de Estado da Saúde de Goiás**

## 1. Sobre o projeto

Este projeto apresenta uma solução de integração de dados em saúde desenvolvida em Python, utilizando Apache Kafka e um servidor HAPI FHIR R4 executado localmente com Docker.

O objetivo é transformar dados de pacientes disponíveis em um arquivo CSV em recursos padronizados HL7 FHIR, permitindo seu armazenamento e consulta por meio de uma API REST.

A solução contempla os recursos:

- **Patient:** dados de identificação e informações demográficas.
- **Condition:** condições clínicas, como diabetes e hipertensão.
- **Observation:** observações clínicas, incluindo informação de gestação.

O projeto utiliza dados fictícios para fins de desenvolvimento e demonstração.

## 2. Tecnologias utilizadas

| Tecnologia | Finalidade |
|---|---|
| Python | Desenvolvimento dos scripts de integração |
| Pandas | Leitura e tratamento dos dados CSV |
| Apache Kafka | Mensageria e transporte dos recursos Patient |
| HAPI FHIR R4 | Servidor de interoperabilidade HL7 FHIR |
| Docker Compose | Orquestração dos serviços locais |
| PostgreSQL | Persistência de dados do servidor FHIR |
| Requests | Comunicação com a API REST FHIR |
| SNOMED CT | Codificação das condições clínicas |
| LOINC | Identificação padronizada de observações |

## 3. Arquitetura da solução

O projeto utiliza dois fluxos de integração.

### 3.1 Integração de Patient via Kafka

```text
patients.csv
     |
     v
Python + Pandas
     |
     v
Conversão para Patient FHIR R4
     |
     v
Kafka Producer
     |
     v
Apache Kafka
Tópico: pacientes-fhir
     |
     v
Kafka Consumer
     |
     v
API REST HAPI FHIR
     |
     v
PostgreSQL
```

O Producer transforma os registros do CSV em recursos Patient e os publica no Kafka.

O Consumer recebe as mensagens e realiza o cadastro condicional no HAPI FHIR, evitando novos cadastros quando encontra um paciente com o mesmo identificador.

O Consumer também utiliza confirmação manual de offsets para registrar o avanço do processamento.

### 3.2 Integração de Condition e Observation

```text
patients.csv
     |
     v
Python + Pandas
     |
     v
Identificação das informações clínicas
     |
     +---- Condition
     |     Diabetes / Hipertensão
     |
     +---- Observation
           Gestação
     |
     v
Consulta do Patient pelo CPF
     |
     v
Associação ao ID do Patient
     |
     v
API REST HAPI FHIR
     |
     v
PostgreSQL
```

Os recursos Condition e Observation são enviados diretamente à API REST do HAPI FHIR.

**Observação:** nesta implementação, somente os recursos Patient passam pelo Apache Kafka.

## 4. Mapeamento dos dados para FHIR

### 4.1 Patient

| Campo CSV | Elemento FHIR |
|---|---|
| Nome | Patient.name.text |
| CPF | Patient.identifier.value |
| Gênero | Patient.gender |
| Data de Nascimento | Patient.birthDate |
| Telefone | Patient.telecom |
| País de Nascimento | Patient.extension |

O CPF é utilizado como identificador de busca nos testes locais.

O país de nascimento é representado por uma extensão baseada na estrutura brasileira BRPais.

### 4.2 Condition

As informações clínicas são identificadas na coluna `Observação`.

| Informação | Terminologia | Código |
|---|---|---|
| Diabético | SNOMED CT | 73211009 |
| Hipertenso | SNOMED CT | 38341003 |

Cada Condition possui uma referência ao paciente correspondente:

```json
{
  "subject": {
    "reference": "Patient/1001"
  }
}
```

O ID apresentado é ilustrativo.

### 4.3 Observation

A informação de gestação é representada por um recurso Observation.

| Elemento | Terminologia | Código |
|---|---|---|
| Pregnancy status | LOINC | 82810-3 |
| Pregnant | SNOMED CT | 77386006 |

O campo `Observation.status` recebe o valor `unknown` porque o CSV não informa o status de processamento da observação.

Esse valor não representa incerteza sobre a informação de gestação.

## 5. Estrutura do projeto

```text
teste-tecnico-fhir/
|
|-- data/
|   |-- patients.csv
|
|-- docs/
|   |-- mapeamento_fhir.md
|
|-- imgs/
|
|-- src/
|   |-- criar_patient.py
|   |-- criar_condition.py
|   |-- criar_observation.py
|   |-- buscar_patient_id.py
|   |-- cadastrar_conditions.py
|   |-- integrar_conditions.py
|   |-- processar_conditions_csv.py
|   |-- processar_observations_csv.py
|   |-- producer_fhir.py
|   |-- consumer_fhir.py
|   |-- validar_patients_fhir.py
|   |-- testar_patients_csv.py
|   |-- testar_conditions_csv.py
|   |-- testar_observations_csv.py
|   |-- ler_csv.py
|   |-- validar_cpf.py
|
|-- docker-compose.yml
|-- .env.example
|-- .gitignore
|-- README.md
```

## 6. Executando o projeto

### 6.1 Pré-requisitos

- Python 3
- Docker Desktop com Docker Compose
- Bibliotecas Python: pandas, requests e kafka-python

### 6.2 Iniciar os serviços

Na pasta principal do projeto:

```bash
docker compose up -d
```

A API FHIR estará disponível em:

```text
http://localhost:8082/fhir
```

O Apache Kafka estará acessível localmente pela porta `9092`.

### 6.3 Instalar as dependências Python

```bash
python -m pip install pandas requests kafka-python
```

### 6.4 Processar os pacientes

Executar o Producer:

```bash
python src/producer_fhir.py
```

Executar o Consumer:

```bash
python src/consumer_fhir.py
```

O Consumer lê os recursos Patient do Kafka e os envia ao HAPI FHIR.

### 6.5 Processar as condições clínicas

```bash
python src/processar_conditions_csv.py
```

O script identifica as condições clínicas, consulta os IDs dos pacientes e realiza os cadastros no servidor.

### 6.6 Processar as observações clínicas

```bash
python src/processar_observations_csv.py
```

O script identifica as informações de gestação e cadastra as Observations relacionadas aos pacientes.

## 7. Validação FHIR

Os recursos Patient foram submetidos à operação de validação do HAPI FHIR:

```text
POST /Patient/$validate
```

Também foram realizados testes de validação dos recursos Condition:

```text
POST /Condition/$validate
```

As Conditions testadas não apresentaram erros de validação, mas receberam avisos relacionados à recomendação `dom-6`, sobre narrativa textual dos recursos.

A validação estrutural no HAPI FHIR não deve ser confundida com a comprovação de conformidade integral a perfis nacionais específicos.

## 8. Resultados obtidos

Durante os testes de integração, foram registrados os seguintes resultados:

| Indicador | Resultado |
|---|---:|
| Pacientes no CSV | 50 |
| Patients enviados pelo Producer | 50 |
| Erros no envio do lote | 0 |
| Patients existentes no HAPI FHIR | 51 |
| Conditions processadas do CSV | 11 |
| Conditions totais no HAPI FHIR | 13 |
| Observations cadastradas | 4 |
| Erros no processamento das Observations | 0 |

O total de 51 Patients inclui um recurso adicional utilizado em testes anteriores.

O total de 13 Conditions inclui dois diagnósticos fictícios cadastrados durante os testes iniciais.

### Teste do Consumer Kafka

Na execução com confirmação manual de offsets, foram registrados:

- 110 recursos Patient recebidos.
- 108 identificados como já existentes.
- Nenhum novo Patient cadastrado.
- Nenhum erro de cadastro.
- 8 mensagens ignoradas.
- 116 mensagens confirmadas no Kafka.

Os resultados incluem mensagens de testes anteriores e indicam uma inconsistência de dois registros na classificação dos contadores, que deve ser investigada.

## 9. Tratamento de duplicidades

O projeto utiliza duas estratégias básicas:

**Patient:** criação condicional por identificador, utilizando o cabeçalho HTTP `If-None-Exist`.

**Condition e Observation:** consulta prévia por paciente e código clínico antes da criação do recurso.

Essas estratégias foram utilizadas nos testes locais. As consultas prévias não garantem ausência de duplicidades em situações de concorrência.

## 10. Limitações e melhorias futuras

- Os CPFs do conjunto de dados são fictícios e não possuem dígitos verificadores válidos.
- O Consumer utiliza commit manual, mas ainda não implementa uma fila de mensagens rejeitadas (*Dead Letter Queue*).
- Mensagens inválidas são descartadas no fluxo de demonstração.
- O controle de offsets e o tratamento de falhas podem ser aprimorados para ambientes de produção.
- As Conditions e Observations ainda não utilizam Kafka.
- O uso completo do perfil nacional BRIndividuo ainda não foi comprovado.
- Não foram implementados testes automatizados abrangentes.
- O controle de duplicidades dos recursos clínicos não é transacional.

## 11. Considerações finais

O projeto demonstra a construção de um pipeline de interoperabilidade em saúde utilizando padrões HL7 FHIR R4, processamento de dados com Python, mensageria com Apache Kafka e persistência em servidor HAPI FHIR.

A solução permite transformar dados estruturados de um arquivo CSV em recursos FHIR, associar informações clínicas aos pacientes e disponibilizar esses recursos por meio de uma API REST.

O desenvolvimento foi realizado em ambiente local, utilizando ferramentas de código aberto, conforme o escopo do desafio técnico.