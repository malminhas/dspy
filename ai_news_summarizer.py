#!/usr/bin/env python3
"""
AI News Summarizer

Usage:
    ai_news_summarizer.py [--sources=N]
    ai_news_summarizer.py (-h | --help)

Options:
    -h --help        Show this screen.
    --sources=N      Number of sources to process [default: all]

"""
import os
import sys
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Dict, Optional
import feedparser
import requests
from bs4 import BeautifulSoup
import dspy
from docopt import docopt

@dataclass
class NewsSourceConfig:
    id: str
    name: str
    description: str
    rss_url: str
    base_url: str
    enabled: bool
    tags: List[str]
    max_articles_per_source: int

@dataclass
class Article:
    title: str
    url: str
    published_date: datetime
    source_name: str
    summary: str = ""
    full_text: str = ""

DEFAULT_SOURCES = {
    # === INDUSTRY RESEARCH & MAJOR AI COMPANIES ===
    "openai-blog": NewsSourceConfig(
        id="openai-blog",
        name="OpenAI Blog",
        description="Latest research and product announcements from OpenAI",
        rss_url="https://openai.com/news/rss.xml",
        base_url="https://openai.com",
        enabled=True,
        tags=["ai", "research", "gpt", "openai"],
        max_articles_per_source=5
    ),
    
    "deepmind-blog": NewsSourceConfig(
        id="deepmind-blog",
        name="DeepMind Blog",
        description="AI research breakthroughs and insights from DeepMind",
        rss_url="https://deepmind.google/blog/feed/basic/",
        base_url="https://deepmind.google",
        enabled=True,
        tags=["ai", "research", "deepmind", "google"],
        max_articles_per_source=5
    ),
    
    "anthropic-news": NewsSourceConfig(
        id="anthropic-news",
        name="Anthropic News",
        description="AI safety and research updates from Anthropic",
        rss_url="https://raw.githubusercontent.com/Olshansk/rss-feeds/main/feeds/feed_anthropic.xml",
        base_url="https://www.anthropic.com",
        enabled=True,
        tags=["ai", "safety", "anthropic", "claude"],
        max_articles_per_source=5
    ),
    
    "google-ai-blog": NewsSourceConfig(
        id="google-ai-blog",
        name="Google AI Blog",
        description="Research and developments from Google's AI teams",
        rss_url="https://blog.google/technology/ai/rss/",
        base_url="https://blog.google",
        enabled=True,
        tags=["ai", "research", "google", "tensorflow"],
        max_articles_per_source=5
    ),

    # === ACADEMIC RESEARCH ===
    "arxiv-cs-ai": NewsSourceConfig(
        id="arxiv-cs-ai",
        name="ArXiv CS.AI",
        description="Latest AI research papers from ArXiv",
        rss_url="https://arxiv.org/rss/cs.AI",
        base_url="https://arxiv.org",
        enabled=False,  # Disabled by default - can be enabled manually
        tags=["ai", "research", "papers", "academic"],
        max_articles_per_source=3
    ),
    
    "arxiv-cs-lg": NewsSourceConfig(
        id="arxiv-cs-lg",
        name="ArXiv CS.LG (Machine Learning)",
        description="Latest machine learning research papers from ArXiv",
        rss_url="https://arxiv.org/rss/cs.LG",
        base_url="https://arxiv.org",
        enabled=False,  # Disabled by default - can be enabled manually
        tags=["ai", "ml", "research", "papers", "academic"],
        max_articles_per_source=3
    ),
    
    "berkeley-ai-research": NewsSourceConfig(
        id="berkeley-ai-research",
        name="Berkeley AI Research",
        description="Deep technical analysis from UC Berkeley AI Research",
        rss_url="https://bair.berkeley.edu/blog/feed.xml",
        base_url="https://bair.berkeley.edu",
        enabled=True,
        tags=["ai", "research", "berkeley", "academic"],
        max_articles_per_source=3
    ),

    # === SPECIALIZED AI SITES ===
    "unite-ai": NewsSourceConfig(
        id="unite-ai",
        name="Unite.AI",
        description="Latest AI news and developments",
        rss_url="https://www.unite.ai/feed/",
        base_url="https://www.unite.ai",
        enabled=True,
        tags=["ai", "news", "industry"],
        max_articles_per_source=5
    ),
    
    "the-decoder": NewsSourceConfig(
        id="the-decoder",
        name="The Decoder",
        description="AI news and deep dives into artificial intelligence",
        rss_url="https://the-decoder.com/feed/",
        base_url="https://the-decoder.com",
        enabled=True,
        tags=["ai", "news", "analysis"],
        max_articles_per_source=3
    ),
    
    "ai-business": NewsSourceConfig(
        id="ai-business",
        name="AI Business",
        description="Business-focused AI news and insights",
        rss_url="https://aibusiness.com/rss.xml",
        base_url="https://aibusiness.com",
        enabled=True,
        tags=["ai", "business", "enterprise"],
        max_articles_per_source=3
    ),

    # === NEWS & INDUSTRY ANALYSIS ===
    "mit-tech-review": NewsSourceConfig(
        id="mit-tech-review",
        name="MIT Technology Review",
        description="In-depth technology analysis and AI coverage",
        rss_url="https://www.technologyreview.com/feed/",
        base_url="https://www.technologyreview.com",
        enabled=True,
        tags=["tech", "ai", "analysis", "mit"],
        max_articles_per_source=3
    ),
    
    "venturebeat-ai": NewsSourceConfig(
        id="venturebeat-ai",
        name="VentureBeat AI",
        description="AI-focused coverage from VentureBeat",
        rss_url="https://venturebeat.com/category/ai/feed/",
        base_url="https://venturebeat.com",
        enabled=True,
        tags=["ai", "business", "startups"],
        max_articles_per_source=4
    ),
    
    "wired-ai": NewsSourceConfig(
        id="wired-ai",
        name="Wired AI",
        description="AI coverage from Wired magazine",
        rss_url="https://www.wired.com/feed/tag/ai/latest/rss",
        base_url="https://www.wired.com",
        enabled=True,
        tags=["ai", "tech", "culture", "wired"],
        max_articles_per_source=3
    )
}

