# Docia CLI - VisionLM Document Intelligence Tool

A powerful command-line interface for intelligent document analysis using Vision Language Models.

## 🚀 Installation

### From Source
```bash
git clone https://github.com/phuhoangg/docia.git
cd docia
pip install -e .
```

### Requirements
- Python 3.8+
- API key for OpenAI or OpenRouter

## 🔧 Configuration

### Environment Variables
```bash
# Required: AI Provider API Key
export OPENAI_API_KEY="your-openai-api-key"
# or
export OPENROUTER_API_KEY="your-openrouter-api-key"

# Optional: Configuration
export DOCA_STORAGE_PATH="./docia_data"
export DOCA_LOG_LEVEL="INFO"
```

### Configuration File
```bash
# Show current configuration
docia config show

# Set configuration values
docia config set --provider openai
docia config set --storage-path ./my_documents
docia config set --max-iterations 5
```

## 📚 Usage

### Adding Documents
```bash
# Add a PDF document
docia add path/to/document.pdf

# Add with custom name
docia add path/to/report.pdf --name "Q3 Financial Report"

# Add with custom ID
docia add path/to/manual.pdf --id "user_manual_2024"
```

### Listing Documents
```bash
# List all documents
docia list

# Search documents
docia search "financial report" --limit 5
```

### Querying Documents
```bash
# Basic query
docia query "What were the Q3 revenue figures?"

# Query specific documents
docia query "What is the authentication process?" -d doc_1 -d doc_2

# Query with different modes
docia query "Summarize the key findings" --mode comprehensive

# Query with page limit
docia query "Extract all table data" --max-pages 10

# Conversation mode (follow-up questions)
docia query "Tell me more about that" --conversation
```

### Advanced Query Options
```bash
# Fast mode (quicker, less comprehensive)
docia query "What is the main topic?" --mode fast

# Comprehensive mode (more thorough analysis)
docia query "Analyze all financial data" --mode comprehensive

# Limit analysis to specific pages
docia query "What are the key metrics?" --max-pages 5
```

### Document Management
```bash
# Remove a document
docia remove doc_123

# Clear conversation history
docia clear

# Show system statistics
docia stats
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

## 🗂️ File Structure

After running Docia, your data will be organized as:

```
docia_data/
├── documents/
│   ├── doc_123/
│   │   ├── metadata.json
│   │   ├── pages/
│   │   │   ├── page_1.jpg
│   │   │   ├── page_2.jpg
│   │   │   └── ...
│   │   ├── summary.txt
│   │   └── thumbnail.jpg
│   └── doc_456/
│       └── ...
├── conversations/
└── logs/
```

## 💡 Tips

### 1. **Optimize Queries**
- Be specific about what you want to find
- Use conversation mode for follow-up questions
- Limit page count for faster results

### 2. **Document Management**
- Use descriptive names when adding documents
- Regularly clean up unused documents
- Monitor storage usage with `docia stats`

### 3. **Cost Management**
- Use `--mode fast` for simple queries
- Set `--max-pages` to limit analysis scope
- Monitor costs in query results

### 4. **Batch Operations**
```bash
# Add multiple documents
for file in reports/*.pdf; do
    docia add "$file"
done

# Query multiple documents
docia query "Compare performance across all documents"
```

## 🐛 Troubleshooting

### Common Issues

**API Key Not Found**
```bash
# Set your API key
export OPENAI_API_KEY="your-key-here"
```

**Document Processing Failed**
```bash
# Check supported formats
docia stats

# Ensure file is not corrupted
file your-document.pdf
```

**Memory Issues**
```bash
# Limit analysis scope
docia query "Your question" --max-pages 3 --mode fast
```

**Configuration Issues**
```bash
# Reset to defaults
rm ~/.docia/config.json
docia config set --provider openai
```

## 📈 Examples

### Financial Analysis
```bash
docia add financial_report.pdf
docia query "What were the Q3 revenue and profit margins?"
docia query "How does this compare to previous quarters?" --conversation
```

### Technical Documentation
```bash
docia add api_documentation.pdf
docia query "How do I implement user authentication?"
docia query "What are the security requirements?" --conversation
```

### Research Analysis
```bash
docia add research_paper.pdf
docia query "What are the main findings of this study?"
docia query "What methodology was used?" --conversation
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🚀 Features

- ✅ **Vision Intelligence**: Analyze documents as images
- ✅ **Adaptive Planning**: Dynamic task planning and execution
- ✅ **Multiple Formats**: Support for PDFs and images
- ✅ **Conversation Mode**: Context-aware follow-up questions
- ✅ **Progress Tracking**: Real-time analysis progress
- ✅ **Cost Monitoring**: Track API usage and costs
- ✅ **Configuration Management**: Flexible configuration options
- ✅ **Batch Operations**: Process multiple documents efficiently

## 🔮 Roadmap

- [ ] Web interface
- [ ] Document batch processing
- [ ] Advanced export formats
- [ ] Plugin system
- [ ] Team collaboration features
- [ ] Advanced analytics dashboard