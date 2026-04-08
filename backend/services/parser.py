"""Curriculum parsing and topic extraction logic."""
import json
import os
import base64
from typing import Optional
from google import genai
from google.genai import types
from sentence_transformers import SentenceTransformer
from models.schemas import TopicExtraction, ParseResult


class CurriculumParser:
    """Parses curriculum documents and extracts topics using Gemini multimodal + S-BERT embeddings."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize parser with Gemini API and S-BERT embeddings."""
        self.client = genai.Client(api_key=api_key)
        self.model_id = "gemini-3-flash-preview"
        # Load S-BERT model for semantic embeddings (384-dimensional vectors)
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

    async def extract_topics_from_file(self, file_bytes: bytes, file_name: str) -> ParseResult:
        """Extract topics directly from file bytes using Gemini's multimodal capabilities.
        
        Supports PDF, DOCX, and text files without manual parsing.
        Gemini 3 can read PDFs natively and understand structure/formatting.
        """
        try:
            # Determine MIME type from filename
            mime_type = "application/pdf"
            if file_name.endswith(".txt"):
                mime_type = "text/plain"
            elif file_name.endswith(".docx"):
                mime_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            
            # Send file bytes directly to Gemini with multimodal support
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=[
                    types.Part.from_bytes(
                        data=file_bytes,
                        mime_type=mime_type
                    ),
                    """Analyze this curriculum/syllabus document and extract all major topics and subtopics.
For each topic, provide:
1. Topic name
2. Brief description (1-2 sentences)
3. List of subtopics
4. Estimated difficulty level (beginner, intermediate, advanced)

Return the response as a JSON array of objects with keys: name, description, subtopics, difficulty_level.
Only return valid JSON, no additional text."""
                ]
            )
            
            response_text = response.text

            # Parse JSON response
            try:
                topics_data = json.loads(response_text)
            except json.JSONDecodeError:
                # Try to extract JSON from response
                start = response_text.find("[")
                end = response_text.rfind("]") + 1
                if start >= 0 and end > start:
                    topics_data = json.loads(response_text[start:end])
                else:
                    raise ValueError("Could not parse LLM response as JSON")

            topics = [
                TopicExtraction(
                    name=t.get("name", ""),
                    description=t.get("description", ""),
                    subtopics=t.get("subtopics", []),
                    difficulty_level=t.get("difficulty_level", "intermediate"),
                )
                for t in topics_data
                if isinstance(topics_data, list)
            ]

            return ParseResult(
                success=True,
                topics=topics,
                raw_text="",
                error=None,
            )

        except Exception as e:
            return ParseResult(
                success=False,
                topics=[],
                error=f"Topic extraction failed: {str(e)}",
            )

    async def embed_topics(self, topics: list[TopicExtraction]) -> list[dict]:
        """Generate S-BERT embeddings for extracted topics.
        
        Args:
            topics: List of TopicExtraction objects
        
        Returns:
            List of dicts with topic data and embeddings
        """
        try:
            # Extract topic names to embed
            topic_names = [t.name for t in topics]
            
            # Generate embeddings (returns numpy arrays)
            embeddings = self.embedding_model.encode(topic_names, convert_to_tensor=False)
            
            # Format as list of dicts with all topic data and embeddings
            topics_with_embeddings = [
                {
                    "topic_name": t.name,
                    "description": t.description,
                    "subtopics": t.subtopics or [],
                    "difficulty_level": t.difficulty_level or "intermediate",
                    "embedding": embeddings[i].tolist(),  # Convert numpy array to list
                }
                for i, t in enumerate(topics)
            ]
            
            return topics_with_embeddings
        except Exception as e:
            raise ValueError(f"Failed to embed topics: {str(e)}")

    async def generate_curriculum_summary(self, curriculum_text: str) -> str:
        """Generate a summary of the curriculum."""
        try:
            prompt = f"""Provide a brief 2-3 sentence summary of this curriculum:

{curriculum_text[:1500]}

Summary should highlight the main learning objectives and scope."""

            response = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt
            )
            return response.text.strip()
        except Exception as e:
            return f"Failed to generate summary: {str(e)}"


# Global parser instance
_parser: Optional[CurriculumParser] = None


def get_parser() -> CurriculumParser:
    """Get or create parser instance."""
    global _parser
    if _parser is None:
        _parser = CurriculumParser(api_key=os.getenv("GEMINI_API_KEY"))
    return _parser
