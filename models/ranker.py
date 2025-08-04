"""
Ranking model for CTR/CVR prediction and promotion scoring.
"""

import os
import numpy as np
from typing import Dict, List, Any, Optional
from loguru import logger

try:
    import lightgbm as lgb
    LIGHTGBM_AVAILABLE = True
except ImportError:
    LIGHTGBM_AVAILABLE = False
    logger.warning("LightGBM not available, using mock ranking model")


class PromotionRanker:
    """Handles ranking of promotion candidates based on CTR/CVR prediction."""
    
    def __init__(self, model_type: Optional[str] = None):
        self.model_type = model_type or os.getenv("RANKING_MODEL_TYPE", "mock")
        self.model = None
        self.feature_names = [
            'base_ctr', 'interest_match_score', 'budget_compatibility',
            'category_diversity', 'price_tier_numeric', 'user_type_numeric'
        ]
        
        if self.model_type == "lightgbm" and LIGHTGBM_AVAILABLE:
            self._load_lightgbm_model()
        else:
            logger.info("Using mock ranking model")
    
    def _load_lightgbm_model(self):
        """Load or create a LightGBM model."""
        model_path = "models/lightgbm_ranker.txt"
        
        if os.path.exists(model_path):
            try:
                self.model = lgb.Booster(model_file=model_path)
                logger.info("Loaded existing LightGBM model")
                return
            except Exception as e:
                logger.error(f"Failed to load LightGBM model: {e}")
        
        # Create and train a simple model with mock data
        logger.info("Training new LightGBM model with mock data")
        self._train_mock_model()
    
    def _train_mock_model(self):
        """Train a simple LightGBM model with mock data."""
        # Generate mock training data
        np.random.seed(42)
        n_samples = 1000
        
        # Features: base_ctr, interest_match, budget_compat, category_div, price_tier, user_type
        X = np.random.rand(n_samples, len(self.feature_names))
        
        # Mock target: higher CTR for better feature combinations
        y = (X[:, 0] * 0.4 +  # base_ctr weight
             X[:, 1] * 0.3 +  # interest_match weight
             X[:, 2] * 0.2 +  # budget_compatibility weight
             X[:, 3] * 0.1 +  # category_diversity weight
             np.random.normal(0, 0.05, n_samples))  # noise
        
        # Clip to reasonable CTR range
        y = np.clip(y, 0.01, 0.5)
        
        # Train LightGBM model
        train_data = lgb.Dataset(X, label=y, feature_name=self.feature_names)
        
        params = {
            'objective': 'regression',
            'metric': 'rmse',
            'boosting_type': 'gbdt',
            'num_leaves': 31,
            'learning_rate': 0.05,
            'feature_fraction': 0.9,
            'bagging_fraction': 0.8,
            'bagging_freq': 5,
            'verbose': -1
        }
        
        self.model = lgb.train(
            params,
            train_data,
            num_boost_round=100,
            valid_sets=[train_data],
            callbacks=[lgb.early_stopping(10), lgb.log_evaluation(0)]
        )
        
        # Save the model
        os.makedirs("models", exist_ok=True)
        self.model.save_model("models/lightgbm_ranker.txt")
        logger.info("LightGBM model trained and saved")
    
    def rank_promotions(self, candidates: List[Dict[str, Any]], user_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Rank promotion candidates based on predicted CTR/CVR.
        
        Args:
            candidates: List of promotion candidates
            user_profile: User profile for personalization
            
        Returns:
            List of ranked promotions with scores
        """
        if not candidates:
            return []
        
        # Extract features for each candidate
        features = []
        for candidate in candidates:
            feature_vector = self._extract_features(candidate, user_profile)
            features.append(feature_vector)
        
        features_array = np.array(features)
        
        # Predict scores
        if self.model_type == "lightgbm" and self.model is not None:
            scores = self.model.predict(features_array)
        else:
            scores = self._mock_predict(features_array)
        
        # Create ranked results
        ranked_promotions = []
        for i, (candidate, score) in enumerate(zip(candidates, scores)):
            ranked_promotion = {
                "id": candidate.get("id", f"promo_{i}"),
                "score": float(score)
            }
            ranked_promotions.append(ranked_promotion)
        
        # Sort by score (descending)
        ranked_promotions.sort(key=lambda x: x["score"], reverse=True)
        
        return ranked_promotions
    
    def _extract_features(self, promotion: Dict[str, Any], user_profile: Dict[str, Any]) -> List[float]:
        """Extract features for ranking model."""
        features = []
        
        # Base CTR from promotion data
        base_ctr = promotion.get("base_ctr", 0.1)
        features.append(base_ctr)
        
        # Interest matching score
        user_interests = set(user_profile.get("interests", []))
        promo_categories = set(promotion.get("categories", []))
        interest_match = len(user_interests & promo_categories) / max(len(user_interests), 1)
        features.append(interest_match)
        
        # Budget compatibility
        user_budget = user_profile.get("budget_level", "medium")
        promo_price_tier = promotion.get("price_tier", "medium")
        budget_compat = self._calculate_budget_compatibility(user_budget, promo_price_tier)
        features.append(budget_compat)
        
        # Category diversity (how many categories the promotion covers)
        category_diversity = len(promotion.get("categories", [])) / 10.0  # normalize
        features.append(category_diversity)
        
        # Price tier as numeric
        price_tier_map = {"low": 0.0, "medium": 0.5, "high": 1.0}
        price_tier_numeric = price_tier_map.get(promo_price_tier, 0.5)
        features.append(price_tier_numeric)
        
        # User type as numeric
        user_type_map = {"casual": 0.0, "professional": 0.5, "enterprise": 1.0}
        user_type_numeric = user_type_map.get(user_profile.get("user_type", "casual"), 0.0)
        features.append(user_type_numeric)
        
        return features
    
    def _calculate_budget_compatibility(self, user_budget: str, promo_price_tier: str) -> float:
        """Calculate compatibility between user budget and promotion price tier."""
        compatibility_matrix = {
            ("low", "low"): 1.0,
            ("low", "medium"): 0.3,
            ("low", "high"): 0.1,
            ("medium", "low"): 0.8,
            ("medium", "medium"): 1.0,
            ("medium", "high"): 0.6,
            ("high", "low"): 0.9,
            ("high", "medium"): 0.9,
            ("high", "high"): 1.0,
        }
        
        return compatibility_matrix.get((user_budget, promo_price_tier), 0.5)
    
    def _mock_predict(self, features: np.ndarray) -> np.ndarray:
        """Mock prediction when LightGBM is not available."""
        # Simple weighted combination of features
        weights = np.array([0.4, 0.3, 0.2, 0.05, 0.03, 0.02])
        scores = np.dot(features, weights)
        
        # Add some randomness
        np.random.seed(hash(str(features.tobytes())) % 2**32)
        noise = np.random.normal(0, 0.02, len(scores))
        scores += noise
        
        # Ensure scores are in reasonable range
        scores = np.clip(scores, 0.01, 0.5)
        
        return scores


# Global ranker instance
_ranker = None


def get_ranker() -> PromotionRanker:
    """Get or create the global ranker instance."""
    global _ranker
    if _ranker is None:
        _ranker = PromotionRanker()
    return _ranker
