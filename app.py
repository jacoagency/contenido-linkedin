import streamlit as st
import logging
import time
from typing import Dict, Any
import traceback
import base64
from io import BytesIO
from PIL import Image
import requests
import pyperclip

# Import custom modules
from agents.supervisor import SupervisorAgent, WorkflowState
from utils.config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="LinkedIn Content Creator",
    page_icon="��",
    layout="wide"
)

def initialize_session_state():
    """Initialize session state variables"""
    if 'workflow_state' not in st.session_state:
        st.session_state.workflow_state = None
    if 'generation_in_progress' not in st.session_state:
        st.session_state.generation_in_progress = False
    if 'agent_statuses' not in st.session_state:
        st.session_state.agent_statuses = {
            "tone_analysis": "waiting",
            "research": "waiting",
            "content_creation": "waiting",
            "image_generation": "waiting"
        }
    if 'language' not in st.session_state:
        st.session_state.language = "en"  # Default to English
    if 'supervisor' not in st.session_state:
        st.session_state.supervisor = None

def validate_api_keys():
    """Validate required API keys"""
    try:
        config = Config()
        config.validate_keys()
        return True
    except ValueError as e:
        st.error(f"❌ Configuration Error: {e}")
        st.info("💡 Please set your API keys in the .env file:")
        st.code("""
OPENAI_API_KEY=your_openai_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
""")
        return False
    except Exception as e:
        st.error(f"❌ Unexpected error: {e}")
        return False

def create_header():
    """Create application header"""
    st.title("LinkedIn Content Creator")
    st.write(
        "Create engaging LinkedIn posts with AI-powered multi-agent workflow" 
        if st.session_state.language == "en" 
        else "Crea publicaciones atractivas para LinkedIn con flujo de trabajo multi-agente impulsado por IA"
    )

def create_input_section():
    """Create the input section"""
    st.subheader("📝 Content Input")
    
    # Language selector
    language = st.selectbox(
        "🌐 Language / Idioma",
        options=["en", "es"],
        format_func=lambda x: "English" if x == "en" else "Español",
        index=0 if st.session_state.language == "en" else 1,
        key="language_selector"
    )
    st.session_state.language = language
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        tone_sample = st.text_area(
            "Your Tone of Voice Example" if language == "en" else "Ejemplo de tu Tono de Voz",
            placeholder=("Paste a sample of your writing that represents your desired tone..." if language == "en" 
                       else "Pega un ejemplo de tu escritura que represente el tono deseado..."),
            height=150,
            help=("This should be text that represents how you want to sound on LinkedIn" if language == "en"
                 else "Este debe ser un texto que represente cómo quieres sonar en LinkedIn")
        )
    
    with col2:
        topic = st.text_input(
            "Content Topic" if language == "en" else "Tema del Contenido",
            placeholder=("e.g., AI in marketing, Remote work trends..." if language == "en"
                       else "ej., IA en marketing, Tendencias de trabajo remoto..."),
            help=("The subject you want to create content about" if language == "en"
                 else "El tema sobre el que quieres crear contenido")
        )
        
        include_image = st.checkbox(
            "Include Image" if language == "en" else "Incluir Imagen", 
            value=True
        )
        include_hashtags = st.checkbox(
            "Include Hashtags" if language == "en" else "Incluir Hashtags", 
            value=True
        )
        
        st.write("")  # Add some spacing
        generate_button = st.button(
            "🚀 " + ("Generate Content" if language == "en" else "Generar Contenido"),
            type="primary",
            use_container_width=True
        )
    
    return tone_sample, topic, include_image, include_hashtags, generate_button

def create_progress_dashboard():
    """Create progress dashboard"""
    st.subheader("🚀 Agent Progress")
    
    agents = [
        ("tone_analysis", "🎯", "Tone Analysis", "Analyzing your writing style"),
        ("research", "🔍", "Research", "Gathering topic insights"),
        ("content_creation", "✍️", "Content Creation", "Writing your post"),
        ("image_generation", "🖼️", "Image Generation", "Creating visuals")
    ]
    
    cols = st.columns(2)
    for idx, (agent_id, icon, name, description) in enumerate(agents):
        status = st.session_state.agent_statuses.get(agent_id, "waiting")
        with cols[idx % 2]:
            st.info(f"{icon} {name}: {description}")

