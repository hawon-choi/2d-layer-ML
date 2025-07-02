# 🧪 Project Overview

This repository contains the codes used for preprocessing data and training machine learning models to classify the number of layers in 2D materials from optical microscope images.
The pipeline extracts color-based features (RGB & YIQ distance) from annotated flake regions and uses them to train classifiers that distinguish between different flake thicknesses.


## 🛠️ Installation

To reproduce the project locally, we recommend you to create the same environment using the following:

### 📦 With `env.yaml` (recommended)
```bash
conda env create -f env.yaml
conda activate 2d-layer-classification
```

## 🔁 Pipeline Overview

1. **`1_pixel.py`**
   - input: data_preprocess/data/json/Graphene.json & data/images/
   - output: data_preprocess/data/json/Graphene_pixel.json) 
   Extracts pixel values near the flake/substrate boundary and converts them to RGB and YIQ color space.

2. **`2_dist.py`**
   - input: data_preprocess/data/json/Graphene_pixel.json
   - output: ../Graphene_dist.json
   Computes pixel-wise color differences (flake ↔ nearest substrate) in both RGB and YIQ channels.

3. **`3_merge.py`**
   - input: data_preprocess/data/json/Graphene_dist.json
   - output: ../Graphene_merge.json 
   Aggregates all color distance data by layer type into a clean JSON dataset for model training.

4. **`ml.ipynb`**
   - input: data_preprocess/data/json/Graphene_merge.json 
   - output: AI/results/xxx.csv & .png
   Trains and evaluates machine learning models (SVM, KNN, Decision Tree) using 5-fold cross-validation and test data. Saves evaluation metrics and confusion matrix plots.

---

## 📂 Directory Structure

├── env.yaml
├── data_preprocess/
│   ├── 1_pixel.py
│   ├── 2_dist.py
│   ├── 3_merge.py
│   └── data/
│       ├── images/                     # Raw optical images
│       └── json/
│           ├── Graphene.json          # Annotated regions
│           ├── Graphene_pixel.json    # Extracted pixel RGB/YIQ values
│           ├── Graphene_dist.json     # RGB & YIQ color distance per flake
│           └── Graphene_merge.json    # Final merged dataset
└── AI/
    ├── ml.ipynb
    └── results/
        ├── RGB_DIST.csv               # Model performance
        ├── RGB_DIST.png               # Confusion matrix
        ├── YIQ_DIST.csv
        └── YIQ_DIST.png

---



