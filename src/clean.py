import pandas as pd
from sqlalchemy import create_engine
import logging
import os

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

DB_PATH = "data/mercado_automotivo.db"
MODELO_FILTRO = "Onix"

os.makedirs("data", exist_ok=True)
engine = create_engine(f"sqlite:///{DB_PATH}")

def carregar_dados():
    try:                                                       
        return pd.read_sql("SELECT * FROM historico_precos", con=engine)
    except Exception:
        logger.warning("Tabela ainda não existe. Retornando DataFrame vazio.")
        return pd.DataFrame()

def limpar_dados(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    df = df[df['modelo'].str.contains(MODELO_FILTRO, case=False, na=False)].copy()
    df['preco'] = pd.to_numeric(df['preco'], errors='coerce')
    df['ano'] = pd.to_numeric(
        df['ano'].astype(str).str.split('/').str[0],
        errors='coerce'
    )
    df['km'] = df['km'].str.replace(' Km', '', regex=True).str.replace('.', '', regex=False)
    df['km'] = pd.to_numeric(df['km'], errors='coerce')
    df = df.drop_duplicates(subset=['anuncio_id', 'data_coleta'], keep='last')
    df = df[df['preco'] > 0].copy()
    logger.info(f"Limpeza concluída. Registros restantes: {len(df)}")
    return df

def salvar_dados_limpos(df: pd.DataFrame) -> None:
    if df.empty:
        logger.warning("Nenhum dado para salvar após limpeza.")
        return
    df.to_sql("historico_precos_limpo", con=engine, if_exists="replace", index=False)  # CORREÇÃO 1
    logger.info(f"{len(df)} registros limpos salvos.")

def main():
    logger.info("=== INICIANDO LIMPEZA DE DADOS ===")
    df = carregar_dados()
    if df.empty:
        logger.warning("Nenhum dado encontrado.")
        return
    df_limpo = limpar_dados(df)
    salvar_dados_limpos(df_limpo)
    logger.info("=== LIMPEZA CONCLUÍDA ===")

if __name__ == "__main__":
    main()
