from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from utils.config import Config
from utils.prompts import TONE_ANALYSIS_PROMPT
import logging

class ToneAnalysisAgent:
    """Agent responsible for analyzing tone of voice from user examples"""
    
    def __init__(self):
        self.config = Config()
        self.llm = ChatOpenAI(
            api_key=self.config.openai_api_key,
            model=self.config.openai_model,
            temperature=0.3
        )
        self.prompt = PromptTemplate(
            input_variables=["tone_sample"],
            template=TONE_ANALYSIS_PROMPT
        )
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt)
        self.logger = logging.getLogger(__name__)
    
    def analyze_tone(self, tone_sample: str) -> dict:
        """
        Analyze the tone and style from the provided text sample
        
        Args:
            tone_sample (str): User's writing sample
            
        Returns:
            dict: Tone analysis results
        """
        try:
            self.logger.info("Starting tone analysis")
            
            if not tone_sample or len(tone_sample.strip()) < 10:
                raise ValueError("Tone sample must be at least 10 characters long")
            
            # Run the analysis
            result = self.chain.run(tone_sample=tone_sample)
            
            # Parse and structure the result
            analysis = {
                "raw_analysis": result,
                "tone_sample": tone_sample,
                "status": "completed",
                "characteristics": self._extract_characteristics(result)
            }
            
            self.logger.info("Tone analysis completed successfully")
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error in tone analysis: {str(e)}")
            return {
                "error": str(e),
                "status": "error",
                "tone_sample": tone_sample
            }
    
    def _extract_characteristics(self, analysis_text: str) -> dict:
        """Extract key characteristics from the analysis text"""
        characteristics = {
            "formality": "unknown",
            "energy": "unknown", 
            "expertise": "unknown",
            "personality": "unknown"
        }
        
        # Simple keyword-based extraction (could be enhanced with NLP)
        text_lower = analysis_text.lower()
        
        # Formality detection
        if any(word in text_lower for word in ["formal", "professional", "business"]):
            characteristics["formality"] = "formal"
        elif any(word in text_lower for word in ["casual", "informal", "conversational"]):
            characteristics["formality"] = "casual"
        
        # Energy detection
        if any(word in text_lower for word in ["energetic", "enthusiastic", "excited"]):
            characteristics["energy"] = "high"
        elif any(word in text_lower for word in ["calm", "measured", "steady"]):
            characteristics["energy"] = "moderate"
        
        # Expertise detection
        if any(word in text_lower for word in ["expert", "technical", "authoritative"]):
            characteristics["expertise"] = "high"
        elif any(word in text_lower for word in ["beginner", "learning", "accessible"]):
            characteristics["expertise"] = "accessible"
        
        return characteristics
    
    def get_tone_summary(self, analysis: dict) -> str:
        """Get a concise summary of the tone analysis"""
        if "error" in analysis:
            return f"Error: {analysis['error']}"
        
        characteristics = analysis.get("characteristics", {})
        summary_parts = []
        
        for key, value in characteristics.items():
            if value != "unknown":
                summary_parts.append(f"{key}: {value}")
        
        return "; ".join(summary_parts) if summary_parts else "Tone analysis completed" 