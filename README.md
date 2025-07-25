# 🤖 DSPy AI Repository

A comprehensive collection of DSPy (Declarative Self-improving Language Programs) examples and tools for building AI-powered applications.

## 📚 What's In This Repository

### 1. **DSPy Playbook** (`dspy-playbook.ipynb`)
An interactive Jupyter notebook demonstrating key DSPy concepts and use cases:

- **Multi-provider LLM Setup** - Configure OpenAI, Anthropic, Perplexity, and Groq
- **Information Extraction** - Structured data extraction from text
- **Sentiment Analysis** - Classify text with confidence scores  
- **RAG (Retrieval-Augmented Generation)** - Question answering with external knowledge
- **ReAct Agents** - Reasoning and Acting with tool integration
- **Multi-Stage Pipelines** - Complex document generation workflows

### 2. **AI News Summarizer** (`ai_news_summarizer.py`)
A production-ready CLI tool that generates daily AI news summaries using DSPy and Perplexity:

- **Automated RSS Collection** - Fetches from 11+ AI news sources
- **Smart Content Extraction** - Retrieves full article text from web pages
- **AI-Powered Summarization** - Uses Perplexity via DSPy for intelligent summaries
- **Executive Summary** - Meta-analysis of daily AI trends
- **Beautiful HTML Reports** - Professional presentation with source links

📄 **[View Latest AI News Summary](https://malminhas.github.io/dspy/ai_news_summary.html)** *(Live Demo)*

## 📸 Preview

### AI News Summary Report
The generated HTML reports feature:
- **Modern Design** - Clean, professional styling with responsive layout
- **Executive Summary** - AI-generated overview of key trends
- **Article Cards** - Individual summaries with metadata and source links  
- **Statistics Dashboard** - Article count and source metrics

Screenshot below. You can also [view the live demo](https://malminhas.github.io/dspy/ai_news_summary.html)

<img width="600" height="900" alt="image" src="https://github.com/user-attachments/assets/119a163d-91ad-490b-94ae-b5426fc8178b" />


## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Virtual environment (recommended)
- API keys for your preferred LLM providers

### Setup

1. **Clone and setup environment:**
```bash
git clone <your-repo-url>
cd dspy
pip install -r requirements.txt
```

2. **Configure API keys** (create `local.env`):
```bash
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key  
PERPLEXITY_API_KEY=your_perplexity_key
GROQ_API_KEY=your_groq_key
```

3. **Run the DSPy Playbook:**
```bash
jupyter notebook dspy-playbook.ipynb
```

4. **Generate AI News Summary:**
```bash
source local.env
python ai_news_summarizer.py --sources=5
```

## 📊 AI News Summarizer Features

### Supported News Sources
- **Industry Leaders**: OpenAI Blog, DeepMind, Anthropic, Google AI Blog
- **Academic Research**: Berkeley AI Research, ArXiv (optional)
- **Industry Analysis**: MIT Tech Review, VentureBeat AI, Wired AI
- **Specialized Sites**: Unite.AI, The Decoder, AI Business

### CLI Usage
```bash
# Process all enabled sources
python ai_news_summarizer.py

# Limit to first N sources  
python ai_news_summarizer.py --sources=3

# Show help
python ai_news_summarizer.py --help
```

### Output Features
- ✅ **Article Summaries** - Single-paragraph summaries of each article
- ✅ **Executive Summary** - AI-generated overview of daily trends
- ✅ **Source Attribution** - Links back to original articles
- ✅ **Publication Dates** - Timestamp information
- ✅ **Modern UI** - Professional HTML styling with responsive design

## 🏗️ Architecture

### DSPy Integration
Both the playbook and news summarizer demonstrate DSPy's power:

- **Signatures** - Define input/output schemas for AI tasks
- **Modules** - Reusable components (Predict, ChainOfThought, ReAct)
- **Multi-provider Support** - Seamless switching between LLM providers
- **Structured Outputs** - Type-safe AI responses

### News Summarizer Pipeline
```
RSS Feeds → Content Extraction → AI Summarization → Executive Summary → HTML Report
```

1. **RSS Collection** - Parallel fetching from multiple sources
2. **Content Scraping** - Intelligent HTML parsing with fallbacks
3. **AI Summarization** - DSPy ChainOfThought with Perplexity
4. **Report Generation** - Beautiful HTML with embedded CSS

## 📁 File Structure

```
dspy/
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── local.env                # API keys (not in git)
├── dspy-playbook.ipynb      # Interactive DSPy examples
├── ai_news_summarizer.py    # News summarization CLI
├── ai_news_summary.html     # Latest generated report
└── .gitignore               # Git ignore patterns
```

## 🔧 Development

### Adding New News Sources
Edit the `DEFAULT_SOURCES` dictionary in `ai_news_summarizer.py`:

```python
"new-source": NewsSourceConfig(
    id="new-source",
    name="New AI Source",
    description="Description of the source",
    rss_url="https://example.com/feed.xml",
    base_url="https://example.com",
    enabled=True,
    tags=["ai", "news"],
    max_articles_per_source=5
)
```

### Customizing Summarization
Modify the `ArticleSummarizer` DSPy signature for different summary styles:

```python
class ArticleSummarizer(dspy.Signature):
    """Custom summarization prompt here."""
    title: str = dspy.InputField(desc="Article title")
    content: str = dspy.InputField(desc="Full article content")
    summary: str = dspy.OutputField(desc="Your custom summary format")
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **[DSPy Framework](https://dspy.ai/)** - For the declarative AI programming paradigm
- **[Perplexity AI](https://www.perplexity.ai/)** - For high-quality AI summarization
- **AI News Sources** - For providing RSS feeds and quality content

---

**Generated with ❤️ using DSPy and AI** 
