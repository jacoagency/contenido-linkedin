# LinkedIn Content Creator - Multi-Agent Orchestrator

## Project Overview
A Python Streamlit application that uses LangChain and LangGraph to orchestrate multiple AI agents for creating LinkedIn content. The system takes user input (tone of voice example and topic) and generates both text posts and images for LinkedIn.

## Architecture
- **Frontend**: Streamlit web interface
- **Backend**: LangChain + LangGraph multi-agent system
- **Agents**: Specialized AI agents for different content creation tasks
- **APIs**: Tavily Search API, OpenAI API

## Agent Architecture

### 1. Tone Analysis Agent
- **Purpose**: Analyze user's tone of voice example
- **Input**: User's tone sample text
- **Output**: Tone profile and style guidelines
- **Tools**: LangChain text analysis

### 2. Research Agent
- **Purpose**: Search for relevant information about the topic
- **Input**: Topic/subject from user
- **Output**: Curated research data and insights
- **Tools**: Tavily Search API via LangChain Community

### 3. Content Creation Agent
- **Purpose**: Generate LinkedIn post content
- **Input**: Tone profile + research data
- **Output**: Formatted LinkedIn post text
- **Tools**: LangChain text generation

### 4. Image Generation Agent
- **Purpose**: Create visual content for the post
- **Input**: Post content summary
- **Output**: LinkedIn-optimized image
- **Tools**: OpenAI DALL-E API

### 5. Supervisor Agent
- **Purpose**: Orchestrate all agents and manage workflow
- **Input**: User request
- **Output**: Coordinated execution plan
- **Tools**: LangGraph workflow management

## Technical Stack
- **Framework**: Streamlit
- **AI Orchestration**: LangGraph
- **AI Framework**: LangChain
- **Search API**: Tavily Search (via langchain-community)
- **Image Generation**: OpenAI DALL-E
- **Language Model**: OpenAI GPT
- **UI Components**: Streamlit native components

## User Interface Requirements

### Input Section
- Text area for tone of voice example
- Input field for content topic/subject
- Generate button to start the process

### Progress Visualization
- Real-time agent status indicators
- Visual workflow progression
- Agent activity animations
- Progress bars for each stage

### Output Section
- Generated LinkedIn post preview
- Generated image display
- Copy-to-clipboard functionality
- Download options

### Design Requirements
- Elegant and modern UI design
- Responsive layout
- Clear visual hierarchy
- Professional color scheme
- Smooth transitions and animations

## Workflow Process

1. **User Input Phase**
   - User provides tone example
   - User specifies content topic
   - System validates inputs

2. **Agent Orchestration Phase**
   - Supervisor agent creates execution plan
   - Tone analysis agent processes voice sample
   - Research agent gathers topic information
   - Content agent generates post
   - Image agent creates visual content

3. **Output Phase**
   - Display generated content
   - Show completion checklist
   - Provide download/copy options

## File Structure
```
linkedin2/
   app.py                 # Main Streamlit application
   agents/
      __init__.py
      tone_agent.py      # Tone analysis agent
      research_agent.py  # Tavily search agent
      content_agent.py   # Content creation agent
      image_agent.py     # Image generation agent
      supervisor.py      # Supervisor agent
   utils/
      __init__.py
      config.py          # API keys and configuration
      prompts.py         # Agent prompts and templates
      ui_components.py   # Custom Streamlit components
   styles/
      main.css           # Custom CSS styles
   requirements.txt       # Python dependencies
   .env                   # Environment variables
```

## Dependencies
- streamlit
- langchain
- langchain-community
- langgraph
- openai
- tavily-python
- python-dotenv
- pandas
- pillow

## Environment Variables
- `OPENAI_API_KEY`
- `TAVILY_API_KEY`
- `LANGCHAIN_API_KEY` (optional for tracing)

## Features to Implement

### Core Features
- Multi-agent workflow orchestration
- Real-time progress visualization
- Tone of voice analysis
- Content research and generation
- Image creation
- LinkedIn post formatting

### UI/UX Features
- Agent status indicators with colors
- Progress animations
- Completion checklist
- Copy-to-clipboard functionality
- Download options
- Error handling and user feedback

### Advanced Features
- Content preview and editing
- Multiple post variations
- Scheduling integration
- Content history
- Template management