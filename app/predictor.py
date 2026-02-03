"""
Logique de chargement et prédiction du modèle ML
"""

import joblib
import numpy as np
import logging
from pathlib import Path
from typing import Optional, Tuple

from app.config import settings

logger = logging.getLogger(__name__)


class CreditScoringPredictor:
    """Classe pour gérer le modèle de credit scoring"""

    def __init__(self):
        """
        Initialise le prédicteur et charge le modèle
        """
        # Sécurisation du chemin (str → Path)
        self.model_path: Path = Path(settings.MODEL_PATH)
        self.model_config = settings.MODEL_CONFIG
        self.model: Optional[object] = None

        self._load_model()

    def _load_model(self) -> None:
        """Charge le modèle depuis le fichier"""
        try:
            if not self.model_path.exists():
                raise FileNotFoundError(
                    f"❌ Modèle introuvable : {self.model_path}"
                )

            self.model = joblib.load(self.model_path)
            logger.info(f"✅ Modèle ML chargé depuis {self.model_path}")

        except Exception as e:
            logger.exception("❌ Échec du chargement du modèle")
            raise

    def is_loaded(self) -> bool:
        """Indique si le modèle est chargé"""
        return self.model is not None

    def predict(
        self,
        age: int,
        income: float,
        credit_amount: float,
        duration: int
    ) -> Tuple[str, float]:
        """
        Fait une prédiction sur une demande de crédit

        Returns:
            ("APPROVED" | "REJECTED", probabilité)
        """
        if not self.is_loaded():
            raise RuntimeError("❌ Le modèle n'est pas chargé")

        if not hasattr(self.model, "predict_proba"):
            raise RuntimeError(
                "❌ Le modèle ne supporte pas predict_proba()"
            )

        try:
            features = np.array([[age, income, credit_amount, duration]])

            logger.info(
                "🔍 Prédiction | age=%s income=%s credit=%s duration=%s",
                age, income, credit_amount, duration
            )

            probability: float = float(
                self.model.predict_proba(features)[0, 1]
            )

            threshold = self.model_config["threshold"]
            decision = (
                "APPROVED" if probability >= threshold else "REJECTED"
            )

            logger.info(
                "✅ Résultat: %s (probabilité=%.3f)",
                decision, probability
            )

            return decision, probability

        except Exception as e:
            logger.exception("❌ Erreur lors de la prédiction")
            raise

    def get_model_info(self) -> dict:
        """Retourne les métadonnées du modèle"""
        return {
            "name": self.model_config["name"],
            "algorithm": self.model_config["algorithm"],
            "version": self.model_config["version"],
            "features": self.model_config["features"],
            "threshold": self.model_config["threshold"],
        }


# Singleton global utilisé par FastAPI
predictor = CreditScoringPredictor()

