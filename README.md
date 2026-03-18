# Automotive Market Scraper 🚗📊

## 🎯 Objetivo de Negócio
O mercado automotivo é dinâmico e a desvalorização dos veículos é um dos principais fatores de decisão de compra e venda. Este projeto de **Engenharia de Dados e Analytics Engineering** tem como objetivo monitorar a depreciação real de veículos usados de forma automatizada. 

Através de um pipeline de ETL/ELT, o sistema cruza os preços praticados em anúncios reais na internet com os valores oficiais de referência da Tabela FIPE. O principal KPI monitorado é a **Taxa de Depreciação (Spread FIPE vs. Mercado)**, permitindo identificar oportunidades de negócio, distorções regionais de preço e o comportamento da curva de desvalorização por ano/modelo.

## 🛠️ Stack Tecnológica
* **Linguagem:** Python
* **Extração e Tratamento:** `requests`, `BeautifulSoup`, `pandas`
* **Armazenamento:** AWS S3 (Data Lake) e PostgreSQL (Data Warehouse)
* **Transformação (Analytics Engineering):** dbt (Data Build Tool)
* **Orquestração e CI/CD:** GitHub Actions
* **Visualização de Dados (BI):** Power BI

## 🏗️ Arquitetura do Projeto

> [!NOTE]  
> *(Placeholder)* O diagrama de arquitetura do pipeline (Miro/Draw.io) será inserido aqui ilustrando o fluxo: `Internet -> AWS S3 -> PostgreSQL -> dbt -> Power BI`.

## 🚀 Como Rodar Localmente

### Pré-requisitos
* Python 3.10+
* PostgreSQL rodando localmente (nativo ou via Docker)
* Conta na AWS (opcional para testes puramente locais, obrigatório para o fluxo do S3)

### Passo a Passo

1. **Clone o repositório:**
```bash
git clone [https://github.com/SEU_USUARIO/automotive_scraper.git](https://github.com/SEU_USUARIO/automotive_scraper.git)
cd automotive_scraper