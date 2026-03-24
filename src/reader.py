import pandas as pd
from sqlalchemy import create_engine

from settings import DB_URL, TABELA_CLEAN, get_logger

logger = get_logger(__name__)

SEP = "=" * 80


def carregar_dados(engine) -> pd.DataFrame:
    try:
        df = pd.read_sql(f"SELECT * FROM {TABELA_CLEAN}", con=engine)
        logger.info(f"{len(df)} registros carregados de '{TABELA_CLEAN}'.")
        return df
    except Exception as e:
        logger.warning(f"Não foi possível ler '{TABELA_CLEAN}': {e}. Execute o clean.py primeiro.")
        return pd.DataFrame()


def exibir_resumo_geral(df: pd.DataFrame) -> None:
    print(f"\n{SEP}")
    print("  RESUMO ANALÍTICO — Mercado Automotivo")
    print(SEP)
    print(f"  Total de anúncios  : {len(df):>10,}")
    print(f"  Preço médio        : R$ {df['preco'].mean():>12,.2f}")
    print(f"  Preço mínimo       : R$ {df['preco'].min():>12,.2f}")
    print(f"  Preço máximo       : R$ {df['preco'].max():>12,.2f}")
    print(f"  Desvio padrão      : R$ {df['preco'].std():>12,.2f}")
    print(f"  Ano médio          : {df['ano'].mean():>14.0f}")
    print(f"  KM médio           : {df['km'].mean():>13,.0f} km")
    print(f"  Última coleta      : {df['data_coleta'].max():>17}")
    print(SEP)


def exibir_top_caros(df: pd.DataFrame, n: int = 10) -> None:
    print(f"\n  Top {n} mais caros:")
    print("-" * 80)
    top = df.nlargest(n, "preco")[["modelo", "preco", "ano", "km", "data_coleta"]]
    print(top.to_string(index=False))


def exibir_distribuicao_por_ano(df: pd.DataFrame) -> None:
    print(f"\n  Distribuição por ano de fabricação (top 10 mais recentes):")
    print("-" * 80)
    resumo = (
        df.groupby("ano")
          .agg(qtd=("preco", "count"), preco_medio=("preco", "mean"), km_medio=("km", "mean"))
          .sort_values("ano", ascending=False)
          .head(10)
    )
    resumo["preco_medio"] = resumo["preco_medio"].map("R$ {:,.2f}".format)
    resumo["km_medio"]    = resumo["km_medio"].map("{:,.0f} km".format)
    resumo.columns        = ["Anúncios", "Preço Médio", "KM Médio"]
    print(resumo.to_string())


def main() -> None:
    logger.info("=== INICIANDO LEITURA ANALÍTICA ===")
    engine = create_engine(DB_URL)

    df = carregar_dados(engine)
    if df.empty:
        return

    exibir_resumo_geral(df)
    exibir_top_caros(df, n=10)
    exibir_distribuicao_por_ano(df)

    logger.info("=== LEITURA CONCLUÍDA ===")


if __name__ == "__main__":
    main()
