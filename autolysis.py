# /// script
# requires-python = ">=3.9"
# dependencies = [
#   "pandas",
#   "seaborn",
#   "matplotlib",
#   "numpy",
#   "scipy",
#   "openai",
#   "scikit-learn",
#   "requests",
#   "ipykernel",
# ]
# ///

import os
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import argparse
import requests
import json
import openai  # Ensure the openai library is installed: pip install openai


def analyze_data(dataframe):
    """
    Analyze the data to generate summary statistics, missing value counts, and a correlation matrix.

    :param dataframe: pandas DataFrame
    :return: tuple(summary statistics, missing values, correlation matrix)
    """
    print("Analyzing the dataset...")
    
    # Summary statistics
    summary_stats = dataframe.describe()

    # Missing values
    missing_values = dataframe.isnull().sum()

    # Correlation matrix
    numeric_data = dataframe.select_dtypes(include=[np.number])
    corr_matrix = numeric_data.corr() if not numeric_data.empty else pd.DataFrame()

    print("Analysis complete.")
    return summary_stats, missing_values, corr_matrix


def detect_outliers(dataframe):
    """
    Detect outliers in the dataset using the Interquartile Range (IQR) method.

    :param dataframe: pandas DataFrame
    :return: Series with outlier counts for each numeric column
    """
    print("Detecting outliers...")

    numeric_data = dataframe.select_dtypes(include=[np.number])
    Q1 = numeric_data.quantile(0.25)
    Q3 = numeric_data.quantile(0.75)
    IQR = Q3 - Q1

    outliers = ((numeric_data < (Q1 - 1.5 * IQR)) | (numeric_data > (Q3 + 1.5 * IQR))).sum()
    
    print("Outlier detection complete.")
    return outliers


def generate_visualizations(corr_matrix, outliers, dataframe, output_dir):
    """
    Generate visualizations for correlation matrix, outliers, and data distribution.

    :param corr_matrix: pandas DataFrame (correlation matrix)
    :param outliers: pandas Series (outlier counts)
    :param dataframe: pandas DataFrame
    :param output_dir: str (output directory for saving plots)
    :return: tuple(paths of generated visualization files)
    """
    print("Generating visualizations...")

    # Heatmap for correlation matrix
    heatmap_file = os.path.join(output_dir, 'correlation_matrix.png')
    plt.figure(figsize=(10, 8))
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt=".2f", linewidths=0.5)
    plt.title('Correlation Matrix')
    plt.savefig(heatmap_file)
    plt.close()

    # Outliers plot
    outliers_file = None
    if not outliers.empty and outliers.sum() > 0:
        outliers_file = os.path.join(output_dir, 'outliers.png')
        plt.figure(figsize=(10, 6))
        outliers.plot(kind='bar', color='red')
        plt.title('Outliers Detection')
        plt.xlabel('Columns')
        plt.ylabel('Number of Outliers')
        plt.savefig(outliers_file)
        plt.close()

    # Distribution plot for the first numeric column
    dist_plot_file = None
    numeric_columns = dataframe.select_dtypes(include=[np.number]).columns
    if len(numeric_columns) > 0:
        dist_plot_file = os.path.join(output_dir, 'distribution.png')
        plt.figure(figsize=(10, 6))
        sns.histplot(dataframe[numeric_columns[0]], kde=True, color='blue', bins=30)
        plt.title(f'Distribution of {numeric_columns[0]}')
        plt.savefig(dist_plot_file)
        plt.close()

    print("Visualizations generated.")
    return heatmap_file, outliers_file, dist_plot_file


def create_readme(summary_stats, missing_values, corr_matrix, outliers, output_dir, outliers_file, dist_plot_file):
    """
    Create a README.md file summarizing the analysis with references to visualizations.

    :param summary_stats: pandas DataFrame
    :param missing_values: pandas Series
    :param corr_matrix: pandas DataFrame
    :param outliers: pandas Series
    :param output_dir: str (output directory)
    :param outliers_file: str (path to the outliers plot file)
    :param dist_plot_file: str (path to the distribution plot file)
    :return: str (path to README.md file)
    """
    print("Creating README file...")

    readme_path = os.path.join(output_dir, 'README.md')
    with open(readme_path, 'w') as readme:
        readme.write("# Automated Data Analysis Report\n\n")

        # Introduction
        readme.write("## Introduction\n")
        readme.write("This report provides insights into the dataset, including summary statistics, outlier detection, and visualizations.\n\n")

        # Summary Statistics
        readme.write("## Summary Statistics\n")
        readme.write(summary_stats.to_markdown(tablefmt='pipe'))
        readme.write("\n\n")

        # Missing Values
        readme.write("## Missing Values\n")
        readme.write(missing_values.to_markdown(tablefmt='pipe'))
        readme.write("\n\n")

        # Outliers
        readme.write("## Outliers\n")
        readme.write(outliers.to_markdown(tablefmt='pipe'))
        readme.write("\n\n")

        # Correlation Matrix Visualization
        readme.write("## Correlation Matrix\n")
        readme.write("![Correlation Matrix](correlation_matrix.png)\n\n")

        # Outliers Visualization
        if outliers_file:
            readme.write("## Outliers Visualization\n")
            readme.write("![Outliers](outliers.png)\n\n")

        # Distribution Plot
        if dist_plot_file:
            readme.write("## Data Distribution\n")
            readme.write("![Distribution](distribution.png)\n\n")

        print(f"README created: {readme_path}")
    return readme_path


def generate_story_with_llm(prompt, context):
    """
    Use an LLM API to generate a story from the analysis results.

    :param prompt: str (story prompt)
    :param context: str (context from data analysis)
    :return: str (generated story)
    """
    print("Generating story using LLM...")
    try:
        token = os.environ.get("AIPROXY_TOKEN")
        api_url = "https://aiproxy.sanand.workers.dev/openai/v1/chat/completions"

        data = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"{prompt}\n\n{context}"}
            ],
            "max_tokens": 1000,
            "temperature": 0.7
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }

        response = requests.post(api_url, headers=headers, data=json.dumps(data))
        response.raise_for_status()

        story = response.json()["choices"][0]["message"]["content"].strip()
        print("Story generated successfully.")
        return story

    except Exception as e:
        print(f"Failed to generate story: {e}")
        return "Story generation failed."


def main(csv_file):
    """
    Main function to execute the complete data analysis pipeline.

    :param csv_file: str (path to the CSV file)
    """
    print("Starting analysis...")

    try:
        dataframe = pd.read_csv(csv_file, encoding='ISO-8859-1')
        print("Dataset loaded successfully.")
    except Exception as e:
        print(f"Error loading dataset: {e}")
        return

    summary_stats, missing_values, corr_matrix = analyze_data(dataframe)
    outliers = detect_outliers(dataframe)

    output_dir = "."
    os.makedirs(output_dir, exist_ok=True)

    heatmap_file, outliers_file, dist_plot_file = generate_visualizations(corr_matrix, outliers, dataframe, output_dir)

    story = generate_story_with_llm("Generate a creative narrative from the dataset analysis.", context=str(summary_stats))

    readme_path = create_readme(summary_stats, missing_values, corr_matrix, outliers, output_dir, outliers_file, dist_plot_file)

    if readme_path:
        with open(readme_path, 'a') as readme:
            readme.write("## Generated Story\n")
            readme.write(story)

        print("Analysis pipeline completed successfully.")


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python script.py <path_to_csv_file>")
        sys.exit(1)
    main(sys.argv[1])
