# AI Browser Agent

Intelligent browser automation software using Playwright and Gemini Flash 2.5 LLM with command-line interface for automated task execution.

## Features

- 🤖 **LLM-Driven Automation**: Uses Gemini Flash 2.5 for intelligent task interpretation and execution
- 🌐 **Cross-Browser Support**: Works with Chromium, Firefox, and WebKit via Playwright
- 🔧 **Command-Line Interface**: Easy-to-use CLI for task execution and automation
- 🔐 **Secure Credential Management**: Encrypted storage for login credentials and API keys
- 🎯 **Context-Aware**: Maintains conversation history and page context across interactions
- ⚡ **Async Performance**: Non-blocking operations for optimal performance
- 🛡️ **Error Recovery**: Intelligent error handling with LLM-driven troubleshooting

## Quick Start

### Installation

```bash
git clone https://github.com/streetquant/ai-browser-agent.git
cd ai-browser-agent
pip install -r requirements.txt
playwright install
```

### Setup

1. Copy environment template:
```bash
cp .env.example .env
```

2. Add your Gemini API key to `.env`:
```
GEMINI_API_KEY=your_api_key_here
```

### Usage

```bash
# Navigate to a website
python src/main.py navigate --url "https://example.com"

# Execute a task with LLM guidance
python src/main.py task --prompt "Find and click the login button" --headless

# Login to a website
python src/main.py login --site "github.com" --username "your_user" --password "your_pass"

# Interactive mode
python src/main.py interactive --site "https://admin.dashboard.com"
```

## Architecture

- **CLI Layer**: Command parsing and user interface
- **Browser Engine**: Playwright-based browser automation
- **LLM Integration**: Gemini Flash 2.5 for intelligent decision making
- **Security**: Encrypted credential management and secure operations

## Development

### Running Tests
```bash
pytest tests/
```

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Security

- Never commit API keys or credentials
- Use environment variables for sensitive data
- Enable 2FA on connected accounts
- Review automation scripts before execution

## Roadmap

- [ ] Multi-tab support
- [ ] Workflow scripting with YAML
- [ ] Plugin system for custom actions
- [ ] Web UI for task management
- [ ] Integration with other LLM providers
