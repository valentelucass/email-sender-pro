from pathlib import Path
import pandas as pd


_ROOT = Path(__file__).resolve().parents[1]
_DEFAULT_XLSX = _ROOT / "data" / "contatos.xlsx"


def ler_contatos(caminho: str | Path = _DEFAULT_XLSX):
    """Lê a planilha de contatos e retorna um DataFrame.

    Se o arquivo não existir, cria um template com colunas mínimas e
    instruções, e levanta um erro amigável para o usuário preencher.
    """
    caminho = Path(caminho)
    if not caminho.exists():
        caminho.parent.mkdir(parents=True, exist_ok=True)
        df_template = pd.DataFrame(
            {
                "Nome": ["Exemplo Nome"],
                "E-mail": ["exemplo@dominio.com"],
                "Empresa": ["(opcional)"],
                "Status": ["Aguardando"],
            }
        )
        df_template.to_excel(caminho, index=False)
        raise FileNotFoundError(
            f"Arquivo de contatos não encontrado. Um template foi criado em '{caminho}'. "
            "Abra o arquivo, preencha os contatos e execute novamente."
        )

    df = pd.read_excel(caminho)

    # Validação de colunas mínimas
    required = {"Nome", "E-mail"}
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(
            "Planilha de contatos inválida. Faltam colunas: " + ", ".join(sorted(missing))
        )

    # Garante coluna Status existente
    if "Status" not in df.columns:
        df["Status"] = "Aguardando"

    return df


def atualizar_status(df, index, status: str, caminho: str | Path = _DEFAULT_XLSX):
    """Atualiza a coluna Status e salva a planilha no disco."""
    df.at[index, "Status"] = status
    df.to_excel(caminho, index=False)
