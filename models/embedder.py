"""
Embedding model for semantic search functionality.
"""

import os
import pickle
import numpy as np
from typing import List, Dict, Any, Optional
from loguru import logger

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    logger.warning("sentence-transformers not available, using mock embeddings")


class EmbeddingModel:
    """Handles text embeddings for semantic search."""
    
    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
        self.model = None
        self.cache_path = os.getenv("EMBEDDINGS_CACHE_PATH", "data/embeddings/")
        os.makedirs(self.cache_path, exist_ok=True)
        
        self._load_model()
    
    def _load_model(self):
        """Load the sentence transformer model."""
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            try:
                logger.info(f"Loading embedding model: {self.model_name}")
                self.model = SentenceTransformer(self.model_name)
                logger.info("Embedding model loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load embedding model: {e}")
                self.model = None
        else:
            logger.warning("Using mock embedding model")
            self.model = None
    
    def encode(self, texts: List[str]) -> np.ndarray:
        """
        Encode texts into embeddings.
        
        Args:
            texts: List of text strings to encode
            
        Returns:
            numpy array of embeddings
        """
        if self.model is not None:
            try:
                embeddings = self.model.encode(texts, convert_to_numpy=True)
                return embeddings
            except Exception as e:
                logger.error(f"Error encoding texts: {e}")
                return self._mock_embeddings(texts)
        else:
            return self._mock_embeddings(texts)
    
    def _mock_embeddings(self, texts: List[str]) -> np.ndarray:
        """Generate mock embeddings based on text characteristics."""
        embeddings = []
        for text in texts:
            # Simple hash-based mock embedding
            text_hash = hash(text.lower()) % 1000000
            # Create a 384-dimensional vector (same as all-MiniLM-L6-v2)
            np.random.seed(text_hash)
            embedding = np.random.normal(0, 1, 384)
            # Normalize
            embedding = embedding / np.linalg.norm(embedding)
            embeddings.append(embedding)
        
        return np.array(embeddings)
    
    def similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """Calculate cosine similarity between two embeddings."""
        return np.dot(embedding1, embedding2) / (
            np.linalg.norm(embedding1) * np.linalg.norm(embedding2)
        )
    
    def save_embeddings(self, embeddings: np.ndarray, filename: str):
        """Save embeddings to cache."""
        filepath = os.path.join(self.cache_path, f"{filename}.pkl")
        with open(filepath, 'wb') as f:
            pickle.dump(embeddings, f)
        logger.info(f"Embeddings saved to {filepath}")
    
    def load_embeddings(self, filename: str) -> Optional[np.ndarray]:
        """Load embeddings from cache."""
        filepath = os.path.join(self.cache_path, f"{filename}.pkl")
        if os.path.exists(filepath):
            with open(filepath, 'rb') as f:
                embeddings = pickle.load(f)
            logger.info(f"Embeddings loaded from {filepath}")
            return embeddings
        return None


class PromotionIndex:
    """Index for fast semantic search over promotions."""
    
    def __init__(self, embedder: EmbeddingModel):
        self.embedder = embedder
        self.promotions: List[Dict[str, Any]] = []
        self.embeddings: Optional[np.ndarray] = None
        self.index_built = False
    
    def add_promotions(self, promotions: List[Dict[str, Any]]):
        """Add promotions to the index."""
        self.promotions.extend(promotions)
        self.index_built = False
        logger.info(f"Added {len(promotions)} promotions to index")
    
    def build_index(self, force_rebuild: bool = False):
        """Build the embedding index for all promotions."""
        if self.index_built and not force_rebuild:
            return
        
        if not self.promotions:
            logger.warning("No promotions to index")
            return
        
        # Try to load cached embeddings
        cached_embeddings = self.embedder.load_embeddings("promotion_embeddings")
        if cached_embeddings is not None and len(cached_embeddings) == len(self.promotions) and not force_rebuild:
            self.embeddings = cached_embeddings
            self.index_built = True
            logger.info("Using cached promotion embeddings")
            return
        
        # Build embeddings
        logger.info(f"Building embeddings for {len(self.promotions)} promotions")
        texts = []
        for promo in self.promotions:
            # Combine title and description for embedding
            text = f"{promo.get('title', '')} {promo.get('description', '')}"
            texts.append(text)
        
        self.embeddings = self.embedder.encode(texts)
        self.index_built = True
        
        # Cache the embeddings
        self.embedder.save_embeddings(self.embeddings, "promotion_embeddings")
        logger.info("Promotion index built successfully")
    
    def search(self, query: str, top_k: int = 10, user_profile: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Search for promotions similar to the query.
        
        Args:
            query: Search query
            top_k: Number of results to return
            user_profile: User profile for personalization
            
        Returns:
            List of promotion results with scores
        """
        if not self.index_built:
            self.build_index()
        
        if not self.promotions or self.embeddings is None:
            return []
        
        # Encode query
        query_embedding = self.embedder.encode([query])[0]
        
        # Calculate similarities
        similarities = []
        for i, promo_embedding in enumerate(self.embeddings):
            similarity = self.embedder.similarity(query_embedding, promo_embedding)
            
            # Apply user profile boosting
            if user_profile:
                similarity = self._apply_user_profile_boost(similarity, self.promotions[i], user_profile)
            
            similarities.append((similarity, i))
        
        # Sort by similarity and return top_k
        similarities.sort(reverse=True)
        results = []
        
        for similarity, idx in similarities[:top_k]:
            promo = self.promotions[idx].copy()
            promo['score'] = float(similarity)
            results.append(promo)
        
        return results
    
    def _apply_user_profile_boost(self, base_score: float, promotion: Dict[str, Any], user_profile: Dict[str, Any]) -> float:
        """Apply user profile-based boosting to the similarity score."""
        boosted_score = base_score
        
        # Interest matching boost
        user_interests = set(user_profile.get('interests', []))
        promo_categories = set(promotion.get('categories', []))
        interest_overlap = len(user_interests & promo_categories)
        if interest_overlap > 0:
            boosted_score += 0.1 * interest_overlap
        
        # Budget level matching
        user_budget = user_profile.get('budget_level', 'medium')
        promo_price_tier = promotion.get('price_tier', 'medium')
        
        if user_budget == promo_price_tier:
            boosted_score += 0.05
        elif (user_budget == 'high' and promo_price_tier == 'medium') or \
             (user_budget == 'medium' and promo_price_tier == 'low'):
            boosted_score += 0.02
        
        return min(boosted_score, 1.0)  # Cap at 1.0
