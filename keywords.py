import pandas as pd
from typing import Union, List

def get_keywords(input_data: Union[str, List[str]]) -> List[str]:
    if isinstance(input_data, list):
        return [str(k) for k in input_data if k]

    elif isinstance(input_data, str) and input_data.endswith(".csv"):
        df = pd.read_csv(input_data)
        df.columns = [col.lower() for col in df.columns]
        keyword_cols = [col for col in df.columns if "keyword" in col]
        if not keyword_cols:
            raise ValueError("No keyword column found in the CSV.")
        return df[keyword_cols[0]].dropna().astype(str).tolist()

    else:
        raise TypeError("Input must be a list of keywords or a CSV file path.")
