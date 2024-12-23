import pandas as pd
import numpy as np
import json

# Load and preprocess raw webscraped data
def preprocess_webscraped_data(file_path):
    df = pd.read_csv(file_path)
    columns = list(df.columns)
    shifted_columns = ["Team"] + columns[:-1]
    df.columns = shifted_columns
    df = df.iloc[:, :-1]
    df["Team"] = df["Team"].astype("string")
    df["Team"] = df["Team"].str.replace(r"\s*\(.*?\)", "", regex=True)
    df = df.dropna(subset=["Result"])

    columns_to_convert = df.columns.difference(['Team', 'Date', 'Opponent', 'Result'])
    df = df[df["Date"].str.match(r"^\d{2}/\d{2}/\d{4}$")]
    df["Points Scored"] = df["Result"].str.extract(r"(\d+)").astype(int)
    df["Date"] = pd.to_datetime(df["Date"], errors='coerce')

    for col in columns_to_convert:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

    return df

# Load and preprocess raw API data
def preprocess_api_data(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)

    if isinstance(data, list):
        df = pd.DataFrame(data)
    else:
        df = pd.DataFrame([data])
    expanded_df = pd.json_normalize(df.loc[0, 'data'])
    cleaned_df = pd.concat([df.drop(columns=['data']), expanded_df], axis=1)
    cleaned_df = cleaned_df.dropna(subset=['TEAM']).drop(columns=['pages'], errors='ignore')
    cleaned_df.reset_index(drop=True, inplace=True)
    cleaned_df = cleaned_df.drop(columns=['sport', 'title', 'updated', 'page'])
    # Manually fixing errors before merge
    cleaned_df['TEAM'] = cleaned_df['TEAM'].replace({
        'Auburn (12)': 'Auburn',
        'Iowa State': 'Iowa St.',
        'Tennessee (50)': 'Tennessee'
    })
    # Fixing capitalization
    cleaned_df = cleaned_df.rename(columns={'TEAM': 'Team', 'RANKING': 'Ranking', 'RECORD': 'Record', 'POINTS': 'Points'})

    return cleaned_df

# Merge data
def merge_data(df, api_data):
    df = pd.merge(df, api_data[['Team', 'Ranking', 'Record', 'Points']], on='Team', how='left')
    df['Ranking'] = pd.to_numeric(df['Ranking'], errors='coerce')
    return df

# Double checking (input filepaths as needed)
if __name__ == "__main__":
    # Use the absolute path you provided
    webscraped_file = "/Users/seaniredell/Desktop/Untitled/data/raw_webscraped.csv"
    api_file = "/Users/seaniredell/Desktop/Untitled/data/raw_api.json"

    webscraped_data = preprocess_webscraped_data(webscraped_file)

    mte_teams = ["Auburn", "Tennessee", "Iowa St.", "Gonzaga", "Oklahoma"]
    MTE, Non_MTE = split_mte_data(webscraped_data, mte_teams)

    api_data = preprocess_api_data(api_file)
    final_data = merge_data(webscraped_data, api_data)

    print("Final DataFrame:")
    print(final_data)


