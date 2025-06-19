from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from utils.config import Config
from utils.prompts import CONTENT_CREATION_PROMPT
import logging
import re

class ContentCreationAgent:
    """Agent responsible for creating LinkedIn post content"""
    
    def __init__(self):
        self.config = Config()
        self.llm = ChatOpenAI(
            api_key=self.config.openai_api_key,
            model=self.config.openai_model,
            temperature=0.7  # Higher temperature for more creative content
        )
        self.prompt = PromptTemplate(
            input_variables=["tone_profile", "research_data", "topic", "language_instruction"],
            template=CONTENT_CREATION_PROMPT
        )
        self.chain = LLMChain(llm=self.llm, prompt=self.prompt)
        self.logger = logging.getLogger(__name__)
    
    def create_content(self, tone_analysis: dict, research_data: dict, topic: str) -> dict:
        """
        Create LinkedIn post content based on tone analysis and research
        
        Args:
            tone_analysis (dict): Results from tone analysis agent
            research_data (dict): Results from research agent
            topic (str): The content topic
            
        Returns:
            dict: Generated content and metadata
        """
        try:
            self.logger.info(f"Starting content creation for topic: {topic}")
            
            # Prepare inputs
            tone_profile = self._format_tone_profile(tone_analysis)
            research_summary = self._format_research_data(research_data)
            
            # Generate the content
            post_content = self.chain.run(
                tone_profile=tone_profile,
                research_data=research_summary,
                topic=topic
            )
            
            # Process and enhance the content
            processed_content = self._process_content(post_content)
            
            content_result = {
                "post_content": processed_content,
                "original_content": post_content,
                "topic": topic,
                "status": "completed",
                "word_count": len(processed_content.split()),
                "hashtags": self._extract_hashtags_from_content(processed_content),
                "call_to_action": self._extract_call_to_action(processed_content)
            }
            
            self.logger.info("Content creation completed successfully")
            return content_result
            
        except Exception as e:
            self.logger.error(f"Error in content creation: {str(e)}")
            return {
                "error": str(e),
                "status": "error",
                "topic": topic
            }
    
    def _format_tone_profile(self, tone_analysis: dict) -> str:
        """Format tone analysis for the content prompt"""
        if "error" in tone_analysis:
            return "No tone analysis available"
        
        profile_parts = []
        
        # Add raw analysis
        if "raw_analysis" in tone_analysis:
            profile_parts.append(f"Analysis: {tone_analysis['raw_analysis']}")
        
        # Add characteristics
        if "characteristics" in tone_analysis:
            chars = tone_analysis["characteristics"]
            char_desc = []
            for key, value in chars.items():
                if value != "unknown":
                    char_desc.append(f"{key}: {value}")
            if char_desc:
                profile_parts.append(f"Key characteristics: {', '.join(char_desc)}")
        
        return "\n".join(profile_parts)
    
    def _format_research_data(self, research_data: dict) -> str:
        """Format research data for the content prompt"""
        if "error" in research_data:
            return "No research data available"
        
        research_parts = []
        
        # Add analysis
        if "analysis" in research_data:
            research_parts.append(f"Research Analysis: {research_data['analysis']}")
        
        # Add insights
        if "insights" in research_data and research_data["insights"]:
            research_parts.append(f"Key Insights: {'; '.join(research_data['insights'])}")
        
        # Add hashtags
        if "hashtags" in research_data and research_data["hashtags"]:
            research_parts.append(f"Relevant Hashtags: {' '.join(research_data['hashtags'])}")
        
        return "\n".join(research_parts)
    
    def _process_content(self, content: str) -> str:
        """Process and clean up the generated content"""
        # Remove excessive newlines
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        # Ensure proper LinkedIn formatting
        content = content.strip()
        
        # Add line breaks before hashtags if they're at the end
        if '#' in content:
            lines = content.split('\n')
            processed_lines = []
            for line in lines:
                if line.strip().startswith('#') and processed_lines and not processed_lines[-1].strip() == '':
                    processed_lines.append('')  # Add blank line before hashtags
                processed_lines.append(line)
            content = '\n'.join(processed_lines)
        
        return content
    
    def _extract_hashtags_from_content(self, content: str) -> list:
        """Extract hashtags from the generated content"""
        hashtag_pattern = r'#\w+'
        hashtags = re.findall(hashtag_pattern, content)
        return list(set(hashtags))  # Remove duplicates
    
    def _extract_call_to_action(self, content: str) -> str:
        """Extract or identify the call to action"""
        # Look for common CTA patterns
        cta_patterns = [
            r'What.*think\?',
            r'Share.*thoughts',
            r'Let.*know',
            r'Comment.*below',
            r'What.*experience',
            r'How.*handle'
        ]
        
        for pattern in cta_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group()
        
        # If no specific CTA found, look for question marks in the last paragraph
        lines = content.split('\n')
        for line in reversed(lines):
            if '?' in line:
                return line.strip()
        
        return "No specific call to action identified"
    
    def get_content_summary(self, content_result: dict) -> str:
        """Get a summary of the generated content"""
        if "error" in content_result:
            return f"Error: {content_result['error']}"
        
        word_count = content_result.get("word_count", 0)
        hashtag_count = len(content_result.get("hashtags", []))
        
        return f"Generated {word_count} word post with {hashtag_count} hashtags"
    
    def optimize_for_linkedin(self, content: str) -> str:
        """Optimize content specifically for LinkedIn's algorithm and best practices"""
        lines = content.split('\n')
        optimized_lines = []
        
        for line in lines:
            # Ensure line length is reasonable (LinkedIn performs better with shorter lines)
            if len(line) > 100 and not line.strip().startswith('#'):
                # Try to break long lines at natural points
                words = line.split()
                current_line = []
                for word in words:
                    if len(' '.join(current_line + [word])) > 100:
                        optimized_lines.append(' '.join(current_line))
                        current_line = [word]
                    else:
                        current_line.append(word)
                if current_line:
                    optimized_lines.append(' '.join(current_line))
            else:
                optimized_lines.append(line)
        
        return '\n'.join(optimized_lines) 