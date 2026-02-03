from ucimlrepo import fetch_ucirepo
import pandas as pd
import os 

# Fetch dataset
dataset = fetch_ucirepo(id=144)

X = dataset.data.features
y = dataset.data.targets

# Merge features + target
data = pd.concat([X, y], axis=1)

# Optional: rename target column for clarity
data = data.rename(columns={y.columns[0]: "target"})


dirpath='/home/asini/Workspace/Enseignments/2025-2026/DevOps_Android_M1/TD/TD3/automl-api/data/processed'
# Save
data.to_csv(os.path.join(dirpath,"german_credit_data.csv"), index=False)

print("Dataset saved as german_credit_data.csv")

