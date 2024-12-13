# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "httpx",
#   "pandas",
#   "seaborn",
#   "matplotlib",
#   "scikit-learn",
# ]
# ///

import os
import sys
import httpx
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer

# Constants
API_URL = "https://aiproxy.sanand.workers.dev/openai/v1/chat/completions"
API_TOKEN = os.environ.get("AIPROXY_TOKEN")  # Use environment variable for the token

# Function to read CSV files
def read_csv_file(filename):
    try:
        return pd.read_csv(filename, encoding="utf-8")
    except UnicodeDecodeError:
        print("Warning: UTF-8 encoding failed. Trying ISO-8859-1 (Latin-1).")
        return pd.read_csv(filename, encoding="ISO-8859-1")

# Perform data analysis
def analyze_data(df):
    # Separate numeric and non-numeric columns
    numeric_df = df.select_dtypes(include=["number"])
    non_numeric_df = df.select_dtypes(exclude=["number"])

    # Handle missing values for numeric columns
    numeric_imputer = SimpleImputer(strategy='mean')
    df[numeric_df.columns] = numeric_imputer.fit_transform(numeric_df)

    # Handle missing values for non-numeric columns
    non_numeric_imputer = SimpleImputer(strategy='most_frequent')
    df[non_numeric_df.columns] = non_numeric_imputer.fit_transform(non_numeric_df)

    analysis = {
        "summary": df.describe(include="all").to_dict(),
        "missing_values": df.isnull().sum().to_dict(),
        "correlation": numeric_df.corr().to_dict(),
        "outliers": detect_outliers(df),
        "clusters": cluster_analysis(df),
    }
    return analysis

# Detect outliers using Isolation Forest
def detect_outliers(df):
    numeric_df = df.select_dtypes(include=["number"])
    if numeric_df.empty:
        return "No numeric data for outlier detection."
    clf = IsolationForest(contamination=0.05, random_state=42)
    outliers = clf.fit_predict(numeric_df)
    return pd.Series(outliers).value_counts().to_dict()

# Perform clustering analysis
def cluster_analysis(df):
    numeric_df = df.select_dtypes(include=["number"])
    if numeric_df.shape[0] > 1 and numeric_df.shape[1] > 1:
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(numeric_df.dropna())
        kmeans = KMeans(n_clusters=3, random_state=42)
        clusters = kmeans.fit_predict(scaled_data)
        cluster_centroids = pd.DataFrame(kmeans.cluster_centers_, columns=numeric_df.columns)
        cluster_summary = {
            "cluster_counts": pd.Series(clusters).value_counts().to_dict(),
            "centroids": cluster_centroids.to_dict(orient="list")
        }
        return cluster_summary
    return "Insufficient data for clustering."

# Generate a single visualization
def generate_visualization(df, output_dir):
    numeric_df = df.select_dtypes(include=["number"])

    if numeric_df.shape[1] > 1:  # Generate Correlation heatmap if possible
        plt.figure(figsize=(10, 6))
        sns.heatmap(numeric_df.corr(), annot=True, cmap="coolwarm")
        plt.title("Correlation Matrix")
        heatmap_filename = "correlation_matrix.png"
        plt.savefig(os.path.join(output_dir, heatmap_filename))
        return heatmap_filename

    elif not numeric_df.empty:  # Otherwise, generate a distribution plot
        col_to_plot = numeric_df.var().idxmax()
        plt.figure(figsize=(8, 5))
        sns.histplot(numeric_df[col_to_plot].dropna(), kde=True)
        plt.title(f"Distribution of {col_to_plot}")
        dist_filename = f"{col_to_plot}_distribution.png"
        plt.savefig(os.path.join(output_dir, dist_filename))
        return dist_filename

    return None

# Send data to LLM dynamically
def send_to_llm(analysis, chart, prompt_type):
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json",
    }

    prompt_mapping = {
        "summary": f"Summarize the dataset with this analysis: {analysis['summary']} and missing values: {analysis['missing_values']}.",
        "correlation": f"Analyze this correlation data: {analysis['correlation']} and suggest insights.",
        "outliers": f"Explain the implications of these outliers: {analysis['outliers']}.",
        "clusters": f"Describe the clustering analysis: {analysis['clusters']} and its business relevance.",
    }

    messages = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "You are an analytical assistant."},
            {"role": "user", "content": prompt_mapping[prompt_type]}
        ],
    }

    try:
        response = httpx.post(
            API_URL,
            json=messages,
            headers=headers,
            timeout=30.0
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except httpx.ReadTimeout:
        print("Error: The request to the AI Proxy timed out. Try again later.")
        sys.exit(1)

# Narrate story based on analysis
def narrate_story(analysis, chart, output_dir):
    prompts = ["summary", "correlation", "outliers", "clusters"]
    responses = [send_to_llm(analysis, chart, prompt) for prompt in prompts]

    readme_content = f"""
# Analysis Report

## Summary
{responses[0]}

## Correlation Insights
{responses[1]}

## Outliers Explanation
{responses[2]}

## Clustering Insights
{responses[3]}

![Visualization]({chart})
"""

    with open(os.path.join(output_dir, "README.md"), "w") as file:
        file.write(readme_content)

# Main function
def main():
    if len(sys.argv) != 2:
        print("Usage: python autolysis.py <dataset.csv>")
        sys.exit(1)

    dataset_path = sys.argv[1]
    output_dir = os.path.splitext(os.path.basename(dataset_path))[0]

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    try:
        df = read_csv_file(dataset_path)
        analysis = analyze_data(df)
        chart = generate_visualization(df, output_dir)
        narrate_story(analysis, chart, output_dir)
        print(f"Analysis complete. See the '{output_dir}' directory for results.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
