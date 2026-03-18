# MotorMetrics 🚗📊

*Leia isto em [Inglês](README.md).*

## 🎯 Objetivo de Negócio
O mercado automotivo é extremamente dinâmico, e a desvalorização dos veículos é um dos principais fatores na decisão de compra e venda. Este projeto de **Engenharia de Dados e Analytics Engineering** visa monitorar automaticamente a depreciação real de veículos usados.

Através de um pipeline de ETL/ELT, o sistema cruza os preços de anúncios reais com os valores oficiais de referência da Tabela FIPE. O principal KPI monitorado é a **Taxa de Depreciação (Spread FIPE vs. Mercado)**, permitindo identificar oportunidades de negócio, distorções regionais de preço e o comportamento da curva de desvalorização por ano/modelo.

## 🛠️ Stack Tecnológica
* **Linguagem:** Python
* **Extração e Tratamento:** `requests`, `BeautifulSoup`, `pandas`
* **Armazenamento:** AWS S3 (Data Lake) e PostgreSQL (Data Warehouse)
* **Transformação (Analytics Engineering):** dbt (Data Build Tool)
* **Orquestração e CI/CD:** GitHub Actions
* **Visualização de Dados (BI):** Power BI

## 🚀 Início Rápido (Configurar e Rodar)

Para colocar o projeto funcionando na sua máquina, copie e cole os comandos abaixo no seu terminal:

```bash
# 1. Clonar o repositório e entrar na pasta
git clone https://github.com/Soooar/Motor-Metrics.git
cd MotorMetrics

# 2. Criar e ativar o ambiente virtual (Windows)
python -m venv venv
./venv/Scripts/activate

# 3. Instalar todas as dependências
pip install -r requirements.txt

# 4. Rodar o robô de extração inicial
python src/extrator_massa.py

[!TIP]
Se você estiver no Linux ou MacOS, use source venv/bin/activate para ativar o ambiente.
