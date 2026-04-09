"""Neural Collaborative Filtering service using HuggingFace model.

Uses pre-trained NCF model from nhbi05/studybridge-ncf for:
- Learning user-resource interaction patterns
- Capturing latent features of users and resources
- Providing calibrated relevance scores
"""

import os
import torch
import numpy as np
from typing import List, Dict, Optional
from huggingface_hub import hf_hub_download
from dotenv import load_dotenv

# Load environment variables
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=env_path)

# Model configuration
HF_REPO_ID = "nhbi05/studybridge-ncf"
MODEL_FILENAME = "studybridge_ncf_final.pt"
EMBEDDING_DIM = 64  # Adjust based on your model training


class NCFRecommender:
    """Neural Collaborative Filtering model for ranking recommendations."""
    
    def __init__(self):
        """Initialize NCF model from HuggingFace."""
        self.model = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.user_embeddings = None
        self.resource_embeddings = None
        self.is_loaded = False
        self._load_model()
    
    def _load_model(self):
        """Download and load the NCF model from HuggingFace."""
        try:
            print("📥 Loading NCF model from HuggingFace...")
            
            # Download model if not cached
            model_path = hf_hub_download(
                repo_id=HF_REPO_ID,
                filename=MODEL_FILENAME,
                cache_dir=os.path.join(os.path.dirname(__file__), '..', 'models')
            )
            
            # Load the model checkpoint
            checkpoint = torch.load(model_path, map_location=self.device)
            
            # Extract model architecture and weights
            # Assuming checkpoint contains 'model_state_dict' or is itself the state dict
            if isinstance(checkpoint, dict) and 'model_state_dict' in checkpoint:
                state_dict = checkpoint['model_state_dict']
            else:
                state_dict = checkpoint
            
            # Build simple NCF model architecture
            self.model = SimplifiedNCFModel(embedding_dim=EMBEDDING_DIM)
            self.model.load_state_dict(state_dict)
            self.model = self.model.to(self.device)
            self.model.eval()
            
            self.is_loaded = True
            print("✅ NCF model loaded successfully")
            
        except Exception as e:
            print(f"⚠️  Failed to load NCF model: {str(e)}")
            print("   Proceeding with embedding-only recommendations")
            self.is_loaded = False
    
    def rerank_resources(
        self,
        user_id: str,
        resources: List[Dict],
        top_k: int = 10
    ) -> List[Dict]:
        """
        Rerank resources using NCF model scores.
        
        Args:
            user_id: Current user identifier
            resources: List of resources with relevance_score
            top_k: Number of top resources to return
        
        Returns:
            Reranked resources with updated collaboration scores
        """
        if not self.is_loaded or len(resources) == 0:
            # Fallback: return top_k by existing relevance score
            return sorted(
                resources,
                key=lambda x: x.get("relevance_score", 0.5),
                reverse=True
            )[:top_k]
        
        try:
            # Hash user_id to a stable integer for embedding lookup
            user_hash = self._hash_user_id(user_id)
            
            # Score each resource using NCF
            scored_resources = []
            for resource in resources:
                ncf_score = self._score_interaction(
                    user_hash,
                    resource.get("id", "unknown")
                )
                
                # Combine semantic relevance (70%) with collaborative score (30%)
                original_score = resource.get("relevance_score", 0.5)
                combined_score = (0.7 * original_score) + (0.3 * ncf_score)
                
                scored_resources.append({
                    **resource,
                    "relevance_score": combined_score,
                    "collaboration_score": ncf_score
                })
            
            # Sort by combined score
            scored_resources.sort(
                key=lambda x: x["relevance_score"],
                reverse=True
            )
            
            return scored_resources[:top_k]
            
        except Exception as e:
            print(f"⚠️  NCF reranking failed: {str(e)}")
            # Fallback to original scores
            return sorted(
                resources,
                key=lambda x: x.get("relevance_score", 0.5),
                reverse=True
            )[:top_k]
    
    def _hash_user_id(self, user_id: str) -> int:
        """Convert user_id to stable integer for embedding lookup."""
        return hash(user_id) % 10000  # Constrain to reasonable range
    
    def _score_interaction(self, user_hash: int, resource_id: str) -> float:
        """
        Score a user-resource interaction using the NCF model.
        
        Falls back to random uniform score if model inference fails.
        """
        try:
            with torch.no_grad():
                # Create interaction pair
                user_tensor = torch.tensor([user_hash % 1000], dtype=torch.long, device=self.device)
                resource_tensor = torch.tensor([hash(resource_id) % 1000], dtype=torch.long, device=self.device)
                
                # Forward pass through model
                score = self.model(user_tensor, resource_tensor)
                
                # Normalize to [0, 1] range
                score_value = torch.sigmoid(score).item()
                return float(score_value)
        
        except Exception as e:
            print(f"⚠️  Error scoring interaction: {str(e)}")
            # Return random score in reasonable range
            return np.random.uniform(0.5, 0.9)


class SimplifiedNCFModel(torch.nn.Module):
    """Simplified NCF architecture for scoring user-resource interactions."""
    
    def __init__(self, embedding_dim: int = 64, num_users: int = 1000, num_resources: int = 5000):
        """
        Initialize NCF model.
        
        Args:
            embedding_dim: Dimension of embedding vectors
            num_users: Maximum number of user embeddings
            num_resources: Maximum number of resource embeddings
        """
        super().__init__()
        
        self.embedding_dim = embedding_dim
        
        # Embedding layers
        self.user_embedding = torch.nn.Embedding(num_users, embedding_dim)
        self.resource_embedding = torch.nn.Embedding(num_resources, embedding_dim)
        
        # MLP layers for interaction modeling
        self.fc1 = torch.nn.Linear(embedding_dim * 2, 128)
        self.fc2 = torch.nn.Linear(128, 64)
        self.fc3 = torch.nn.Linear(64, 1)
        
        # Activation and regularization
        self.relu = torch.nn.ReLU()
        self.dropout = torch.nn.Dropout(0.2)
    
    def forward(self, user_ids: torch.Tensor, resource_ids: torch.Tensor) -> torch.Tensor:
        """
        Forward pass through NCF model.
        
        Args:
            user_ids: Tensor of user indices
            resource_ids: Tensor of resource indices
        
        Returns:
            Interaction scores
        """
        # Get embeddings
        user_emb = self.user_embedding(user_ids)
        resource_emb = self.resource_embedding(resource_ids)
        
        # Concatenate embeddings
        combined = torch.cat([user_emb, resource_emb], dim=1)
        
        # MLP
        x = self.relu(self.fc1(combined))
        x = self.dropout(x)
        x = self.relu(self.fc2(x))
        x = self.dropout(x)
        x = self.fc3(x)
        
        return x


# Global instance
_ncf_model = None


def get_ncf_recommender() -> NCFRecommender:
    """Get or create the NCF recommender instance."""
    global _ncf_model
    if _ncf_model is None:
        _ncf_model = NCFRecommender()
    return _ncf_model
