from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from utils.config import Config
from utils.prompts import RESEARCH_PROMPT
import logging

class ResearchAgent:
    """Agent responsible for researching topics using Tavily Search API"""
    
    def __init__(self):
        self.config = Config()
        self.llm = ChatOpenAI(
            api_key=self.config.openai_api_key,
            model=self.config.openai_model,
            temperature=0.2
        )
        self.search_tool = TavilySearchResults(
            api_key=self.config.tavily_api_key,
            max_results=self.config.tavily_max_results
        )
        self.prompt = PromptTemplate(
            input_variables=["topic", "search_results", "language", "language_instruction"],
            template=RESEARCH_PROMPT + "\n\nSearch Results: {search_results}"
        )
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt)
        self.logger = logging.getLogger(__name__)
    
    def research_topic(self, topic: str) -> dict:
        """
        Research the given topic using Tavily search and AI analysis
        
        Args:
            topic (str): The topic to research
            
        Returns:
            dict: Research results and analysis
        """
        try:
            self.logger.info(f"Starting research for topic: {topic}")
            
            if not topic or len(topic.strip()) < 3:
                raise ValueError("Topic must be at least 3 characters long")
            
            # Perform the search
            search_results = self.search_tool.run(topic)
            
            # Analyze and synthesize the search results
            analysis = self.chain.run(
                topic=topic,
                search_results=self._format_search_results(search_results)
            )
            
            research_data = {
                "topic": topic,
                "search_results": search_results,
                "analysis": analysis,
                "status": "completed",
                "insights": self._extract_insights(analysis),
                "hashtags": self._extract_hashtags(analysis)
            }
            
            self.logger.info("Research completed successfully")
            return research_data
            
        except Exception as e:
            self.logger.error(f"Error in research: {str(e)}")
            return {
                "error": str(e),
                "status": "error",
                "topic": topic
            }
    
    def _format_search_results(self, search_results) -> str:
        """Format search results for the LLM prompt"""
        if isinstance(search_results, list):
            formatted_results = []
            for i, result in enumerate(search_results[:5], 1):
                if isinstance(result, dict):
                    title = result.get('title', 'No title')
                    content = result.get('content', result.get('snippet', 'No content'))
                    url = result.get('url', 'No URL')
                    formatted_results.append(f"{i}. {title}\n   {content}\n   Source: {url}\n")
                else:
                    formatted_results.append(f"{i}. {str(result)}\n")
            return "\n".join(formatted_results)
        else:
            return str(search_results)
    
    def _extract_insights(self, analysis_text: str) -> list:
        """Extract key insights from the analysis"""
        insights = []
        
        # Look for numbered lists or bullet points
        lines = analysis_text.split('\n')
        for line in lines:
            line = line.strip()
            if line and (line.startswith(('1.', '2.', '3.', '4.', '5.', '-', '•'))):
                insights.append(line)
        
        return insights[:5]  # Return top 5 insights
    
    def _extract_hashtags(self, analysis_text: str) -> list:
        """Extract relevant hashtags from the analysis"""
        import re
        
        # Look for hashtag mentions in the text
        hashtag_pattern = r'#\w+'
        hashtags = re.findall(hashtag_pattern, analysis_text)
        
        # If no hashtags found, generate some based on common patterns
        if not hashtags:
            text_lower = analysis_text.lower()
            potential_hashtags = []
            
            # Common LinkedIn hashtags based on content
            if 'ai' in text_lower or 'artificial intelligence' in text_lower:
                potential_hashtags.extend(['#AI', '#ArtificialIntelligence', '#MachineLearning'])
            if 'marketing' in text_lower:
                potential_hashtags.extend(['#Marketing', '#DigitalMarketing', '#MarketingStrategy'])
            if 'leadership' in text_lower:
                potential_hashtags.extend(['#Leadership', '#Management', '#ProfessionalDevelopment'])
            if 'remote' in text_lower or 'work from home' in text_lower:
                potential_hashtags.extend(['#RemoteWork', '#WorkFromHome', '#FutureOfWork'])
            
            hashtags = potential_hashtags[:5]
        
        return list(set(hashtags))  # Remove duplicates
    
    def get_research_summary(self, research_data: dict) -> str:
        """Get a concise summary of the research"""
        if "error" in research_data:
            return f"Error: {research_data['error']}"
        
        insights = research_data.get("insights", [])
        if insights:
            return f"Found {len(insights)} key insights about {research_data['topic']}"
        else:
            return f"Research completed for topic: {research_data['topic']}" 