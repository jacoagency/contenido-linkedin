# 🚀 LinkedIn Content Creator - Multi-Agent Orchestrator

A sophisticated Python Streamlit application that uses LangChain and LangGraph to orchestrate multiple AI agents for creating compelling LinkedIn content. The system takes your tone of voice example and topic, then generates both text posts and supporting images tailored to your style.

## ✨ Features

### 🤖 Multi-Agent Architecture
- **Tone Analysis Agent**: Analyzes your writing style and voice characteristics
- **Research Agent**: Searches for relevant information using Tavily Search API
- **Content Creation Agent**: Generates LinkedIn posts matching your tone
- **Image Generation Agent**: Creates professional visuals using DALL-E
- **Supervisor Agent**: Orchestrates the entire workflow using LangGraph

### 🎨 Modern UI/UX
- Real-time progress visualization with animated status cards
- Professional gradient design and smooth animations
- Responsive layout that works on all devices
- Interactive progress dashboard with agent status indicators
- Copy-to-clipboard and download functionality

### 🔧 Advanced Features
- LinkedIn-optimized content formatting
- Hashtag extraction and suggestion
- Call-to-action identification
- Error handling with graceful degradation
- Session state management
- Comprehensive logging and debugging

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- OpenAI API key
- Tavily Search API key

### Setup Instructions

1. **Clone the repository** (or use the created files):
```bash
git clone <repository-url>
cd linkedin2
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Configure API keys**:
   - Copy the `.env` file and add your API keys:
```bash
# API Keys - Replace with your actual API keys
OPENAI_API_KEY=your_openai_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
LANGCHAIN_API_KEY=your_langchain_api_key_here

# Optional settings
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=linkedin-content-creator
```

4. **Get API Keys**:
   - **OpenAI**: Visit [OpenAI Platform](https://platform.openai.com/api-keys)
   - **Tavily**: Visit [Tavily](https://tavily.com/) to get your search API key
   - **LangChain** (optional): Visit [LangSmith](https://smith.langchain.com/) for tracing

5. **Run the application**:
```bash
streamlit run app.py
```

## 📚 Usage

### Getting Started
1. Launch the application with `streamlit run app.py`
2. Enter your tone of voice example (minimum 10 characters)
3. Specify your content topic (minimum 3 characters)
4. Click "🚀 Generate Content" to start the multi-agent workflow

### Tone of Voice Examples
Provide a sample of your writing that represents how you want to sound on LinkedIn:

**Professional Tone Example:**
```
"I believe in the power of data-driven decision making. In my experience leading teams, I've found that combining analytical insights with human intuition creates the most impactful results. What strategies have worked best for your organization?"
```

**Casual Tone Example:**
```
"Just had an amazing coffee chat with a fellow entrepreneur! 🚀 We discussed the challenges of scaling a startup, and it reminded me why I love this community. The support and shared knowledge is incredible. What's the best advice you've received lately?"
```

### Content Topics
Examples of effective topics:
- "AI in marketing automation"
- "Remote work productivity tips"
- "Leadership during economic uncertainty"
- "Sustainable business practices"
- "Career transition strategies"

## 🏗️ Architecture

### File Structure
```
linkedin2/
├── app.py                 # Main Streamlit application
├── agents/
│   ├── __init__.py
│   ├── tone_agent.py      # Tone analysis agent
│   ├── research_agent.py  # Tavily search agent
│   ├── content_agent.py   # Content creation agent
│   ├── image_agent.py     # Image generation agent
│   └── supervisor.py      # Supervisor agent
├── utils/
│   ├── __init__.py
│   ├── config.py          # API keys and configuration
│   ├── prompts.py         # Agent prompts and templates
│   └── ui_components.py   # Custom Streamlit components
├── styles/
│   └── main.css           # Custom CSS styles
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables
└── README.md             # This file
```

### Workflow Process
1. **Input Validation**: Validates tone sample and topic
2. **Tone Analysis**: Analyzes writing style and characteristics
3. **Topic Research**: Searches for relevant information and insights
4. **Content Creation**: Generates LinkedIn post based on tone and research
5. **Image Generation**: Creates supporting visual content
6. **Output Display**: Presents results with download/copy options

## 🔧 Configuration

### Environment Variables
- `OPENAI_API_KEY`: Required for content and image generation
- `TAVILY_API_KEY`: Required for topic research
- `LANGCHAIN_API_KEY`: Optional for workflow tracing
- `LANGCHAIN_TRACING_V2`: Enable LangChain tracing (true/false)
- `LANGCHAIN_PROJECT`: Project name for tracing

### Model Configuration
Default models can be changed in `utils/config.py`:
- **OpenAI Model**: `gpt-4-turbo-preview`
- **DALL-E Model**: `dall-e-3`
- **Tavily Results**: 5 search results

## 🚨 Troubleshooting

### Common Issues

1. **Missing API Keys**:
   - Ensure all required API keys are in your `.env` file
   - Check that the `.env` file is in the project root directory

2. **Import Errors**:
   - Verify all dependencies are installed: `pip install -r requirements.txt`
   - Check Python version compatibility (3.8+)

3. **Streamlit Issues**:
   - Clear Streamlit cache: `streamlit cache clear`
   - Restart the application

4. **API Rate Limits**:
   - OpenAI and Tavily have rate limits
   - Wait a few minutes between requests if you hit limits

### Logging
Logs are displayed in the terminal where you run the application. Set logging level in `app.py` if needed.

## 🎨 Customization

### Adding New Agents
1. Create a new agent file in the `agents/` directory
2. Implement the agent class with required methods
3. Add the agent to the supervisor workflow in `agents/supervisor.py`
4. Update the UI components to display the new agent's status

### Modifying Prompts
Edit prompts in `utils/prompts.py` to customize agent behavior:
- Tone analysis prompts
- Research prompts
- Content creation prompts
- Image generation prompts

### Styling
Customize the UI by editing:
- `utils/ui_components.py`: Streamlit components
- `styles/main.css`: CSS styles and animations

## 📈 Performance Tips

1. **API Optimization**:
   - Use appropriate temperature settings for different agents
   - Implement caching for repeated requests
   - Consider using streaming for real-time updates

2. **UI Performance**:
   - Use session state effectively
   - Implement progressive loading for large content
   - Optimize image loading and display

## 🔒 Security Notes

- Never commit API keys to version control
- Use environment variables for all sensitive configuration
- Implement proper error handling to avoid exposing internal details
- Consider rate limiting for production deployments

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **LangChain**: For the powerful AI framework
- **LangGraph**: For workflow orchestration
- **Streamlit**: For the excellent web framework
- **OpenAI**: For GPT and DALL-E APIs
- **Tavily**: For search capabilities

## 📞 Support

If you encounter any issues or have questions:
1. Check the troubleshooting section above
2. Review the logs in your terminal
3. Ensure all API keys are correctly configured
4. Verify your Python and package versions

---

**Built with ❤️ using Python, Streamlit, LangChain, and LangGraph** 