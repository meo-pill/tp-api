
# 🎯 Credit Scoring API - FastAPI avec JWT & ML

Une API REST complète pour l'évaluation de crédit avec intelligence artificielle, authentification JWT et base de données PostgreSQL.

## 🚀 Démarrage rapide

### Option 1 : Script automatique (recommandé)
```bash
# Lancement complet avec tests interactifs
./test_api.sh
```

Le script vous guide à travers :
- Configuration des utilisateurs à créer
- Tests de toutes les fonctionnalités
- Validation des cas d'erreur
- Démonstration complète de l'API

### Option 2 : Manuel avec Docker Compose
```bash
# 1. Démarrer les services
docker-compose up -d

# 2. Initialiser la base de données
docker-compose exec api python init_bd.py

# 3. Tester l'API
curl http://localhost:8000/docs
```

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Client Web    │    │   FastAPI        │    │  PostgreSQL     │
│   (Postman,     │◄──►│   + JWT Auth     │◄──►│   Database      │
│   Frontend...)  │    │   + ML Model     │    │   (Docker)      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

**Technologies utilisées :**
- **FastAPI 0.104.1** - Framework web moderne et performant
- **PostgreSQL 15** - Base de données relationnelle
- **JWT (JSON Web Tokens)** - Authentification stateless
- **Pydantic 2.5** - Validation et sérialisation des données
- **Docker & Docker Compose** - Containerisation
- **Modèle ML FLAML** - Prédictions de credit scoring

## 📚 Endpoints disponibles

### 🔐 Authentification
- `POST /auth/register` - Inscription utilisateur
- `POST /auth/login` - Connexion (retourne JWT token)
- `GET /auth/me` - Profil utilisateur actuel

### 🤖 Prédictions ML
- `POST /predictions/predict` - Prédiction de crédit (protégé)
- `GET /predictions/history` - Historique des prédictions (protégé)
- `GET /predictions/stats` - Statistiques utilisateur (protégé)

### 👨‍💼 Administration (admin uniquement)
- `GET /admin/users` - Liste de tous les utilisateurs
- `GET /admin/stats` - Statistiques globales

### 📖 Documentation
- `GET /docs` - Interface Swagger UI interactive
- `GET /redoc` - Documentation ReDoc alternative

## 🧪 Tests et exemples

### Test complet avec le script
```bash
# Le script interactif teste automatiquement :
./test_api.sh

# ✅ Configuration des utilisateurs
# ✅ Démarrage Docker
# ✅ Initialisation BDD
# ✅ Tests d'inscription (+ gestion d'erreurs)
# ✅ Tests de connexion
# ✅ Tests de sécurité (accès sans token)
# ✅ Tests de prédictions ML
# ✅ Tests d'historique et statistiques
# ✅ Tests des fonctionnalités admin
```

### Tests manuels avec curl

#### 1. Inscription d'un nouvel utilisateur
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "username": "john",
    "password": "SecurePass123",
    "full_name": "John Doe"
  }'
```

#### 2. Connexion et récupération du token
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=john&password=SecurePass123"

# Réponse : {"access_token":"eyJ...", "token_type":"bearer"}
```

#### 3. Utilisation du token pour une prédiction
```bash
TOKEN="your-jwt-token-here"

curl -X POST http://localhost:8000/predictions/predict \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "age": 35,
    "income": 3200,
    "credit_amount": 15000,
    "duration": 48
  }'

# Réponse : {"decision":"APPROVED","probability":0.75,"model_ver":"1.0","prediction_id":1}
```

#### 4. Consultation de l'historique
```bash
curl -X GET http://localhost:8000/predictions/history \
  -H "Authorization: Bearer $TOKEN"
```

## 🔧 Configuration avancée

### Variables d'environnement
```bash
# Dans .env ou docker-compose.yml
DATABASE_URL=postgresql://credit_user:credit_password@db:5432/credit_scoring_db
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Paramètres de l'API
- **Port** : 8000 (configurable)
- **Base de données** : PostgreSQL sur le port 5432
- **Expiration des tokens JWT** : 30 minutes
- **Algorithme JWT** : HS256

## 🐳 Docker

### Structure des conteneurs
- **api** : Application FastAPI (Python 3.11-slim)
- **db** : PostgreSQL 15-alpine avec données persistantes

### Commandes Docker utiles
```bash
# Voir les logs
docker-compose logs -f api

