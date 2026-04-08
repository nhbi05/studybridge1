"""Curriculum parsing and topic extraction logic."""
import json
import os
import PyPDF2
from typing import Optional
from io import BytesIO
from google import genai
from sentence_transformers import SentenceTransformer
from models.schemas import TopicExtraction, ParseResult


class CurriculumParser:
    """Parses curriculum documents and extracts topics using LLM + S-BERT embeddings."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize parser with Gemini API and S-BERT embeddings."""
        self.client = genai.Client(api_key=api_key)
        self.model_id = "gemini-3-flash"
        # Load S-BERT model for semantic embeddings (384-dimensional vectors)
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

    async def parse_pdf(self, file_content: bytes) -> str:
        """Extract text from PDF file."""
        try:
            pdf_reader = PyPDF2.PdfReader(BytesIO(file_content))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            raise ValueError(f"Failed to parse PDF: {str(e)}")

    async def parse_text_file(self, file_content: bytes) -> str:
        """Parse text file."""
        try:
            return file_content.decode("utf-8").strip()
        except Exception as e:
            raise ValueError(f"Failed to parse text file: {str(e)}")

    async def extract_topics(self, curriculum_text: str) -> ParseResult:
        """Extract topics from curriculum text using Gemini."""
        try:
            prompt = f"""Analyze the following curriculum and extract all major topics and subtopics. 
For each topic, provide:
1. Topic name
2. Brief description (1-2 sentences)
3. List of subtopics
4. Estimated difficulty level (beginner, intermediate, advanced)

Curriculum text:
{curriculum_text[:2000]}  # Limit to first 2000 chars for API efficiency

Return the response as a JSON array of objects with keys: name, description, subtopics, difficulty_level.
Only return valid JSON, no additional text."""

            response = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt
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
                raw_text=curriculum_text[:500],
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
            List of dicts with keys: topic_name, embedding (list[float])
        """
        try:
            # Extract topic names to embed
            topic_names = [t.name for t in topics]
            
            # Generate embeddings (returns numpy arrays)
            embeddings = self.embedding_model.encode(topic_names, convert_to_tensor=False)
            
            # Format as list of dicts with topic names and embeddings
            topics_with_embeddings = [
                {
                    "topic_name": name,
                    "embedding": embeddings[i].tolist(),  # Convert numpy array to list
                }
                for i, name in enumerate(topic_names)
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
