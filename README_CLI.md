# Docia CLI - VisionLM Document Intelligence Tool

A powerful command-line interface for intelligent document analysis using Vision Language Models.

## 🚀 Quick Start

After installation, start the interactive shell:

```bash
docia shell
```

The shell will start in ADD MODE, where you can add documents by entering file paths or dragging and dropping files.

Once documents are added, the shell automatically switches to QUERY MODE, where you can ask questions directly by typing them.

## 📚 Interactive Shell Usage

### Modes

The interactive shell has two modes:

1. **ADD MODE** - For adding documents
   - Enter file paths directly or drag and drop files
   - Example: `C:\Documents\report.pdf`

2. **QUERY MODE** - For asking questions about documents
   - Type questions directly
   - Example: `What is the main topic of this document?`

### Commands

Use `/` to see available commands:

```bash
/                 - Show command menu
/add              - Switch to add document mode
/query            - Switch to query mode
/list             - List all documents
/clear            - Clear conversation history
/exit             - Exit the shell
```

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

## 🛠️ Command Line Usage

You can also use Docia with direct commands:

### Adding Documents
```bash
# Add a PDF document
docia add path/to/document.pdf

# Add with custom name
docia add path/to/report.pdf --name "Q3 Financial Report"
```

### Listing Documents
```bash
# List all documents
docia list
```

### Querying Documents
```bash
# Basic query
docia query "What were the Q3 revenue figures?"

# Query specific documents
docia query "What is the authentication process?" -d doc_1 -d doc_2
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

## 💡 Tips

1. **Start with the interactive shell** - It's the easiest way to use Docia
2. **Add documents first** - Most queries need documents to analyze
3. **Ask specific questions** - The more specific your question, the better the results
4. **Monitor task progress** - Watch the task display to see what Docia is working on
5. **Use conversation mode** - Ask follow-up questions for deeper insights

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