import sys
import os
from dotenv import load_dotenv

# Add the project root to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

load_dotenv()

from src.vector_store import VectorStoreBuilder
from src.recommender import AnimeRecommender
from utils.logger import get_logger
from utils.custom_exception import CustomException

logger = get_logger(__name__)

class AnimeRecommendationPipeline:
    def __init__(self,persist_dir="chroma_db"):
        try:
            logger.info("Intializing Recommdation Pipeline")

            vector_builder = VectorStoreBuilder(csv_path="" , persist_directory=persist_dir)

            retriever = vector_builder.load_vector_store().as_retriever()

            # Get API key and model name directly from environment
            api_key = os.getenv("GROQ_API_KEY")
            model_name = "llama-3.1-8b-instant"
            
            self.recommender = AnimeRecommender(retriever, api_key, model_name)

            logger.info("Pipleine intialized sucesfully...")

        except Exception as e:
            logger.error(f"Failed to intialize pipeline {str(e)}")
            raise CustomException("Error during pipeline intialization" , e)
        
    def recommend(self,query:str) -> str:
        try:
            logger.info(f"Recived a query {query}")

            recommendation = self.recommender.get_recommendation(query)

            logger.info("Recommendation generated sucesfulyy...")
            return recommendation
        except Exception as e:
            logger.error(f"Failed to get recommendation {str(e)}")
            raise CustomException("Error during getting recommendation" , e)
        


        