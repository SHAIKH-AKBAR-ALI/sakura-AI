from langchain_openai import ChatOpenAI
from src.prompt_template import get_anime_prompt

class AnimeRecommender:
    def __init__(self,retriever,api_key:str,model_name:str="gpt-4o-mini"):
        self.llm = ChatOpenAI(api_key=api_key, model=model_name, temperature=0)
        self.prompt = get_anime_prompt()
        self.retriever = retriever

    def get_recommendation(self,query:str):
        # Pre-filter: Handle ONLY basic greetings without using context
        greeting_words = ['hello', 'hi', 'hey', 'greetings', 'good morning', 'good afternoon']
        # Only filter if it's EXACTLY a greeting (not anime names)
        if (any(query.lower().strip() == word for word in greeting_words) or 
            (any(word in query.lower() for word in greeting_words) and len(query.split()) <= 2)):
            return "Hello! I'm here to help you discover amazing anime. What kind of shows are you interested in?"
        
        # For everything else (including anime names), use the full pipeline
        # Retrieve relevant documents
        docs = self.retriever.invoke(query)
        
        # Combine documents into context
        context = "\n\n".join([doc.page_content for doc in docs])
        
        # Format the prompt with context and query
        formatted_prompt = self.prompt.format(context=context, question=query)
        
        # Get response from LLM
        response = self.llm.invoke(formatted_prompt)
        return response.content