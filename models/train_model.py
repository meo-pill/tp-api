"""
Script d'entraînement du modèle de credit scoring
Ce script crée un modèle simple pour la démonstration
"""
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib
from pathlib import Path

# Configuration
RANDOM_STATE = 42
MODEL_PATH = Path(__file__).parent / "credit_scoring_model.pkl"


def generate_synthetic_data(n_samples=1000):
    """
    Génère des données synthétiques pour l'entraînement
    
    Dans un vrai projet, on utiliserait des données réelles
    """
    np.random.seed(RANDOM_STATE)
    
    # Générer des features
    age = np.random.randint(18, 70, n_samples)
    income = np.random.normal(2500, 1000, n_samples)
    income = np.clip(income, 800, 8000)  # Limiter les valeurs
    
    credit_amount = np.random.normal(15000, 8000, n_samples)
    credit_amount = np.clip(credit_amount, 1000, 50000)
    
    duration = np.random.randint(6, 84, n_samples)
    
    # Logique simple pour la target
    # Plus l'âge est élevé, le revenu élevé, le crédit faible et la durée courte,
    # plus la probabilité d'approbation est élevée
    risk_score = (
        (age / 70) * 0.3 +
        (income / 8000) * 0.4 +
        (1 - credit_amount / 50000) * 0.2 +
        (1 - duration / 84) * 0.1
    )
    
    # Ajouter du bruit
    noise = np.random.normal(0, 0.1, n_samples)
    risk_score = np.clip(risk_score + noise, 0, 1)
    
    # Target : 1 = APPROVED, 0 = REJECTED
    target = (risk_score > 0.5).astype(int)
    
    # Créer le DataFrame
    df = pd.DataFrame({
        'age': age,
        'income': income,
        'credit_amount': credit_amount,
        'duration': duration,
        'approved': target
    })
    
    return df


def train_model():
    """Entraîne le modèle de credit scoring"""
    print("🔄 Génération des données d'entraînement...")
    df = generate_synthetic_data(n_samples=2000)
    
    print(f"📊 Dataset : {len(df)} échantillons")
    print(f"   - APPROVED : {df['approved'].sum()} ({df['approved'].mean()*100:.1f}%)")
    print(f"   - REJECTED : {(~df['approved'].astype(bool)).sum()} ({(1-df['approved'].mean())*100:.1f}%)")
    
    # Séparer features et target
    X = df[['age', 'income', 'credit_amount', 'duration']]
    y = df['approved']
    
    # Split train/test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y
    )
    
    print(f"\n🔄 Entraînement du modèle...")
    print(f"   - Train : {len(X_train)} échantillons")
    print(f"   - Test  : {len(X_test)} échantillons")
    
    # Entraîner un Random Forest simple
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=RANDOM_STATE,
        n_jobs=-1
    )
    
    model.fit(X_train, y_train)
    
    # Évaluation
    y_pred_train = model.predict(X_train)
    y_pred_test = model.predict(X_test)
    
    train_acc = accuracy_score(y_train, y_pred_train)
    test_acc = accuracy_score(y_test, y_pred_test)
    
    print(f"\n📈 Performances :")
    print(f"   - Accuracy Train : {train_acc:.4f}")
    print(f"   - Accuracy Test  : {test_acc:.4f}")
    
    print(f"\n📋 Rapport de classification (Test) :")
    print(classification_report(
        y_test, 
        y_pred_test,
        target_names=['REJECTED', 'APPROVED']
    ))
    
    # Importance des features
    feature_importance = pd.DataFrame({
        'feature': X.columns,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print(f"\n🔍 Importance des features :")
    print(feature_importance.to_string(index=False))
    
    # Sauvegarder le modèle
    print(f"\n💾 Sauvegarde du modèle dans {MODEL_PATH}...")
    joblib.dump(model, MODEL_PATH)
    
    print(f"\n✅ Modèle entraîné et sauvegardé avec succès !")
    print(f"📁 Chemin : {MODEL_PATH}")
    print(f"📦 Taille : {MODEL_PATH.stat().st_size / 1024:.2f} KB")
    
    return model


if __name__ == "__main__":
    model = train_model()
    
    # Test rapide
    print(f"\n🧪 Test rapide du modèle :")
    test_cases = [
        {"age": 35, "income": 3200, "credit_amount": 15000, "duration": 48},
        {"age": 25, "income": 1500, "credit_amount": 30000, "duration": 72},
        {"age": 50, "income": 5000, "credit_amount": 10000, "duration": 24},
    ]
    
    for i, case in enumerate(test_cases, 1):
        features = np.array([[
            case["age"], 
            case["income"], 
            case["credit_amount"], 
            case["duration"]
        ]])
        prob = model.predict_proba(features)[0, 1]
        decision = "APPROVED" if prob >= 0.5 else "REJECTED"
        
        print(f"\n  Test {i}: {case}")
        print(f"  → Décision: {decision} (prob: {prob:.4f})")
