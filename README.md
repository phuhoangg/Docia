# Docia - VisionLM Document Intelligence

A powerful command-line interface for intelligent document analysis using Vision Language Models.

## 🚀 Features

- **Vision Intelligence**: Analyze documents as images using advanced Vision AI
- **Adaptive Planning**: Dynamic task planning and execution for complex queries
- **Multiple Formats**: Support for PDFs, JPG, PNG, WebP, BMP, TIFF
- **Conversation Mode**: Context-aware follow-up questions and memory
- **Progress Tracking**: Real-time analysis progress with detailed feedback
- **Cost Monitoring**: Track API usage and costs for optimization
- **Multiple Providers**: Support for OpenAI and OpenRouter

## 📦 Installation

### From Source

```bash
git clone https://github.com/phuhoangg/Docia
cd docia
pip install -e .
```

### Requirements

- Python 3.8+
- API key for OpenAI or OpenRouter

## ⚙️ Configuration

Docia uses a `.env` file for configuration. Copy and configure:

```bash
# Example .env file
DOCIA_PROVIDER=openrouter
OPENROUTER_API_KEY=your-openrouter-api-key
DOCIA_MODEL=google/gemini-2.5-flash
DOCIA_VISION_MODEL=google/gemini-2.5-flash
DOCIA_STORAGE_PATH=./docia_data
```

The CLI will automatically load the `.env` file

## 🎯 Usage

### Quick Start

```bash
# Start Docia in interactive mode (default)
docia

# The interactive shell will start in ADD MODE
# You can add documents by entering file paths or dragging files
# After adding documents, you'll automatically switch to QUERY MODE
# In QUERY MODE, you can ask questions directly by typing them

# Example workflow in interactive mode:
# [ADD] Docia > C:\Documents\report.pdf
# [QUERY] Docia > What is this document about?
```

### Interactive Shell Features

The interactive shell provides:
- **Two intuitive modes**: ADD MODE for adding documents, QUERY MODE for asking questions
- **Direct input**: No need for command prefixes - just type file paths or questions
- **Real-time task tracking**: See what Docia is working on
- **Built-in commands**: Use `/` to see available commands
- **Automatic mode switching**: Seamlessly transitions between adding and querying

### Basic Commands

```bash
# Add a document
docia add path/to/document.pdf

# Start interactive shell
docia

# Show help in interactive shell
/                 # Show command menu
/add              # Switch to add document mode
/query            # Switch to query mode
/list             # List all documents
/clear            # Clear conversation history
/exit             # Exit the shell

# Show system statistics
docia stats

# List all documents
docia list

# Add with custom name
docia add path/to/report.pdf --name "Q3 Financial Report"

# Query documents
docia query "What were the Q3 revenue figures?"

# Search documents
docia search "financial report" --limit 5

# Remove a document
docia remove doc_123
```

### Advanced Query Options

```bash
# Query with specific provider
docia query "Analyze the data" --provider openai

# Query with custom API key
docia query "What are the findings?" --api-key "your-key"

# Limit analysis scope
docia query "Extract key metrics" --max-pages 5

# Conversation mode (follow-up questions)
docia query "Tell me more about that" --conversation
```

### Configuration Management

```bash
# Show current configuration
docia config show

# Set configuration values
docia config set --provider openai
docia config set --storage-path ./my_documents
```

## 📊 Progress Tracking

The CLI provides real-time progress tracking for complex queries:

```bash
$ docia query "Analyze the financial trends and growth patterns"
🚀 Docia initialized successfully!
🔍 Querying: Analyze the financial trends and growth patterns

📋 Created analysis plan with 2 tasks
   1. Extract Financial Data (table)
   2. Analyze Growth Trends (chart)

🔍 Starting: Extract Financial Data
📄 Selected pages: [3, 4, 5, 8]
✅ Completed: Extract Financial Data (4 pages)

🔍 Starting: Analyze Growth Trends
📄 Selected pages: [6, 7, 10]
✅ Completed: Analyze Growth Trends (3 pages)

🎯 Analysis Results:
==================================================
Based on the analysis of Q3 financial data and growth charts...

📊 Query Information:
   Processing time: 12.34 seconds
   Pages analyzed: 7
   Tasks completed: 2
   Total iterations: 1
   Cost: $0.0234
```

## 📚 Interactive Shell Usage

### Modes

The interactive shell has two modes:

1. **ADD MODE** - For adding documents
   - Enter file paths directly or drag and drop files
   - Example: `C:\Documents\report.pdf`

2. **QUERY MODE** - For asking questions about documents
   - Type questions directly
   - Example: `What is the main topic of this document?`

### Adding Documents

In ADD MODE, you can add documents by:
1. Typing the full path to a PDF or image file
2. Dragging and dropping files onto the terminal window

Example:
```
[ADD] Docia > C:\Users\Documents\financial_report.pdf
```

After adding documents, you'll automatically switch to QUERY MODE.

### Querying Documents

In QUERY MODE, ask questions directly:

Example:
```
[QUERY] Docia > What are the key findings in this report?
```

The shell will analyze your documents and provide intelligent responses.

### Task Tracking

The interactive shell displays real-time task progress:
- Current tasks are shown at the top of the screen
- Task status is updated as processing occurs
- You can ask questions while tasks are running

## 🔧 API Keys Setup

### OpenAI
1. Visit [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create a new API key
3. Set in your `.env` file:
   ```bash
   DOCIA_PROVIDER=openai
   OPENAI_API_KEY=your-openai-api-key
   ```

### OpenRouter
1. Visit [OpenRouter](https://openrouter.ai/keys)
2. Create a new API key
3. Set in your `.env` file:
   ```bash
   DOCIA_PROVIDER=openrouter
   OPENROUTER_API_KEY=your-openrouter-api-key
   ```

## 📚 Documentation

- [CLI Documentation](README_CLI.md) - Detailed CLI usage and examples
- [Configuration Guide](docia/.env.example) - Environment configuration options, create a `.env` base on `.env.example`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🔮 Roadmap

- [ ] Web interface
- [ ] Document batch processing
- [ ] Advanced export formats
- [ ] Plugin system
- [ ] Team collaboration features
- [ ] Advanced analytics dashboard