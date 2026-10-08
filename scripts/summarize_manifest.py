#!/usr/bin/env python3
import argparse, pandas as pd
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--manifest", default="data/dermlatbench_metadata.csv"); args = ap.parse_args(); df = pd.read_csv(args.manifest, low_memory=False); print("Rows:", len(df)); print("\nBy source:"); print(df["source_dataset_clean"].value_counts().to_string()); print("\nBy final label:"); print(df["final_patient_laterality"].value_counts().to_string())
if __name__ == "__main__": main()
