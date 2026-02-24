
import os
import pandas as pd
import numpy as np
from scipy.stats import ks_2samp, chi2_contingency
import matplotlib.pyplot as plt
from tqdm import tqdm

# --- Configuration ---
REFERENCE_CSV = '/usr/local/google/home/guyu/Desktop/gcli/agent-prototypes/agent_prototypes/qabench/repos.csv'
CANDIDATE_CSV = '/usr/local/google/home/guyu/Desktop/gcli/codewiki_qa/curation/qualified_repos.csv'
OUTPUT_DIR = '/usr/local/google/home/guyu/Desktop/gcli/codewiki_qa/curation'
SUBSET_SIZE = 50

# --- Helper Functions ---

def calculate_loc_similarity(dist1, dist2):
    """Calculates the Kolmogorov-Smirnov similarity."""
    if len(dist1) == 0 or len(dist2) == 0:
        return 0, 1.0 # Return a neutral p-value if one is empty
    ks_stat, p_value = ks_2samp(dist1, dist2)
    return ks_stat, p_value

def calculate_lang_similarity(dist1, dist2):
    """Calculates the Chi-Squared similarity."""
    if dist1.empty or dist2.empty:
        return 0, 1.0 # Return a neutral p-value if one is empty

    # Create a contingency table
    freq1 = dist1.value_counts()
    freq2 = dist2.value_counts()
    
    # Find common languages to avoid zero frequencies in the table
    common_languages = freq1.index.intersection(freq2.index)
    
    if len(common_languages) < 2:
        # Chi-squared test is not meaningful with less than 2 common categories
        return 0, 1.0

    contingency_table = pd.DataFrame([freq1[common_languages], freq2[common_languages]], index=['ref', 'sub']).fillna(0)

    # The table should now be safe for the test
    chi2_stat, p_value, _, _ = chi2_contingency(contingency_table)
    return chi2_stat, p_value

def plot_distributions(ref_df, subset_df, output_path):
    """Plots and saves the distributions for LOC and language."""
    # Plot LOC (ECDF)
    plt.figure(figsize=(12, 6))
    
    # ECDF for Lines of Code
    ref_loc = np.sort(ref_df['lines_of_code'])
    ref_y = np.arange(1, len(ref_loc) + 1) / len(ref_loc)
    subset_loc = np.sort(subset_df['lines_of_code'])
    subset_y = np.arange(1, len(subset_loc) + 1) / len(subset_loc)
    
    plt.plot(ref_loc, ref_y, marker='.', linestyle='none', label='Reference Set')
    plt.plot(subset_loc, subset_y, marker='.', linestyle='none', label='Selected Subset')
    plt.xlabel('Lines of Code (Log Scale)')
    plt.ylabel('ECDF')
    plt.xscale('log')
    plt.title('Empirical Cumulative Distribution Function (ECDF) of Lines of Code')
    plt.legend()
    plt.grid(True)
    plt.savefig(os.path.join(output_path, 'loc_distribution.png'))
    plt.close()

    # Plot Language Distribution
    plt.figure(figsize=(14, 7))
    ref_lang_counts = ref_df['primary_language'].value_counts(normalize=True)
    subset_lang_counts = subset_df['primary_language'].value_counts(normalize=True)
    
    lang_dist_df = pd.DataFrame({
        'Reference': ref_lang_counts,
        'Subset': subset_lang_counts
    }).fillna(0)
    
    lang_dist_df.plot(kind='bar')
    plt.title('Primary Language Distribution (Normalized)')
    plt.ylabel('Proportion')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(os.path.join(output_path, 'language_distribution.png'))
    plt.close()


# --- Main Script ---