class AINewsSummarizer:
    def __init__(self):
        # Initialize DSPy with Perplexity
        perplexity_key = os.environ.get('PERPLEXITY_API_KEY')
        if not perplexity_key:
            raise ValueError('PERPLEXITY_API_KEY environment variable is required')
        
        self.lm = dspy.LM('perplexity/sonar', api_key=perplexity_key)
        dspy.configure(lm=self.lm)
        
        # Set up session for HTTP requests
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def get_enabled_sources(self, limit: Optional[int] = None) -> List[NewsSourceConfig]:
        """Get enabled sources, optionally limited to N sources"""
        enabled_sources = [source for source in DEFAULT_SOURCES.values() if source.enabled]
        
        if limit and limit != "all":
            try:
                limit_int = int(limit)
                enabled_sources = enabled_sources[:limit_int]
            except ValueError:
                print(f"Warning: Invalid limit '{limit}', using all sources")
        
        return enabled_sources
    
    def is_today_or_recent(self, article_date: datetime, days_back: int = 2) -> bool:
        """Check if article is from today or recent days (to account for timezone differences)"""
        today = datetime.now()
        cutoff_date = today - timedelta(days=days_back)
        return article_date >= cutoff_date
    
    def parse_rss_feed(self, source: NewsSourceConfig) -> List[Article]:
        """Parse RSS feed and return recent articles"""
        try:
            print(f"  📡 Fetching RSS feed for {source.name}...")
            
            # Fetch the RSS feed
            response = self.session.get(source.rss_url, timeout=10)
            response.raise_for_status()
            
            # Parse the feed
            feed = feedparser.parse(response.content)
            
            articles = []
            for entry in feed.entries[:source.max_articles_per_source * 2]:  # Get extra to filter by date
                try:
                    # Parse publication date
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        pub_date = datetime(*entry.published_parsed[:6])
                    elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                        pub_date = datetime(*entry.updated_parsed[:6])
                    else:
                        # If no date, skip or use current date
                        print(f"    ⚠️  No date found for article: {getattr(entry, 'title', 'Unknown')}")
                        continue
                    
                    # Filter for recent articles
                    if not self.is_today_or_recent(pub_date):
                        continue
                    
                    # Create article object
                    article = Article(
                        title=getattr(entry, 'title', 'No title'),
                        url=getattr(entry, 'link', ''),
                        published_date=pub_date,
                        source_name=source.name
                    )
                    
                    articles.append(article)
                    
                    if len(articles) >= source.max_articles_per_source:
                        break
                        
                except Exception as e:
                    print(f"    ⚠️  Error parsing entry: {e}")
                    continue
            
            print(f"    ✅ Found {len(articles)} recent articles from {source.name}")
            return articles
            
        except Exception as e:
            print(f"    ❌ Error fetching RSS feed for {source.name}: {e}")
            return []
    
    def collect_articles(self, sources: List[NewsSourceConfig]) -> List[Article]:
        """Collect articles from all RSS feeds"""
        print("\n🔍 Collecting articles from RSS feeds...")
        
        all_articles = []
        for source in sources:
            articles = self.parse_rss_feed(source)
            all_articles.extend(articles)
        
        print(f"\n📰 Total articles collected: {len(all_articles)}")
        
        # Sort by publication date (newest first)
        all_articles.sort(key=lambda x: x.published_date, reverse=True)
        
        return all_articles
    
    def fetch_article_content(self, article: Article) -> str:
        """Fetch full HTML content and extract article text"""
        try:
            print(f"  🌐 Fetching content for: {article.title[:60]}...")
            
            # Fetch the HTML content
            response = self.session.get(article.url, timeout=15)
            response.raise_for_status()
            
            # Parse HTML with BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove unwanted elements
            for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'iframe']):
                element.decompose()
            
            # Try different strategies to find main content
            article_text = ""
            
            # Strategy 1: Look for common article content selectors
            content_selectors = [
                'article',
                '[role="main"]',
                '.post-content',
                '.article-content',
                '.entry-content',
                '.content',
                '.post-body',
                '.article-body',
                'main',
                '.main-content'
            ]
            
            for selector in content_selectors:
                content_element = soup.select_one(selector)
                if content_element:
                    article_text = content_element.get_text(strip=True, separator=' ')
                    break
            
            # Strategy 2: If no specific content found, get all paragraphs
            if not article_text:
                paragraphs = soup.find_all('p')
                article_text = ' '.join([p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 50])
            
            # Strategy 3: Fallback to body text
            if not article_text:
                body = soup.find('body')
                if body:
                    article_text = body.get_text(strip=True, separator=' ')
            
            # Clean up the text
            article_text = ' '.join(article_text.split())  # Normalize whitespace
            
            if len(article_text) < 100:
                print(f"    ⚠️  Warning: Article content seems too short ({len(article_text)} chars)")
            else:
                print(f"    ✅ Extracted {len(article_text)} characters")
            
            return article_text
            
        except Exception as e:
            print(f"    ❌ Error fetching content for {article.url}: {e}")
            return ""
    
    def fetch_all_article_content(self, articles: List[Article]) -> List[Article]:
        """Fetch full content for all articles"""
        print(f"\n📄 Fetching full content for {len(articles)} articles...")
        
        for i, article in enumerate(articles, 1):
            print(f"\n[{i}/{len(articles)}]", end=" ")
            article.full_text = self.fetch_article_content(article)
            
            # Add a small delay to be respectful to servers
            if i < len(articles):
                import time
                time.sleep(1)
        
        # Filter out articles with no content
        articles_with_content = [a for a in articles if len(a.full_text) > 100]
        
        print(f"\n✅ Successfully retrieved content for {len(articles_with_content)}/{len(articles)} articles")
        
        return articles_with_content
    
    def summarize_article(self, article: Article) -> str:
        """Summarize article content using DSPy/Perplexity"""
        try:
            print(f"  🤖 Summarizing: {article.title[:60]}...")
            
            # Define DSPy signature for summarization
            class ArticleSummarizer(dspy.Signature):
                """Summarize a news article into a single, informative paragraph that captures the key points and significance."""
                
                title: str = dspy.InputField(desc="Article title")
                content: str = dspy.InputField(desc="Full article content")
                summary: str = dspy.OutputField(desc="Single paragraph summary capturing key points and significance")
            
            # Create summarizer
            summarizer = dspy.ChainOfThought(ArticleSummarizer)
            
            # Truncate content if too long (to stay within token limits)
            max_content_length = 8000  # Adjust based on model limits
            truncated_content = article.full_text[:max_content_length]
            if len(article.full_text) > max_content_length:
                truncated_content += "... [content truncated]"
            
            # Generate summary
            result = summarizer(
                title=article.title,
                content=truncated_content
            )
            
            summary = result.summary.strip()
            
            print(f"    ✅ Generated summary ({len(summary)} chars)")
            return summary
            
        except Exception as e:
            print(f"    ❌ Error summarizing article: {e}")
            return f"Summary unavailable for this article. Error: {str(e)}"
    
    def summarize_all_articles(self, articles: List[Article]) -> List[Article]:
        """Generate summaries for all articles"""
        print(f"\n🤖 Generating summaries for {len(articles)} articles...")
        
        for i, article in enumerate(articles, 1):
            print(f"\n[{i}/{len(articles)}]", end=" ")
            article.summary = self.summarize_article(article)
            
            # Add a small delay to be respectful to API
            if i < len(articles):
                import time
                time.sleep(2)  # Slightly longer delay for API calls
        
        print(f"\n✅ Generated summaries for all {len(articles)} articles")
        return articles
    
    def generate_executive_summary(self, articles: List[Article]) -> str:
        """Generate an executive summary from all article summaries"""
        try:
            print(f"\n📊 Generating executive summary from {len(articles)} articles...")
            
            # Define DSPy signature for executive summary
            class ExecutiveSummarizer(dspy.Signature):
                """Generate an executive summary from multiple AI news article summaries, highlighting key trends and developments."""
                
                article_summaries: str = dspy.InputField(desc="Combined summaries of all articles")
                date: str = dspy.InputField(desc="Date of the report")
                executive_summary: str = dspy.OutputField(desc="Executive summary highlighting key trends, developments, and insights from the AI news")
            
            # Create summarizer
            exec_summarizer = dspy.ChainOfThought(ExecutiveSummarizer)
            
            # Combine all summaries
            combined_summaries = "\n\n".join([
                f"{i+1}. {article.title} ({article.source_name}): {article.summary}"
                for i, article in enumerate(articles)
            ])
            
            # Generate executive summary
            result = exec_summarizer(
                article_summaries=combined_summaries,
                date=datetime.now().strftime("%Y-%m-%d")
            )
            
            summary = result.executive_summary.strip()
            print(f"    ✅ Generated executive summary ({len(summary)} chars)")
            return summary
            
        except Exception as e:
            print(f"    ❌ Error generating executive summary: {e}")
            return "Executive summary unavailable due to processing error."
    
    def generate_html_report(self, articles: List[Article], executive_summary: str) -> str:
        """Generate HTML report with executive summary and article summaries"""
        
        report_date = datetime.now().strftime("%Y-%m-%d")
        report_time = datetime.now().strftime("%H:%M:%S")
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI News Summary - {report_date}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f8f9fa;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
            font-weight: 700;
        }}
        .header .subtitle {{
            margin: 10px 0 0 0;
            font-size: 1.2em;
            opacity: 0.9;
        }}
        .executive-summary {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }}
        .executive-summary h2 {{
            color: #333;
            margin-top: 0;
            font-size: 1.8em;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }}
        .articles-section {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .articles-section h2 {{
            color: #333;
            margin-top: 0;
            font-size: 1.8em;
            border-bottom: 3px solid #764ba2;
            padding-bottom: 10px;
        }}
        .article {{
            border-left: 4px solid #667eea;
            padding: 20px;
            margin: 20px 0;
            background: #f8f9fa;
            border-radius: 0 8px 8px 0;
        }}
        .article h3 {{
            margin-top: 0;
            color: #333;
            font-size: 1.3em;
        }}
        .article .meta {{
            color: #666;
            font-size: 0.9em;
            margin-bottom: 15px;
        }}
        .article .summary {{
            font-size: 1em;
            line-height: 1.7;
            color: #444;
        }}
        .article .link {{
            margin-top: 15px;
        }}
        .article .link a {{
            color: #667eea;
            text-decoration: none;
            font-weight: 500;
        }}
        .article .link a:hover {{
            text-decoration: underline;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            color: #666;
            font-size: 0.9em;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .stat {{
            background: rgba(255,255,255,0.2);
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }}
        .stat .number {{
            font-size: 2em;
            font-weight: bold;
            display: block;
        }}
        .stat .label {{
            font-size: 0.9em;
            opacity: 0.9;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🤖 AI News Summary</h1>
        <div class="subtitle">Generated on {report_date} at {report_time}</div>
        <div class="stats">
            <div class="stat">
                <span class="number">{len(articles)}</span>
                <span class="label">Articles Analyzed</span>
            </div>
            <div class="stat">
                <span class="number">{len(set(a.source_name for a in articles))}</span>
                <span class="label">Sources</span>
            </div>
        </div>
    </div>

    <div class="executive-summary">
        <h2>📊 Executive Summary</h2>
        <p>{executive_summary}</p>
    </div>

    <div class="articles-section">
        <h2>📰 Article Summaries</h2>
"""
        
        for i, article in enumerate(articles, 1):
            html_content += f"""
        <div class="article">
            <h3>{i}. {article.title}</h3>
            <div class="meta">
                <strong>Source:</strong> {article.source_name} | 
                <strong>Published:</strong> {article.published_date.strftime("%Y-%m-%d %H:%M")}
            </div>
            <div class="summary">{article.summary}</div>
            <div class="link">
                <a href="{article.url}" target="_blank">Read full article →</a>
            </div>
        </div>
"""
        
        html_content += f"""
    </div>

    <div class="footer">
        <p>Report generated by AI News Summarizer using DSPy and Perplexity AI</p>
        <p>Sources processed: {', '.join(set(a.source_name for a in articles))}</p>
    </div>
</body>
</html>
"""
        
        return html_content

def main():
    arguments = docopt(__doc__)
    
    print("🤖 AI News Summarizer")
    print("=" * 50)
    
    # Initialize summarizer
    try:
        summarizer = AINewsSummarizer()
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    # Get sources to process
    sources_limit = arguments.get('--sources', 'all')
    sources = summarizer.get_enabled_sources(sources_limit)
    
    print(f"Processing {len(sources)} news sources...")
    for source in sources:
        print(f"  • {source.name}")
    
    # Step 1: Collect articles from RSS feeds
    articles = summarizer.collect_articles(sources)
    
    if not articles:
        print("\n❌ No recent articles found. Try again later or check the RSS feeds.")
        return
    
    # Show what we found
    print(f"\n📋 Recent articles found:")
    for i, article in enumerate(articles[:10], 1):  # Show first 10
        print(f"  {i}. {article.title}")
        print(f"     Source: {article.source_name} | Date: {article.published_date.strftime('%Y-%m-%d %H:%M')}")
        print(f"     URL: {article.url}")
        print()
    
    if len(articles) > 10:
        print(f"  ... and {len(articles) - 10} more articles")
    
    print(f"\nNext: Implement HTML content retrieval...")
    # Step 2: Fetch full content for each article
    articles_with_content = summarizer.fetch_all_article_content(articles)
    
    if not articles_with_content:
        print("\n❌ No article content could be retrieved.")
        return
    
    # Show content preview
    print(f"\n📖 Content retrieved successfully:")
    for i, article in enumerate(articles_with_content[:3], 1):  # Show first 3
        print(f"\n{i}. {article.title}")
        print(f"   Content preview: {article.full_text[:200]}...")
        print(f"   Full length: {len(article.full_text)} characters")
    
    print(f"\nNext: Implement DSPy summarization...")
    # Step 3: Generate summaries for all articles
    summarized_articles = summarizer.summarize_all_articles(articles_with_content)
    
    # Show summaries
    print(f"\n📝 Article Summaries:")
    for i, article in enumerate(summarized_articles[:10], 1):  # Show first 10
        print(f"  {i}. {article.title}")
        print(f"     Summary: {article.summary}")
        print()
    
    if len(summarized_articles) > 10:
        print(f"  ... and {len(summarized_articles) - 10} more summaries")

    # Step 4: Generate executive summary
    executive_summary = summarizer.generate_executive_summary(summarized_articles)
    print(f"\n📊 Executive Summary:")
    print(executive_summary)

    # Step 5: Generate HTML report
    html_report = summarizer.generate_html_report(summarized_articles, executive_summary)
    print(f"\n📄 Generating HTML report...")
    with open("ai_news_summary.html", "w", encoding="utf-8") as f:
        f.write(html_report)
    print("✅ HTML report generated as ai_news_summary.html")

if __name__ == '__main__':
    main() 