import pandas as pd
import os


def find_files_with_substring(directory, substring):
    # List to hold files that match the criterion
    matching_files = []
    
    # Walk through the directory
    for root, dirs, files in os.walk(directory):
        # Check each file name for the substring
        for file in files:
            if substring in file:
                # Add the file path to the list if it contains the substring
                matching_files.append(os.path.join(root, file))
    
    return matching_files


def read_csv_preserve_id(file_path):
    """Read CSV and ensure 'id' column is read as string to preserve leading zeros."""
    try:
        return pd.read_csv(file_path, dtype={"id": str})
    except Exception:
        # Fallback: read normally and coerce 'id' to str if present
        df = pd.read_csv(file_path)
        if "id" in df.columns:
            df["id"] = df["id"].astype(str)
        return df


def merge_csvs(output_dir="output/apps", out_fname="output/apps/merged_results.csv"):
    matching_files = find_files_with_substring(output_dir, ".csv")
    matching_files.sort()

    dataframes = []
    for file in matching_files:
        df = read_csv_preserve_id(file)
        dataframes.append(df)

    if not dataframes:
        print(f"No CSV files found in {output_dir}")
        return

    # Require `id` column in all files to compute intersection; otherwise fall back to previous behavior
    all_have_id = all(("id" in df.columns) for df in dataframes)
    if not all_have_id:
        print("Warning: not all CSV files have an 'id' column. Falling back to concatenation + dedupe.")
        merged_dataframe = pd.concat(dataframes, ignore_index=True)
        if "id" in merged_dataframe.columns:
            merged_dataframe["id"] = merged_dataframe["id"].astype(str)
            merged_dataframe = merged_dataframe.drop_duplicates(subset=["id"], keep="first").reset_index(drop=True)
        os.makedirs(os.path.dirname(out_fname), exist_ok=True)
        merged_dataframe.to_csv(out_fname, index=False)
        print(f"Merged {len(matching_files)} files -> {out_fname} ({len(merged_dataframe)} rows)")
        return

    # Compute sets of ids per file and their intersection
    file_id_sets = [set(df["id"].astype(str).unique()) for df in dataframes]
    common_ids = set.intersection(*file_id_sets) if file_id_sets else set()

    print(f"Found {len(matching_files)} CSV files. IDs present in all files: {len(common_ids)}")

    # For each file, print IDs that will be excluded (not present in all files)
    for path, ids in zip(matching_files, file_id_sets):
        excluded = ids - common_ids
        name = os.path.basename(path)
        if excluded:
            ex_list = sorted(excluded)
            # Print summary and a sample (limit long lists)
            print(f"{name}: {len(excluded)} excluded ids (not present in all files)")
            if len(ex_list) <= 100:
                print(", ".join(ex_list))
            else:
                print(", ".join(ex_list[:100]) + f", ... (and {len(ex_list)-100} more)")
        else:
            print(f"{name}: all ids present in the intersection")

    # Keep only rows whose `id` appears in every file
    filtered_dfs = [df[df["id"].astype(str).isin(common_ids)].copy() for df in dataframes]
    merged_dataframe = pd.concat(filtered_dfs, ignore_index=True)
    merged_dataframe["id"] = merged_dataframe["id"].astype(str)
    merged_dataframe = merged_dataframe.drop_duplicates(subset=["id"], keep="first").reset_index(drop=True)

    os.makedirs(os.path.dirname(out_fname), exist_ok=True)
    merged_dataframe.to_csv(out_fname, index=False)
    print(f"Merged {len(matching_files)} files -> {out_fname} ({len(merged_dataframe)} rows)")


if __name__ == "__main__":
    merge_csvs()