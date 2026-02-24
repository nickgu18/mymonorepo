
import pandas as pd

def check_duplicates(csv_path):
    """
    Reads a CSV file and checks for duplicate repositories.
    """
    df = pd.read_csv(csv_path)
    duplicates = df[df.duplicated('repo', keep=False)]
    if not duplicates.empty:
        print("Duplicate repositories found:")
        print(duplicates)
    else:
        print("No duplicate repositories found.")

if __name__ == '__main__':
    check_duplicates('/usr/local/google/home/guyu/Desktop/gcli/codewiki_qa/curation/experiment_4/selected_repos.csv')