def main():
    # 1. Load Data
    print("Loading datasets...")
    ref_df = pd.read_csv(REFERENCE_CSV)
    # Handle potential missing values or non-numeric data in 'lines_of_code'
    ref_df['lines_of_code'] = pd.to_numeric(ref_df['lines_of_code'], errors='coerce').fillna(0)
    ref_df = ref_df[ref_df['lines_of_code'] > 0] # Filter out repos with 0 LOC

    candidate_df = pd.read_csv(CANDIDATE_CSV)
    candidate_df.rename(columns={'repo_name': 'repo'}, inplace=True) # Align column names
    candidate_df['lines_of_code'] = pd.to_numeric(candidate_df['lines_of_code'], errors='coerce').fillna(0)
    candidate_df = candidate_df[candidate_df['lines_of_code'] > 0]
    
    # Ensure we have enough candidates
    if len(candidate_df) < SUBSET_SIZE:
        print(f"Error: Not enough candidate repositories ({len(candidate_df)}) to form a subset of {SUBSET_SIZE}.")
        return

    # 2. Greedy Selection
    print("Starting greedy selection...")
    selected_indices = []
    candidate_pool = candidate_df.copy()

    for i in tqdm(range(SUBSET_SIZE), desc="Selecting Repos"):
        best_candidate_index = -1
        best_score = -1

        # Create a temporary DataFrame of the current selection
        current_selection_df = candidate_df.loc[selected_indices]

        for index, candidate_row in candidate_pool.iterrows():
            # Create a potential new selection by adding the candidate
            potential_selection_df = pd.concat([current_selection_df, candidate_row.to_frame().T])
            
            # Calculate similarity scores
            _, loc_p = calculate_loc_similarity(ref_df['lines_of_code'], potential_selection_df['lines_of_code'])
            _, lang_p = calculate_lang_similarity(ref_df['primary_language'], potential_selection_df['primary_language'])
            
            # Combine p-values. We want to maximize both, so we can average them.
            # A higher score is better.
            score = (loc_p + lang_p) / 2.0

            if score > best_score:
                best_score = score
                best_candidate_index = index
        
        # Add the best candidate to our selection and remove it from the pool
        if best_candidate_index != -1:
            selected_indices.append(best_candidate_index)
            candidate_pool.drop(best_candidate_index, inplace=True)
        else:
            print("Warning: Could not find a best candidate in an iteration.")
            break # Stop if no suitable candidate is found

    selected_subset_df = candidate_df.loc[selected_indices]
    print("Greedy selection complete.")

    # 3. Create Output Directory
    experiment_num = 1
    while os.path.exists(os.path.join(OUTPUT_DIR, f'experiment_{experiment_num}')):
        experiment_num += 1
    exp_dir = os.path.join(OUTPUT_DIR, f'experiment_{experiment_num}')
    os.makedirs(exp_dir)
    print(f"Created experiment directory: {exp_dir}")

    # 4. Save Results
    # Save selected repos
    selected_subset_df.to_csv(os.path.join(exp_dir, 'selected_repos.csv'), index=False)

    # Save distribution analysis
    final_ks_stat, final_loc_p = calculate_loc_similarity(ref_df['lines_of_code'], selected_subset_df['lines_of_code'])
    final_chi2_stat, final_lang_p = calculate_lang_similarity(ref_df['primary_language'], selected_subset_df['primary_language'])

    with open(os.path.join(exp_dir, 'distribution_analysis.txt'), 'w') as f:
        f.write("---" + "-" * 20 + "\n")
        f.write("Distribution Similarity Analysis ---" + "\n\n")
        f.write(f"Subset Size: {len(selected_subset_df)}" + "\n")
        f.write("\n--- Lines of Code (Kolmogorov-Smirnov Test) ---" + "\n")
        f.write(f"K-S Statistic: {final_ks_stat:.4f}" + "\n")
        f.write(f"P-value: {final_loc_p:.4f}" + "\n")
        f.write("Interpretation: A high p-value (e.g., > 0.05) suggests that we cannot reject the null hypothesis that the two samples are drawn from the same distribution." + "\n")
        
        f.write("\n--- Primary Language (Chi-Squared Test) ---" + "\n")
        f.write(f"Chi-Squared Statistic: {final_chi2_stat:.4f}" + "\n")
        f.write(f"P-value: {final_lang_p:.4f}" + "\n")
        f.write("Interpretation: A high p-value (e.g., > 0.05) suggests no significant difference between the language distributions." + "\n")

    # 5. Plot and Save Distributions
    print("Generating plots...")
    plot_distributions(ref_df, selected_subset_df, exp_dir)
    
    print("\nExperiment finished successfully!")
    print(f"Results saved in: {exp_dir}")


if __name__ == '__main__':
    main()
