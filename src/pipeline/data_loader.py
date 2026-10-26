import os
import glob
import pandas as pd
from sklearn.model_selection import GroupShuffleSplit
from src.pipeline.config import SEED

def load_and_profile_csv(sample_dir_pattern="use_cases/pnm_study_case/sample/*.csv"):
    csv_files = sorted(glob.glob(sample_dir_pattern))
    if not csv_files:
        raise FileNotFoundError(f"Tidak ada file CSV yang ditemukan di {sample_dir_pattern}")

    dfs = []
    for file_path in csv_files:
        df = pd.read_csv(file_path, sep=";", quotechar='"', on_bad_lines="skip", low_memory=False)
        df["source_file"] = os.path.basename(file_path)
        df["source_row_number"] = df.index
        dfs.append(df)

    full_df = pd.concat(dfs, ignore_index=True)

    profile_report = {
        "files_loaded": len(csv_files),
        "total_rows": len(full_df),
        "duplicate_rows": int(full_df.duplicated(subset=["original_id"]).sum()),
        "missing_titles": int(full_df["title"].isna().sum()),
        "missing_bodies": int(full_df["body"].isna().sum()),
        "language_distribution": full_df["language"].value_counts(dropna=False).to_dict()
    }
    return full_df, profile_report

def clean_and_split_by_article_id(full_df):
    clean_df = full_df.drop_duplicates(subset=["original_id"]).copy()
    clean_df = clean_df.dropna(subset=["title", "body"]).reset_index(drop=True)
    clean_df["title"] = clean_df["title"].astype(str).str.strip()
    clean_df["body"] = clean_df["body"].astype(str).str.strip()
    clean_df["full_text"] = clean_df["title"] + ". " + clean_df["body"]

    # Split 70% Train, 15% Validation, 15% Held-Out Test berdasarkan original_id
    gss_train = GroupShuffleSplit(n_splits=1, test_size=0.30, random_state=SEED)
    train_idx, temp_idx = next(gss_train.split(clean_df, groups=clean_df["original_id"]))
    train_df = clean_df.iloc[train_idx].reset_index(drop=True)
    temp_df = clean_df.iloc[temp_idx].reset_index(drop=True)

    gss_val = GroupShuffleSplit(n_splits=1, test_size=0.50, random_state=SEED)
    val_idx, test_idx = next(gss_val.split(temp_df, groups=temp_df["original_id"]))
    val_df = temp_df.iloc[val_idx].reset_index(drop=True)
    test_df = temp_df.iloc[test_idx].reset_index(drop=True)

    return train_df, val_df, test_df
