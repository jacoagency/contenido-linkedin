import streamlit as st
import time
from typing import Dict, Any

def create_agent_status_card(agent_name: str, status: str, message: str):
    """Create a status card for an agent"""
    status_icons = {
        "waiting": "⏳",
        "working": "🔄",
        "completed": "✅",
        "error": "❌"
    }
    
    icon = status_icons.get(status, "⏳")
    st.info(f"{icon} {agent_name.replace('_', ' ').title()}: {message}")

def create_progress_dashboard(agent_statuses: Dict[str, str]):
    """Create a progress dashboard showing all agents"""
    st.subheader("🚀 Agent Progress Dashboard")
    
    col1, col2 = st.columns(2)
    
    with col1:
        for i, (agent, status) in enumerate(list(agent_statuses.items())[:3]):
            create_agent_status_card(agent, status, get_status_message(agent, status))
    
    with col2:
        for agent, status in list(agent_statuses.items())[3:]:
            create_agent_status_card(agent, status, get_status_message(agent, status))

def create_input_section():
    """Create the user input section"""
    st.subheader("📝 Content Input")
    
    with st.container():
        col1, col2 = st.columns([2, 1])
        
        with col1:
            tone_sample = st.text_area(
                "Your Tone of Voice Example",
                placeholder="Paste a sample of your writing that represents your desired tone...",
                height=150,
                help="This should be text that represents how you want to sound on LinkedIn",
                label_visibility="visible"
            )
        
        with col2:
            topic = st.text_input(
                "Content Topic",
                placeholder="e.g., AI in marketing, Remote work trends...",
                help="The subject you want to create content about",
                label_visibility="visible"
            )
            
            st.write("")
            generate_button = st.button(
                "🚀 Generate Content",
                type="primary",
                use_container_width=True
            )
    
    return tone_sample, topic, generate_button

def create_output_section(post_content: str = None, image_url: str = None):
    """Create the output section for generated content"""
    st.subheader("📋 Generated Content")
    
    if post_content:
        st.write("LinkedIn Post:")
        st.write(post_content)
        
        col1, col2 = st.columns([1, 1])
        with col1:
            st.download_button(
                "💾 Save Post",
                data=post_content,
                file_name="linkedin_post.txt",
                mime="text/plain",
                use_container_width=True
            )
    
    if image_url:
        st.write("Generated Image:")
        st.image(image_url, use_column_width=True)
        st.markdown(f"[Download Image]({image_url})")

def show_completion_checklist(completed_tasks: list):
    """Show completion checklist"""
    st.subheader("✅ Completion Checklist")
    
    tasks = [
        ("Tone Analysis", "tone_analysis"),
        ("Topic Research", "research"),
        ("Content Creation", "content_creation"),
        ("Image Generation", "image_generation")
    ]
    
    for task_name, task_id in tasks:
        status = "✅" if task_id in completed_tasks else "⏳"
        st.write(f"{status} {task_name}")

def get_status_message(agent: str, status: str) -> str:
    """Get status message for an agent"""
    messages = {
        "tone_analysis": {
            "waiting": "Waiting to analyze your tone...",
            "working": "Analyzing your writing style...",
            "completed": "Tone analysis complete",
            "error": "Error analyzing tone"
        },
        "research": {
            "waiting": "Waiting to research topic...",
            "working": "Gathering insights...",
            "completed": "Research complete",
            "error": "Error during research"
        },
        "content_creation": {
            "waiting": "Waiting to create content...",
            "working": "Writing your post...",
            "completed": "Content creation complete",
            "error": "Error creating content"
        },
        "image_generation": {
            "waiting": "Waiting to generate image...",
            "working": "Creating image...",
            "completed": "Image generation complete",
            "error": "Error generating image"
        }
    }
    
    return messages.get(agent, {}).get(status, "Status unknown") 