import pandas as pd
from sqlalchemy import create_engine

from settings import DB_URL, TABELA_RAW, TABELA_CLEAN, MODELO_FILTRO, get_logger

logger = get_logger(__name__)


def carregar_dados(engine) -> pd.DataFrame:
    try:
        df = pd.read_sql(f"SELECT * FROM {TABELA_RAW}", con=engine)
        logger.info(f"{len(df)} registros carregados de '{TABELA_RAW}'.")
        return df
    except Exception as e:
        logger.warning(f"Não foi possível ler '{TABELA_RAW}': {e}")
        return pd.DataFrame()


def _limpar_ano(serie: pd.Series) -> pd.Series:
    if pd.api.types.is_numeric_dtype(serie):
        return serie
    return pd.to_numeric(
        serie.astype(str).str.split("/").str[0].str.strip(),
        errors="coerce",
    )


def _limpar_km(serie: pd.Series) -> pd.Series:
    """
    Verifica o dtype antes de operar como string — o extract.py já grava km
    como float, então chamar .str.replace em coluna numérica retornaria NaN.
    """
    if pd.api.types.is_numeric_dtype(serie):
        return serie
    return pd.to_numeric(
        serie.astype(str)
             .str.replace(r"\s*Km", "", regex=True)
             .str.replace(".", "", regex=False)
             .str.strip(),
        errors="coerce",
    )


def limpar_dados(df: pd.DataFrame, modelo_filtro: str = MODELO_FILTRO) -> pd.DataFrame:
    if df.empty:
        return df

    total_inicial = len(df)

    if modelo_filtro:
        df = df[df["modelo"].str.contains(modelo_filtro, case=False, na=False)].copy()
        logger.info(f"Após filtro '{modelo_filtro}': {len(df)}/{total_inicial} registros.")

    df["preco"] = pd.to_numeric(df["preco"], errors="coerce")
    df["ano"]   = _limpar_ano(df["ano"])
    df["km"]    = _limpar_km(df["km"])

    antes = len(df)
    df = df[df["preco"] > 0].dropna(subset=["preco", "ano"]).copy()
    logger.info(f"Removidos {antes - len(df)} registros inválidos.")

    df = (
        df.sort_values("data_coleta", ascending=True)
          .drop_duplicates(subset=["anuncio_id"], keep="last")
          .copy()
    )

    logger.info(f"Limpeza concluída. {len(df)} registros válidos (de {total_inicial}).")
    return df


def salvar_dados_limpos(df: pd.DataFrame, engine) -> None:
    if df.empty:
        logger.warning("Nenhum dado para salvar após limpeza.")
        return

    df.to_sql(name=TABELA_CLEAN, con=engine, if_exists="replace", index=False)
    logger.info(f"{len(df)} registros salvos em '{TABELA_CLEAN}'.")


def main() -> None:
    logger.info("=== INICIANDO LIMPEZA DE DADOS ===")
    engine = create_engine(DB_URL)

    df = carregar_dados(engine)
    if df.empty:
        logger.warning("Nenhum dado encontrado. Execute o extract.py primeiro.")
        return

    df_limpo = limpar_dados(df)
    salvar_dados_limpos(df_limpo, engine)

    logger.info("=== LIMPEZA CONCLUÍDA ===")


if __name__ == "__main__":
    main()