# Accéder au conteneur API
docker-compose exec api bash

# Redémarrer les services
docker-compose restart

# Reconstruction complète
docker-compose down
docker-compose up -d --build
```

## 🎓 Guide pédagogique (pour formateurs)

### Phase 1 : Comprendre l'architecture (20 min)

**Architecture expliquée :**
```
Client → Inscription → JWT Token → API (vérifie token) → Prédiction ML → BDD → Réponse
```

**Démonstration live avec le script :**
1. Lancer `./test_api.sh` 
2. Choisir les utilisateurs à créer
3. Observer chaque étape avec les pauses
4. Expliquer les concepts au fur et à mesure

### Phase 2 : Modèle de données (30 min)
```python
# Structure de la base de données expliquée
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)  # Identifiant unique
    email = Column(String, unique=True)     # Un seul email par utilisateur
    username = Column(String, unique=True)  # Nom d'utilisateur unique
    hashed_password = Column(String)        # Mot de passe chiffré (sécurité)
    is_admin = Column(Boolean, default=False)  # Droits administrateur

class Prediction(Base):
    __tablename__ = "predictions"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))  # Lien vers l'utilisateur
    # ... autres champs de prédiction
```

**🛑 CHECKPOINT : "Observer les tables dans PostgreSQL"**

### Phase 3 : Authentification JWT (45 min)

**Concepts clés à expliquer :**
- **Qu'est-ce qu'un JWT ?** Token auto-contenu avec expiration
- **Pourquoi hasher les mots de passe ?** Sécurité (bcrypt)  
- **Comment vérifier un token ?** Middleware de FastAPI

**Démonstration pratique :**
```python
# Montrer l'évolution du token JWT
# 1. Connexion → Token généré
# 2. Requête avec token → Token vérifié
# 3. Token expiré → Erreur 401
```

### Phase 4 : Endpoints protégés (60 min)

**La magie des dépendances FastAPI :**
```python
@app.post("/predictions/predict")
async def predict(
    request: CreditRequest,
    current_user: User = Depends(get_current_active_user)  # ✨ Magie !
):
    # Si pas de token valide → FastAPI renvoie 401 automatiquement
    # Sinon → current_user contient l'utilisateur connecté
```

**🛑 CHECKPOINT : "Tester /predictions/predict sans token → 401"**

### Phase 5 : Intégration ML et Data Collection (40 min)

**Enregistrer chaque prédiction :**
```python
# Dans /predictions/predict, après la prédiction ML
db_prediction = create_prediction(
    db, current_user.id, age, income, decision, probability
)
# "Maintenant on peut analyser toutes les requêtes !"
```

**Analytics utilisateur :**
```python
@app.get("/predictions/stats")
async def get_stats(current_user: User = Depends(...)):
    # Calculer les statistiques personnalisées de l'utilisateur
    return {
        "total_predictions": count,
        "approved": approved_count,
        "approval_rate": rate
    }
```

### Phase 6 : Tests avec Postman/Swagger (30 min)

**Collection Postman fournie :**
1. Register User
2. Login (sauver le token automatiquement)
3. Get Current User Profile
4. Predict Credit Score
5. Get Prediction History
6. Get User Statistics
7. Admin: Get All Users
8. Admin: Get Global Statistics

**Configuration automatique du token :**
```javascript
// Dans "Tests" du endpoint login
pm.environment.set("auth_token", pm.response.json().access_token);

