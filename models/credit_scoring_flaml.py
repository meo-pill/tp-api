from flaml import AutoML
import pandas as pd
from sklearn.model_selection import train_test_split
import joblib




data_fpath_dir='/home/asini/Workspace/Enseignments/2025-2026/DevOps_Android_M1/TD/TD3/automl-api/data/processed'


data_fpath=os.path.join(data_fpath_dir,'german_credit_data.csv')



data = pd.read_csv(data_fpath)

X = data.drop(columns=["target"])
y = data["target"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

automl = AutoML()
automl.fit(
    X_train=X_train,
    y_train=y_train,
    task="classification",
    time_budget=60,   # ⏱ 1 minute
    metric="accuracy",
    seed=42
)

joblib.dump(automl, "credit_scoring_model.pkl")
print("Model saved: credit_scoring_model.pkl")

