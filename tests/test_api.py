"""
Tests unitaires pour l'API Credit Scoring
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestHealthEndpoint:
    """Tests pour l'endpoint /health"""
    
    def test_health_check_success(self):
        """Test que le health check retourne 200"""
        response = client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "model_loaded" in data
        assert data["model_loaded"] is True
    
    def test_health_check_structure(self):
        """Test la structure de la réponse health"""
        response = client.get("/health")
        data = response.json()
        
        required_fields = ["status", "model_loaded", "model_version", "timestamp"]
        for field in required_fields:
            assert field in data


class TestPredictEndpoint:
    """Tests pour l'endpoint /predict"""
    
    def test_predict_valid_request_approved(self):
        """Test une demande qui devrait être approuvée"""
        payload = {
            "age": 45,
            "income": 5000,
            "credit_amount": 10000,
            "duration": 24
        }
        
        response = client.post("/predict", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert "decision" in data
        assert data["decision"] in ["APPROVED", "REJECTED"]
        assert "probability" in data
        assert 0 <= data["probability"] <= 1
        assert "model_version" in data
    
    def test_predict_valid_request_rejected(self):
        """Test une demande qui devrait être rejetée"""
        payload = {
            "age": 22,
            "income": 1200,
            "credit_amount": 40000,
            "duration": 84
        }
        
        response = client.post("/predict", json=payload)
        assert response.status_code == 200
        
        data = response.json()
        assert data["decision"] in ["APPROVED", "REJECTED"]
    
    def test_predict_missing_field(self):
        """Test une requête avec un champ manquant"""
        payload = {
            "age": 35,
            "income": 3200,
            # credit_amount manquant
            "duration": 48
        }
        
        response = client.post("/predict", json=payload)
        assert response.status_code == 422  # Unprocessable Entity
    
    def test_predict_invalid_age(self):
        """Test avec un âge invalide (< 18)"""
        payload = {
            "age": 15,
            "income": 3200,
            "credit_amount": 15000,
            "duration": 48
        }
        
        response = client.post("/predict", json=payload)
        assert response.status_code == 422
    
    def test_predict_negative_income(self):
        """Test avec un revenu négatif"""
        payload = {
            "age": 35,
            "income": -1000,
            "credit_amount": 15000,
            "duration": 48
        }
        
        response = client.post("/predict", json=payload)
        assert response.status_code == 422
    
    def test_predict_invalid_duration(self):
        """Test avec une durée invalide"""
        payload = {
            "age": 35,
            "income": 3200,
            "credit_amount": 15000,
            "duration": 150,  # > 120 mois
            }
        response = client.post("/predict", json=payload)
        assert response.status_code == 422
        
    def test_predict_empty_body(self):
        """Test avec un corps vide"""
        response = client.post("/predict", json={})
        assert response.status_code == 422
    	
    	


class TestModelInfoEndpoint:
    """Tests pour l'endpoint /model/info"""
    def test_model_info_success(self):
        """Test que model info retourne 200"""
        response = client.get("/model/info")
        assert response.status_code == 200
        data = response.json()
        assert "model_name" in data
        assert "algorithm" in data
        assert "version" in data
        assert "features" in data
        assert "threshold" in data

    def test_model_info_structure(self):
            """Test la structure des informations du modèle"""
            response = client.get("/model/info")
            data = response.json()
            
            assert isinstance(data["features"], list)
            assert len(data["features"]) == 4
            assert "age" in data["features"]
            assert "income" in data["features"]
            assert "credit_amount" in data["features"]
            assert "duration" in data["features"]
    
    
class TestRootEndpoint:
    """Tests pour l'endpoint racine"""
    def test_root_endpoint(self):
        """Test l'endpoint racine"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "documentation" in data

if __name__ == "__main__":
	pytest.main([file, "-v", "--tb=short"])	    
	    
	    
	    