def create_output_section(post_content: str = None, image_url: str = None):
    """Create the output section"""
    st.subheader("📋 " + ("Generated Content" if st.session_state.language == "en" else "Contenido Generado"))
    
    if post_content:
        st.write("LinkedIn Post:" if st.session_state.language == "en" else "Publicación de LinkedIn:")
        st.write(post_content)
        
        col1, col2 = st.columns([1, 1])
        with col1:
            st.download_button(
                "💾 " + ("Download Post" if st.session_state.language == "en" else "Descargar Publicación"),
                data=post_content,
                file_name="linkedin_post.txt",
                mime="text/plain",
                use_container_width=True
            )
        with col2:
            copy_button = st.button(
                "📋 " + ("Copy to Clipboard" if st.session_state.language == "en" else "Copiar al Portapapeles"),
                use_container_width=True
            )
            if copy_button:
                pyperclip.copy(post_content)
                st.success(
                    "✅ Copied to clipboard!" if st.session_state.language == "en" else "✅ ¡Copiado al portapapeles!"
                )
    
    if image_url:
        st.write("Generated Image:" if st.session_state.language == "en" else "Imagen Generada:")
        st.image(image_url, use_container_width=True)
        st.markdown(
            f"[{('Download Image' if st.session_state.language == 'en' else 'Descargar Imagen')}]({image_url})"
        )

def run_workflow_with_real_time_progress(tone_sample: str, topic: str):
    """Run workflow with real-time progress updates"""
    try:
        # Initialize supervisor
        if st.session_state.supervisor is None:
            with st.spinner("🔧 Initializing AI agents..."):
                st.session_state.supervisor = SupervisorAgent()
        
        supervisor = st.session_state.supervisor
        
        # Create progress container
        progress_placeholder = st.empty()
        
        # Show initial progress
        with progress_placeholder.container():
            create_progress_dashboard()
        
        # Simulate step-by-step progress and run workflow
        steps = ["tone_analysis", "research", "content_creation", "image_generation"]
        
        # Start workflow in background
        with st.spinner("🎯 Running AI workflow..."):
            workflow_result = supervisor.run_workflow(
                tone_sample, 
                topic,
                language=st.session_state.language  # Pass the language parameter
            )
            
            # Update progress based on results
            if workflow_result:
                completed_steps = workflow_result.get("completed_steps", [])
                errors = workflow_result.get("errors", [])
                
                for step in steps:
                    if step in completed_steps:
                        st.session_state.agent_statuses[step] = "completed"
                    elif any(step in error.lower() for error in errors):
                        st.session_state.agent_statuses[step] = "error"
                
                # Final progress update
                with progress_placeholder.container():
                    create_progress_dashboard()
        
        return workflow_result
        
    except Exception as e:
        error_msg = f"Workflow execution failed: {str(e)}"
        logger.error(f"{error_msg}\n{traceback.format_exc()}")
        st.error(f"❌ {error_msg}")
        return None

def main():
    """Main application function"""
    initialize_session_state()
    
    # Validate API keys
    if not validate_api_keys():
        st.stop()
    
    # Create header
    create_header()
    
    # Create input section
    tone_sample, topic, include_image, include_hashtags, generate_button = create_input_section()
    
    # Show progress dashboard if there's activity
    if st.session_state.workflow_state:
        create_progress_dashboard()
    
    # Handle generate button click
    if generate_button:
        if not tone_sample or len(tone_sample.strip()) < 10:
            st.error(
                "⚠️ Please provide a tone sample of at least 10 characters."
                if st.session_state.language == "en"
                else "⚠️ Por favor proporciona un ejemplo de tono de al menos 10 caracteres."
            )
        elif not topic or len(topic.strip()) < 3:
            st.error(
                "⚠️ Please provide a topic of at least 3 characters."
                if st.session_state.language == "en"
                else "⚠️ Por favor proporciona un tema de al menos 3 caracteres."
            )
        else:
            # Reset statuses
            for agent in st.session_state.agent_statuses:
                st.session_state.agent_statuses[agent] = "waiting"
            
            # Run workflow
            workflow_result = run_workflow_with_real_time_progress(tone_sample, topic)
            
            if workflow_result:
                # Show results
                content_result = workflow_result.get("content_result", {})
                image_result = workflow_result.get("image_result", {})
                
                if content_result:
                    create_output_section(
                        content_result.get("post_content"),
                        image_result.get("image_url") if include_image else None
                    )
                
                # Show completion message
                status = workflow_result.get("status", "unknown")
                if status == "completed":
                    st.success(
                        "🎉 Content generation completed successfully!"
                        if st.session_state.language == "en"
                        else "🎉 ¡La generación de contenido se completó exitosamente!"
                    )
                elif status == "partially_completed":
                    st.warning(
                        "⚠️ Content generation partially completed. Some steps had errors."
                        if st.session_state.language == "en"
                        else "⚠️ La generación de contenido se completó parcialmente. Algunos pasos tuvieron errores."
                    )
                else:
                    st.error(
                        "❌ Content generation failed."
                        if st.session_state.language == "en"
                        else "❌ La generación de contenido falló."
                    )
                
                # Show errors if any
                errors = workflow_result.get("errors", [])
                if errors:
                    with st.expander(
                        "⚠️ View Errors" if st.session_state.language == "en" else "⚠️ Ver Errores"
                    ):
                        for error in errors:
                            st.error(error)

if __name__ == "__main__":
    main() 