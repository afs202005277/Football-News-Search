# Football News Search System - Portuguese League (2023/2024)

## Overview

This repository contains the implementation of a **Football News Search System** for the **Portuguese League (2023/2024)**.
The system is designed to **retrieve and analyze football-related news** using various data sources, including **Arquivo.pt, Wikipedia, and Kaggle datasets**. Additionally, it integrates **semantic search, sentiment analysis, and related content recommendations** to enhance the search experience.

## Data Sources

The project utilizes the following sources for news retrieval:

- **Arquivo.pt** (Web crawling & scraping from `record.pt`, `abola.pt`, and `ojogo.pt`)
- **Wikipedia** (Scraping for football team history)
- **Kaggle Datasets** (CSV files containing football game events)

## System Features

### 1. **Search System & User Interface**
- A user-friendly **frontend** to facilitate intuitive search and exploration.
- The interface allows testing different features and improving search evaluations.

### 2. **Schema Enhancements**
- **Synonym Expansion:** Automatically collected and manually refined synonyms for improved query matching.
- **Semantic Search with Embeddings:** Uses the **Sentence-Transformers** Python package for **vector-based nearest-neighbor search**.
- **Sentiment Analysis:** Analyzes the emotional tone of articles, enabling users to filter news based on positive/negative sentiment.
- **Related Content Recommendations:** Suggests **three similar articles** when viewing a news piece, based on semantic similarity.

## Evaluation and Performance

To assess system improvements, six different **schema configurations** were tested:

| Schema | Description |
|--------|------------|
| **1**  | Baseline (no improvements) |
| **2**  | Basic text embeddings |
| **3**  | Synonym expansion |
| **4**  | Text embeddings + related content |
| **5**  | Text embeddings + sentiment analysis |
| **6**  | **Text embeddings + related content + sentiment analysis (Best Performance)** |

### **Key Findings**
- **Synonym Expansion** did not consistently improve performance.
- **Semantic Search with Embeddings** was effective when combined with other techniques.
- **Related Content Recommendations** significantly enhanced search relevance.
- **Sentiment Analysis** helped filter emotional-tone queries.
- **Combining related content & sentiment analysis provided the best results.**

#### **Mean Average Precision (MAP) Results**
| Schema | MAP (All Queries) | MAP (Excluding Outlier Query) |
|--------|------------------|-----------------------------|
| **1**  | 0.453260        | 0.549170                     |
| **2**  | 0.531000        | 0.444270                     |
| **3**  | 0.454390        | 0.550070                     |
| **4**  | 0.661030        | 0.566050                     |
| **5**  | 0.650390        | 0.539800                     |
| **6**  | **0.745980**    | **0.634010**                 |

