# Free Deployment to Streamlit Community Cloud

## 1) Prepare GitHub Repository

- Create a new repository on GitHub.
- Upload the following files:
  - `app.py`
  - `rules.py`
  - `inference.py`
  - `requirements.txt`
  - `.gitignore`
  - `sample_test_data.csv` (optional, for demo)

## 2) Push Project from Local

Run in the project folder:

```powershell
git init
git add .
git commit -m "Initial CDSS rule-based app"
git branch -M main
git remote add origin https://github.com/USERNAME/REPO-NAME.git
git push -u origin main
```

If repository already exists, just:

```powershell
git add .
git commit -m "Prepare deployment"
git push
```

## 3) Deploy on Streamlit Community Cloud

- Open https://share.streamlit.io/
- Login with GitHub account.
- Click **Create app**.
- Select repository, branch `main`, and main file `app.py`.
- Click **Deploy**.

## 4) Verify Application

After build completes, open the app URL and check:

- **Individual Analysis** tab runs.
- **Batch CSV Analysis** tab can upload CSV file.
- Results display risk, traceability, and rule summary.

## 5) Update Application After Deployment

For every code change:

```powershell
git add .
git commit -m "Update CDSS logic/UI"
git push
```

Streamlit Cloud will automatically rebuild.

## Important Notes for TA

- This system is **rule-based** and **does not use machine learning**.
- Dataset is used as simulation data for inference, not for training models.
- For online demo, use CSV files that are not too large for fast response.
