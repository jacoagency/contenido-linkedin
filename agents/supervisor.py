from typing import Dict, Any, List, TypedDict
from langgraph.graph import StateGraph, END
from langchain.schema import HumanMessage
import logging

from agents.tone_agent import ToneAnalysisAgent
from agents.research_agent import ResearchAgent
from agents.content_agent import ContentCreationAgent
from agents.image_agent import ImageGenerationAgent
from utils.config import Config
from utils.prompts import SUPERVISOR_PLANNING_PROMPT

class WorkflowState(TypedDict):
    """State object for the workflow"""
    tone_sample: str
    topic: str
    language: str
    tone_analysis: Dict[str, Any]
    research_data: Dict[str, Any]
    content_result: Dict[str, Any]
    image_result: Dict[str, Any]
    current_step: str
    completed_steps: List[str]
    errors: List[str]
    status: str

class SupervisorAgent:
    """Supervisor agent that orchestrates the multi-agent workflow"""
    
    def __init__(self):
        # Initialize all agents
        self.tone_agent = ToneAnalysisAgent()
        self.research_agent = ResearchAgent()
        self.content_agent = ContentCreationAgent()
        self.image_agent = ImageGenerationAgent()
        
        self.logger = logging.getLogger(__name__)
        
        # Create the workflow graph
        self.workflow = self._create_workflow()
        
    def _create_workflow(self) -> StateGraph:
        """Create the LangGraph workflow"""
        
        def analyze_tone(state: Dict) -> Dict:
            """Analyze tone of voice"""
            # Ensure state has required fields
            if "errors" not in state:
                state["errors"] = []
            if "completed_steps" not in state:
                state["completed_steps"] = []
            if "current_step" not in state:
                state["current_step"] = ""
            if "status" not in state:
                state["status"] = ""
                
            state["current_step"] = "tone_analysis"
            state["status"] = "working"
            
            try:
                self.logger.info("Starting tone analysis")
                tone_result = self.tone_agent.analyze_tone(state["tone_sample"])
                state["tone_analysis"] = tone_result
                
                if "error" not in tone_result:
                    state["completed_steps"].append("tone_analysis")
                else:
                    state["errors"].append(f"Tone analysis error: {tone_result['error']}")
                    
            except Exception as e:
                error_msg = f"Tone analysis failed: {str(e)}"
                self.logger.error(error_msg)
                state["errors"].append(error_msg)
            
            return state
        
        def research_topic(state: Dict) -> Dict:
            """Research the topic"""
            # Ensure state has required fields
            if "errors" not in state:
                state["errors"] = []
            if "completed_steps" not in state:
                state["completed_steps"] = []
                
            state["current_step"] = "research"
            state["status"] = "working"
            
            try:
                self.logger.info("Starting topic research")
                research_result = self.research_agent.research_topic(state["topic"])
                state["research_data"] = research_result
                
                if "error" not in research_result:
                    state["completed_steps"].append("research")
                else:
                    state["errors"].append(f"Research error: {research_result['error']}")
                    
            except Exception as e:
                error_msg = f"Research failed: {str(e)}"
                self.logger.error(error_msg)
                state["errors"].append(error_msg)
            
            return state
        
        def create_content(state: Dict) -> Dict:
            """Create content based on tone and research"""
            # Ensure state has required fields
            if "errors" not in state:
                state["errors"] = []
            if "completed_steps" not in state:
                state["completed_steps"] = []
                
            state["current_step"] = "content_creation"
            state["status"] = "working"
            
            try:
                self.logger.info("Starting content creation")
                content_result = self.content_agent.create_content(
                    state.get("tone_analysis", {}),
                    state.get("research_data", {}),
                    state["topic"]
                )
                state["content_result"] = content_result
                
                if "error" not in content_result:
                    state["completed_steps"].append("content_creation")
                else:
                    state["errors"].append(f"Content creation error: {content_result['error']}")
                    
            except Exception as e:
                error_msg = f"Content creation failed: {str(e)}"
                self.logger.error(error_msg)
                state["errors"].append(error_msg)
            
            return state
        
        def generate_image(state: Dict) -> Dict:
            """Generate image for the post"""
            # Ensure state has required fields
            if "errors" not in state:
                state["errors"] = []
            if "completed_steps" not in state:
                state["completed_steps"] = []
                
            state["current_step"] = "image_generation"
            state["status"] = "working"
            
            try:
                self.logger.info("Starting image generation")
                
                # Get post content for image generation
                post_content = ""
                content_result = state.get("content_result")
                if content_result and "post_content" in content_result:
                    post_content = content_result["post_content"]
                
                image_result = self.image_agent.generate_image(post_content, state["topic"])
                state["image_result"] = image_result
                
                if "error" not in image_result:
                    state["completed_steps"].append("image_generation")
                else:
                    state["errors"].append(f"Image generation error: {image_result['error']}")
                    
            except Exception as e:
                error_msg = f"Image generation failed: {str(e)}"
                self.logger.error(error_msg)
                state["errors"].append(error_msg)
            
            return state
        
        def finalize_workflow(state: Dict) -> Dict:
            """Finalize the workflow"""
            # Ensure state has required fields
            if "errors" not in state:
                state["errors"] = []
            if "completed_steps" not in state:
                state["completed_steps"] = []
                
            state["current_step"] = "completed"
            
            # Update final status based on completion and errors
            error_count = len(state.get("errors", []))
            completed_count = len(state.get("completed_steps", []))
            
            if error_count == 0 and completed_count == 4:
                state["status"] = "completed"
            elif completed_count > 0:
                state["status"] = "partially_completed"
            else:
                state["status"] = "failed"
                
            self.logger.info(f"Workflow completed with status: {state['status']}")
            return state
        
        # Create the workflow graph
        workflow = StateGraph(WorkflowState)
        
        # Add nodes
        workflow.add_node("analyze_tone", analyze_tone)
        workflow.add_node("research_topic", research_topic)
        workflow.add_node("create_content", create_content)
        workflow.add_node("generate_image", generate_image)
        workflow.add_node("finalize", finalize_workflow)
        
        # Set entry point
        workflow.set_entry_point("analyze_tone")
        
        # Add edges (workflow sequence)
        workflow.add_edge("analyze_tone", "research_topic")
        workflow.add_edge("research_topic", "create_content")
        workflow.add_edge("create_content", "generate_image")
        workflow.add_edge("generate_image", "finalize")
        workflow.add_edge("finalize", END)
        
        return workflow.compile()
    
    def run_workflow(self, tone_sample: str, topic: str, language: str = "en", progress_callback=None) -> Dict:
        """
        Run the complete workflow
        
        Args:
            tone_sample (str): User's tone example
            topic (str): Content topic
            language (str): Content language (en/es)
            progress_callback: Optional callback function for progress updates
            
        Returns:
            Dict: Final state with all results
        """
        try:
            self.logger.info(f"Starting workflow for topic: {topic} in {language}")
            
            # Validate inputs
            if not tone_sample or len(tone_sample.strip()) < 10:
                raise ValueError("Tone sample must be at least 10 characters long")
            if not topic or len(topic.strip()) < 3:
                raise ValueError("Topic must be at least 3 characters long")
            
            # Initialize state with required fields
            initial_state = {
                "tone_sample": tone_sample.strip(),
                "topic": topic.strip(),
                "language": language,
                "tone_analysis": {},
                "research_data": {},
                "content_result": {},
                "image_result": {},
                "current_step": "start",
                "completed_steps": [],
                "errors": [],
                "status": "starting"
            }
            
            # Run the workflow
            final_state = self.workflow.invoke(initial_state)
            
            self.logger.info(f"Workflow completed with status: {final_state.get('status', 'unknown')}")
            return final_state
            
        except Exception as e:
            error_msg = f"Workflow execution failed: {str(e)}"
            self.logger.error(error_msg)
            
            # Return error state with all required fields
            return {
                "tone_sample": tone_sample,
                "topic": topic,
                "language": language,
                "tone_analysis": {},
                "research_data": {},
                "content_result": {},
                "image_result": {},
                "current_step": "error",
                "completed_steps": [],
                "errors": [error_msg],
                "status": "error"
            }
    
    def get_workflow_status(self, state: Dict) -> Dict[str, str]:
        """Get status of all workflow steps"""
        steps = {
            "tone_analysis": "waiting",
            "research": "waiting",
            "content_creation": "waiting",
            "image_generation": "waiting"
        }
        
        # Update based on completed steps
        for step in state.get("completed_steps", []):
            if step in steps:
                steps[step] = "completed"
        
        # Update current step
        current_step = state.get("current_step", "")
        if current_step in steps and steps[current_step] != "completed":
            steps[current_step] = "working"
        
        # Update error steps
        for error in state.get("errors", []):
            for step in steps:
                if step in error.lower():
                    steps[step] = "error"
                    break
        
        return steps
    
    def get_results_summary(self, state: Dict) -> Dict[str, Any]:
        """Get a summary of all results"""
        summary = {
            "status": state.get("status", "unknown"),
            "completed_steps": len(state.get("completed_steps", [])),
            "total_steps": 4,
            "errors": state.get("errors", []),
            "results": {}
        }
        
        # Add individual results
        tone_analysis = state.get("tone_analysis")
        if tone_analysis:
            summary["results"]["tone_analysis"] = self.tone_agent.get_tone_summary(tone_analysis)
        
        research_data = state.get("research_data")
        if research_data:
            summary["results"]["research"] = self.research_agent.get_research_summary(research_data)
        
        content_result = state.get("content_result")
        if content_result:
            summary["results"]["content"] = self.content_agent.get_content_summary(content_result)
        
        image_result = state.get("image_result")
        if image_result:
            summary["results"]["image"] = self.image_agent.get_image_summary(image_result)
        
        return summary 