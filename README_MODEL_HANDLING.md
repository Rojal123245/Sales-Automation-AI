# Handling Large Model Files

This project uses machine learning models that can be quite large, which presents challenges for version control. The following guidelines explain how to work with these large model files.

## Why Model Files Are Not in Git

Model files (specifically `models/saved/sales_forecast.pkl`) exceed GitHub's file size limit of 100MB. Therefore, they are excluded from the repository via `.gitignore`.

## Options for Working with Large Models

### Option 1: Generate the Model Locally (Recommended)

Run the full training pipeline to generate the model locally:

```bash
python main.py --mode train
```

This will create the model file at `models/saved/sales_forecast.pkl`.

### Option 2: Download Pre-trained Models

For convenience, pre-trained models can be downloaded from an external storage service:

```bash
# Example command to download models (customize as needed)
python scripts/download_models.py
```

### Option 3: Use Git LFS (For Team Environments)

If your team needs to version large model files, consider using Git Large File Storage (LFS):

1. Install Git LFS:

   ```bash
   brew install git-lfs  # macOS
   apt-get install git-lfs  # Ubuntu/Debian
   ```

2. Initialize Git LFS in your repository:

   ```bash
   git lfs install
   ```

3. Track model files with LFS:

   ```bash
   git lfs track "models/saved/*.pkl"
   git add .gitattributes
   ```

4. Then add and commit as usual:
   ```bash
   git add models/saved/sales_forecast.pkl
   git commit -m "Add model file via LFS"
   ```

## Working Without Pre-trained Models

The system is designed to work even without pre-trained models:

- If a model file is not found, a simple fallback model is used
- This enables testing the automation pipeline without requiring large model files
- For production use, always generate or download the proper model

## Best Practices

1. Don't commit large binary files directly to Git
2. Use the training pipeline to generate models when needed
3. For sharing models across a team, set up a proper model registry or use Git LFS
4. Document model versions and parameters in code or documentation
