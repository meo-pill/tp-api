import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score
import autosklearn.classification

import os



data_fpath_dir='/home/asini/Workspace/Enseignments/2025-2026/DevOps_Android_M1/TD/TD3/automl-api/data/processed'


data_fpath=os.path.join(data_fpath_dir,'german_credit_data.csv')
# 1. Charger les données (exemple CSV)
data = pd.read_csv(data_fpath)

# 2. Séparer features / cible
X = data.drop(columns=["target"])
y = data["target"]

# 3. Encodage simple (si nécessaire)
for col in X.select_dtypes(include="object").columns:
    X[col] = LabelEncoder().fit_transform(X[col])

# 4. Split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# 5. AutoML
automl = autosklearn.classification.AutoSklearnClassifier(
    time_left_for_this_task=300,   # 5 minutes suffisent
    per_run_time_limit=60,
    n_jobs=1,
    seed=42
)

automl.fit(X_train, y_train)

# 6. Évaluation rapide
y_pred = automl.predict(X_test)
print("Accuracy:", accuracy_score(y_test, y_pred))

# 7. Sauvegarde du modèle
joblib.dump(automl, "credit_scoring_model.pkl")

print("Modèle sauvegardé : credit_scoring_model.pkl")

