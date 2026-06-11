import os
import pandas as pd


def read_leads(input_file: str, limit: int | None = None) -> pd.DataFrame:
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input file not found: {input_file}")

    leads_df = pd.read_csv(input_file)

    if limit:
        return leads_df.head(limit)

    return leads_df


def save_output(results: list[dict], output_file: str) -> None:
    output_df = pd.DataFrame(results)
    output_df.to_csv(output_file, index=False)