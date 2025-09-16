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
git clone (https://github.com/phuhoangg/Docia)
cd docia-project
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
DOCIA_MODEL=google/gemini-2.0-flash-exp:free
DOCIA_VISION_MODEL=moonshotai/kimi-vl-a3b-thinking:free
DOCIA_STORAGE_PATH=./docia_data
```

The CLI will automatically load the `.env` file

## 🎯 Usage

### Quick Start

```bash
# Start Docia in interactive mode (default)
docia

# In interactive mode:
docia[14:30:25]> help
docia[14:30:26]> "What are the key findings in this report?"
docia[14:30:27]> tasks
docia[14:30:28]> exit
```

### Basic Commands

```bash
# Show help
docia --help

# Show system statistics
docia stats

# List all documents
docia list

# Add a document
docia add path/to/document.pdf

# Add with custom name
docia add path/to/report.pdf --name "Q3 Financial Report"

# Query documents
docia query "What were the Q3 revenue figures?"

# Search documents
docia search "financial report" --limit 5

# Remove a document
docia remove doc_123

# Start interactive shell explicitly
docia shell
```

### Interactive Mode Features

The interactive shell provides:
- Real-time task tracking from the planner
- Conversation history management
- Live progress updates
- Timestamped prompts
- Built-in commands for system management
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

## 📁 Project Structure

```
docia-project/
├── docia/              # Main Python package
│   ├── core/          # Configuration and utilities
│   ├── models/        # Data models
│   ├── processors/    # Document processing
│   ├── storage/       # Knowledge storage
│   ├── intelligence/   # AI orchestration
│   ├── integrations/  # AI provider integrations
│   └── utils/         # Utility functions
├── cli/               # CLI interface
│   ├── commands/      # CLI commands
│   ├── main.py        # Main CLI entry point
│   └── app.py         # CLI app configuration
├── docia/             # Package directory with .env file
├── setup.py           # Package setup
├── requirements.txt   # Dependencies
├── README.md          # This file
├── README_CLI.md      # Detailed CLI documentation
└── .gitignore         # Git ignore rules
```

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
- [Configuration Guide](docia/.env.example) - Environment configuration options, create a `.evn` base on `.evn.example`

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