// Dans les autres requêtes, Header automatique :
// Authorization: Bearer {{auth_token}}
```

## 📋 Fonctionnalités implémentées

### ✅ Authentification complète
- Inscription avec validation email/username unique
- Connexion avec JWT tokens
- Protection automatique des endpoints
- Gestion des erreurs d'authentification

### ✅ Modèle ML intégré
- Prédictions de credit scoring avec FLAML
- Stockage de chaque prédiction en BDD
- Historique complet par utilisateur
- Statistiques personnalisées et globales

### ✅ Interface admin
- Liste de tous les utilisateurs
- Statistiques globales de l'application
- Protection par rôle administrateur

### ✅ Tests automatisés
- Script interactif pour validation complète
- Tests des cas d'erreur (email/pseudo déjà utilisé)
- Validation de tous les endpoints
- Documentation des cas d'usage

### ✅ Production-ready
- Containerisation Docker
- Base de données PostgreSQL
- Variables d'environnement
- Logs structurés
- Documentation Swagger/ReDoc

## 🚀 Exercices d'extension suggérés

### Niveau débutant
1. **Endpoint de changement de mot de passe**
   ```python
   @app.put("/auth/change-password")
   async def change_password(old_password: str, new_password: str, ...)
   ```

2. **Validation plus stricte des données**
   - Age entre 18 et 80 ans
   - Revenus minimum 1000€
   - Durée de crédit entre 6 et 120 mois

3. **Endpoint de déconnexion**
   - Blacklist des tokens JWT
   - Nettoyage des sessions actives

### Niveau intermédiaire
4. **Rate limiting par utilisateur**
   ```python
   # Maximum 10 prédictions par heure par utilisateur
   from slowapi import Limiter
   @limiter.limit("10/hour")
   ```

5. **Export des données en CSV**
   ```python
   @app.get("/predictions/export.csv")
   async def export_predictions(current_user: User = Depends(...)):
       # Retourner un fichier CSV avec l'historique
   ```

6. **Notifications par email**
   - Email de bienvenue après inscription
   - Notification si prédiction rejetée

### Niveau avancé
7. **Dashboard administrateur web**
   - Interface HTML avec graphiques
   - Statistiques en temps réel
   - Gestion des utilisateurs

8. **API de monitoring**
   ```python
   @app.get("/health")
   async def health_check():
       return {"status": "healthy", "database": "connected"}
   ```

9. **Tests unitaires complets**
   ```python
   # tests/test_auth.py, tests/test_predictions.py
   pytest app/tests/
   ```

10. **Déploiement en production**
    - Configuration HTTPS
    - Variables d'environnement sécurisées
    - Logs centralisés
    - Monitoring avec Prometheus

## 📁 Structure du projet

```
design-rest-api/
├── 📁 app/                    # Code source principal
│   ├── __init__.py
│   ├── main.py               # Point d'entrée FastAPI
│   ├── config.py             # Configuration
│   ├── database.py           # Modèles SQLAlchemy
│   ├── models.py             # Modèles Pydantic
│   ├── schemas.py            # Schémas de validation
│   ├── auth.py               # Authentification JWT
│   ├── crud.py               # Opérations base de données
│   ├── dependencies.py       # Dépendances FastAPI
│   ├── security.py           # Utilitaires de sécurité
│   ├── predictor.py          # Logique de prédiction ML
│   └── 📁 routers/           # Endpoints organisés
│       ├── auth.py           # Routes d'authentification
│       ├── predictions.py    # Routes de prédiction
│       ├── admin.py          # Routes administrateur
│       └── model.py          # Routes du modèle ML
├── 📁 models/                # Modèles ML et training
├── 📁 data/                  # Données d'entraînement
├── 📁 tests/                 # Tests automatisés
├── 📁 postman/               # Collection Postman
├── 📁 docs/                  # Documentation générée
├── docker-compose.yml        # Configuration Docker
├── Dockerfile               # Image de l'application
├── requirements.txt         # Dépendances Python
├── test_api.sh             # Script de test interactif ⭐
├── init_bd.py              # Initialisation base de données
├── RESUME_MODIFICATIONS.txt # Journal des modifications
└── README.md               # Ce fichier
```

## 🤝 Contribution

1. Fork le projet
2. Créer une branche (`git checkout -b feature/AmazingFeature`)
3. Commiter les changements (`git commit -m 'Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 🆘 Support

- **Documentation** : `/docs` (Swagger UI) ou `/redoc`
- **Tests** : Utiliser le script `./test_api.sh`
- **Logs** : `docker-compose logs -f api`
- **Issues** : Créer un issue sur GitHub

---

**💡 Astuce** : Commencez toujours par lancer `./test_api.sh` pour une démonstration complète du projet !


