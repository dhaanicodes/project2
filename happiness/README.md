# README.md

## Overview

This analysis presents a comprehensive examination of a dataset spanning various indicators of well-being across different countries and years. Key variables investigated include the Life Ladder, Log GDP per capita, Social support, Healthy life expectancy at birth, Freedom to make life choices, Generosity, Perceptions of corruption, Positive affect, and Negative affect.

## Data Summary

The dataset consists of 2363 observations categorized by country and year. Below is a summary of the main features:

- **Country name**
  - Count: 2363
  - Unique: 165
  - Most frequent country: Lebanon (18 occurrences)
  
- **Year**
  - Mean: 2014.76
  - Range: 2005 - 2023

- **Life Ladder**
  - Mean: 5.48
  - Range: 1.281 - 8.019

- **Log GDP per capita**
  - Mean: 9.40
  - Range: 5.527 - 11.676

- **Social support**
  - Mean: 0.81
  - Range: 0.228 - 0.987

- **Healthy life expectancy at birth**
  - Mean: 63.40 years
  - Range: 6.72 - 74.6 years

- **Freedom to make life choices**
  - Mean: 0.75
  - Range: 0.228 - 0.985

- **Generosity**
  - Mean: ~0.0001
  - Range: -0.34 to 0.7

- **Perceptions of corruption**
  - Mean: 0.74
  - Range: 0.035 - 0.983

- **Positive affect**
  - Mean: 0.65
  - Range: 0.179 - 0.884

- **Negative affect**
  - Mean: 0.27
  - Range: 0.083 - 0.705

### Missing Values
No missing values were detected in any of the variables.

### Correlation Analysis
Strong correlations were found:
- **Life Ladder** and **Log GDP per capita** (0.78)
- **Life Ladder** and **Social support** (0.72)
- **Healthy life expectancy at birth** with **Life Ladder** (0.71)

Weaker correlations include:
- The correlation between **Freedom to make life choices** and **Generosity** (0.32)
- The correlation between **Negative affect** and **Positive affect** (-0.33)

## Outlier Detection
The analysis identified 2244 observations as positive outliers and 119 as negative outliers. The characteristics and potential causes of these anomalies should be explored further to understand their implications.

## Clustering Analysis
The dataset was segmented into three clusters:
- **Cluster 1**: 1113 members
- **Cluster 2**: 835 members
- **Cluster 0**: 415 members

Centroids for these clusters suggest varying levels of wellbeing indicators. For example, Cluster 1 tends to exhibit higher Life Ladder scores and GDP per capita, which suggests it might represent countries with more developed economies and a higher standard of living.

## Key Trends and Patterns
- High GDP correlates with greater life satisfaction as indicated by the Life Ladder score.
- Countries with robust social support systems tend to exhibit higher scores in the Life Ladder metric.
- There are notable disparities in Healthy life expectancy across the clusters, indicating varying health systems' efficiencies in different regions.

## Recommendations
1. **Further Data Collection**: More demographic data (age, education level) could provide deeper insights into the factors influencing life satisfaction.
2. **Handling Outliers**: Investigate the outlier data points to determine if additional contextual information is available or if these points point to data entry errors.
3. **Future Analysis**: Perform trend analysis to observe how these indicators have changed over time. It would help organizations prioritize where to allocate resources or focus their development efforts.
4. **Explore Missing Data Hypothetically**: Future iterations may need to account for variables like cultural differences, which can affect perceptions but may be challenging to quantify or standardize.

## Conclusion
The dataset provides a robust framework for understanding the multifaceted components of well-being across countries. The correlations, coupled with the clustering analysis, suggest clear pathways for organizations wanting to improve life satisfaction and economic conditions in various parts of the world.

## Attachments
Charts demonstrating various distributions and correlation matrices have been saved as images:
- correlation_matrix.png
- year_distribution.png
- Life_Ladder_distribution.png
- Log_GDP_per_capita_distribution.png
- Social_support_distribution.png
- Healthy_life_expectancy_distribution.png
- Freedom_to_make_life_choices_distribution.png
- Generosity_distribution.png
- Perceptions_of_corruption_distribution.png
- Positive_affect_distribution.png
- Negative_affect_distribution.png

This README serves as an initial guide to understanding the insights obtainable from the dataset and facilitates informed decision-making based on its analysis.