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
import os  # Make sure to import os for environment variable access

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

# Generate visualizations
def generate_visualizations(df, output_dir):
    charts = []
    numeric_df = df.select_dtypes(include=["number"])

    # Correlation heatmap
    if numeric_df.shape[1] > 1:
        plt.figure(figsize=(10, 6))
        sns.heatmap(numeric_df.corr(), annot=True, cmap="coolwarm")
        plt.title("Correlation Matrix")
        plt.savefig(os.path.join(output_dir, "correlation_matrix.png"))
        charts.append("correlation_matrix.png")

    # Distribution plots
    for col in numeric_df.columns:
        plt.figure(figsize=(8, 5))
        sns.histplot(numeric_df[col].dropna(), kde=True)
        plt.title(f"Distribution of {col}")
        filename = f"{col}_distribution.png"
        plt.savefig(os.path.join(output_dir, filename))
        charts.append(filename)

    # Missing values heatmap
    if df.isnull().sum().any():
        plt.figure(figsize=(10, 6))
        sns.heatmap(df.isnull(), cbar=False, cmap="viridis")
        plt.title("Missing Values Heatmap")
        filename = "missing_values_heatmap.png"
        plt.savefig(os.path.join(output_dir, filename))
        charts.append(filename)

    return charts

# Send data to LLM
def send_to_llm(messages):
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json",
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
def narrate_story(analysis, charts, output_dir):
    prompt = f"""
    Create a README.md narrating this analysis:
    Data Summary: {analysis['summary']}
    Missing Values: {analysis['missing_values']}
    Correlation Matrix: {analysis['correlation']}
    Outlier Detection: {analysis['outliers']}
    Clustering Analysis: {analysis['clusters']}
    Attach these charts: {charts}.

    Key prompts to use:
    - Identify anomalies or surprising patterns from the analysis.
    - Suggest potential business decisions or insights based on clustering.
    - Explain why certain correlations are strong or weak.
    - Hypothesize causes for missing values and how to handle them.
    - Provide recommendations for future analysis or data collection.

    Additional Prompts:
    - What are the key trends or patterns in the dataset?
    - Summarize the structure and content of this dataset.
    - Suggest methods to handle missing data in this dataset.
    - Identify potential causes of detected outliers.
    - Describe the characteristics of identified clusters and their potential business implications.
    - Evaluate the overall quality of this dataset.
    - What additional data would improve the insights drawn from this dataset?
    - Draft a summary of findings and their implications for decision-making.
    """
    messages = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "You are a Markdown writer."},
            {"role": "user", "content": prompt}
        ],
    }
    story = send_to_llm(messages)
    with open(os.path.join(output_dir, "README.md"), "w") as file:
        file.write(story)

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
        charts = generate_visualizations(df, output_dir)
        narrate_story(analysis, charts, output_dir)
        print(f"Analysis complete. See the '{output_dir}' directory for results.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
