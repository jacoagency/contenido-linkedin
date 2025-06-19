import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for API keys and settings"""
    
    def __init__(self):
        # API Keys
        self._openai_api_key = os.getenv("OPENAI_API_KEY")
        self._tavily_api_key = os.getenv("TAVILY_API_KEY")
        self._langchain_api_key = os.getenv("LANGCHAIN_API_KEY")
        
        # LangChain Settings
        self._langchain_tracing_v2 = os.getenv("LANGCHAIN_TRACING_V2", "false").lower() == "true"
        self._langchain_project = os.getenv("LANGCHAIN_PROJECT", "linkedin-content-creator")
        
        # OpenAI Settings
        self._openai_model = "gpt-4-turbo-preview"
        self._dalle_model = "dall-e-3"
        
        # Tavily Settings
        self._tavily_max_results = 5
    
    @property
    def openai_api_key(self) -> str:
        return self._openai_api_key
    
    @property
    def tavily_api_key(self) -> str:
        return self._tavily_api_key
    
    @property
    def langchain_api_key(self) -> str:
        return self._langchain_api_key
    
    @property
    def langchain_tracing_v2(self) -> bool:
        return self._langchain_tracing_v2
    
    @property
    def langchain_project(self) -> str:
        return self._langchain_project
    
    @property
    def openai_model(self) -> str:
        return self._openai_model
    
    @property
    def dalle_model(self) -> str:
        return self._dalle_model
    
    @property
    def tavily_max_results(self) -> int:
        return self._tavily_max_results
    
    def validate_keys(self) -> bool:
        """Validate that all required API keys are present"""
        missing_keys = []
        
        if not self._openai_api_key:
            missing_keys.append("OPENAI_API_KEY")
        if not self._tavily_api_key:
            missing_keys.append("TAVILY_API_KEY")
            
        if missing_keys:
            raise ValueError(f"Missing required API keys: {', '.join(missing_keys)}")
        
        return True 