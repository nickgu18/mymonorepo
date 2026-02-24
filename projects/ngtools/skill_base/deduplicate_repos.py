
import pandas as pd

def deduplicate_repos(csv_path):
    """
    Reads a CSV file of repositories, removes duplicates based on the 'repo' column,
    keeping the entry with the most recent 'creation_time', and overwrites the CSV with the cleaned data.
    """
    df = pd.read_csv(csv_path)
    df['creation_time'] = pd.to_datetime(df['creation_time'], format='mixed', utc=True)
    df_deduplicated = df.sort_values('creation_time', ascending=False).drop_duplicates('repo').sort_index()
    df_deduplicated.to_csv(csv_path, index=False)
    print(f"Deduplicated {len(df)} entries down to {len(df_deduplicated)} and updated {csv_path}")

if __name__ == '__main__':
    deduplicate_repos('agent-prototypes/agent_prototypes/qabench/repos.csv')
