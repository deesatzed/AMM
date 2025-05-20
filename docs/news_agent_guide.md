# Adaptive News Briefing & Research Agent Guide

This guide provides detailed instructions for setting up, configuring, and optimizing the Adaptive News Briefing & Research Agent built with the AMM system.

## Overview

The Adaptive News Agent combines all three memory components to deliver personalized news briefings and research assistance:

1. **Fixed Knowledge**: Core information about news topics, industries, and research methodologies
2. **Dynamic Context**: Daily news headlines and abstracts that are regularly updated
3. **Adaptive Memory**: User preferences, past interactions, and research interests

## Setup Instructions

### 1. Prerequisites

Ensure you have the following:
- Python 3.11+
- AMM system installed
- Gemini API key
- News data source (RSS feeds, API, or manual updates)

### 2. Environment Configuration

Create a `.env` file with the following variables:

```
API_KEY=your-gemini-api-key
MODEL=gemini-2.5-flash-preview-04-17
MODEL2=gemini-2.5-pro-preview-05-06
EMBEDDING=models/text-embedding-004
NEWS_UPDATE_INTERVAL=3600  # Update frequency in seconds
```

### 3. Knowledge Sources Setup

#### Fixed Knowledge Sources

Create the following knowledge files:

1. `knowledge_files/news_topics.md`:
   ```markdown
   # News Topics and Categories
   
   ## Technology
   - Artificial Intelligence
   - Cybersecurity
   - Blockchain
   - ...
   
   ## Business
   - Finance
   - Startups
   - Markets
   - ...
   
   ## Science
   - Space Exploration
   - Medical Research
   - Climate Science
   - ...
   ```

2. `knowledge_files/research_methodologies.md`:
   ```markdown
   # Research Methodologies
   
   ## Primary Research
   - Interviews
   - Surveys
   - Direct Observation
   - ...
   
   ## Secondary Research
   - Literature Reviews
   - Data Analysis
   - Case Studies
   - ...
   ```

#### Dynamic Context Setup

Create placeholder files for dynamic content:

1. `knowledge_files/headlines.md`:
   ```markdown
   # Top Tech Headlines - [DATE]
   
   1. [Headline 1]
   2. [Headline 2]
   3. [Headline 3]
   ```

2. `knowledge_files/headline1_abstract.txt`, `knowledge_files/headline2_abstract.txt`, etc.

### 4. AMM Design Configuration

Using the AMM Design Studio or a JSON file, configure your News Agent:

```json
{
  "id": "adaptive_news_agent",
  "name": "Adaptive News Briefing & Research Agent",
  "description": "Provides personalized news briefings and research assistance based on user preferences and interests.",
  "knowledge_sources": [
    {
      "id": "news_topics",
      "name": "News Topics",
      "description": "Information about different news categories and topics",
      "type": "file",
      "path": "knowledge_files/news_topics.md"
    },
    {
      "id": "research_methods",
      "name": "Research Methodologies",
      "description": "Information about research approaches and techniques",
      "type": "file",
      "path": "knowledge_files/research_methodologies.md"
    },
    {
      "id": "headlines",
      "name": "Current Headlines",
      "description": "Today's top news headlines",
      "type": "file",
      "path": "knowledge_files/headlines.md"
    },
    {
      "id": "headline1",
      "name": "Headline 1 Details",
      "description": "Detailed information about headline 1",
      "type": "file",
      "path": "knowledge_files/headline1_abstract.txt"
    },
    {
      "id": "headline2",
      "name": "Headline 2 Details",
      "description": "Detailed information about headline 2",
      "type": "file",
      "path": "knowledge_files/headline2_abstract.txt"
    },
    {
      "id": "headline3",
      "name": "Headline 3 Details",
      "description": "Detailed information about headline 3",
      "type": "file",
      "path": "knowledge_files/headline3_abstract.txt"
    }
  ],
  "adaptive_memory": {
    "enabled": true,
    "retention_policy_days": 30,
    "retrieval_limit": 5
  },
  "agent_prompts": {
    "system_instruction": "You are an Adaptive News Briefing & Research Agent. Your purpose is to provide personalized news briefings and research assistance based on the user's interests and preferences. You have access to current headlines and can provide summaries and analysis. You can also help with research questions by suggesting sources, methodologies, and approaches. Always maintain a professional, informative tone while adapting to the user's level of expertise and interests based on your memory of past interactions.",
    "user_instruction_template": "Please provide information or assistance related to: {query_text}\n\nCurrent headlines are available if you'd like a news briefing."
  }
}
```

### 5. News Update Mechanism

Implement a script to regularly update the dynamic news content:

```python
# news_updater.py
import os
import time
import datetime
from typing import Dict
from pathlib import Path
from dotenv import load_dotenv
import feedparser  # For RSS feeds

# Load environment variables
load_dotenv()
UPDATE_INTERVAL = int(os.getenv("NEWS_UPDATE_INTERVAL", "3600"))

class NewsUpdater:
    def __init__(self, headlines_file: str, abstract_dir: str):
        self.headlines_file = headlines_file
        self.abstract_dir = abstract_dir
    
    def fetch_news(self) -> Dict[str, str]:
        """Fetch news from RSS feeds or APIs."""
        # Example using RSS feed
        feed = feedparser.parse("https://news.google.com/rss/search?q=technology&hl=en-US&gl=US&ceid=US:en")
        
        headlines = {}
        for i, entry in enumerate(feed.entries[:3], 1):  # Get top 3 headlines
            headline = entry.title
            abstract = f"{entry.title}\n\n{entry.summary}\n\nSource: {entry.link}"
            headlines[headline] = abstract
            
        return headlines
    
    def update_headlines(self, headlines: Dict[str, str]) -> None:
        """Update the headlines file and abstracts with new content."""
        current_date = datetime.datetime.now().strftime("%B %d, %Y")
        
        # Update headlines file
        headlines_content = f"# Top Tech Headlines - {current_date}\n\n"
        for i, headline in enumerate(headlines.keys(), 1):
            headlines_content += f"{i}. {headline}\n"
        
        Path(self.headlines_file).write_text(headlines_content)
        
        # Update abstract files
        for i, (headline, abstract) in enumerate(headlines.items(), 1):
            abstract_file = f"{self.abstract_dir}/headline{i}_abstract.txt"
            abstract_content = f"# {headline}\n\n{abstract}"
            Path(abstract_file).write_text(abstract_content)
        
        print(f"Updated headlines at {datetime.datetime.now()}")

    def run(self):
        """Run the updater in a loop."""
        while True:
            try:
                headlines = self.fetch_news()
                self.update_headlines(headlines)
            except Exception as e:
                print(f"Error updating news: {type(e).__name__} - {e}")
            
            time.sleep(UPDATE_INTERVAL)

if __name__ == "__main__":
    updater = NewsUpdater(
        headlines_file="knowledge_files/headlines.md",
        abstract_dir="knowledge_files"
    )
    updater.run()
```

### 6. Building and Running the Agent

Build the agent using the AMM build system:

```bash
python build_amm.py path/to/news_agent_design.json builds --requirements requirements.txt
```

Run the agent:

```bash
cd builds/adaptive_news_agent/
python run_amm.py
```

In a separate terminal, run the news updater:

```bash
python news_updater.py
```

## Usage Examples

### 1. News Briefing

**User Query**: "Give me today's news briefing"

**Expected Response**:
```
Here's your news briefing for May 15, 2023:

1. Google Announces New AI Features at I/O 2023
   Google unveiled several new AI features at its annual developer conference, 
   including improvements to Google Search, Assistant, and Photos...

2. Cybersecurity Firm Reports Surge in Ransomware Attacks
   A leading cybersecurity firm has reported a 30% increase in ransomware 
   attacks targeting healthcare organizations...

3. SpaceX Successfully Launches Satellite Constellation
   SpaceX has successfully launched another batch of Starlink satellites, 
   bringing the total number in orbit to over 2,000...

Based on your previous interests in AI and space technology, you might 
want to explore the Google I/O announcements and SpaceX launch in more detail.
```

### 2. Research Assistance

**User Query**: "I need to research the impact of AI on healthcare. Where should I start?"

**Expected Response**:
```
To research the impact of AI on healthcare, I recommend this approach:

1. Start with these key areas:
   - Diagnostic AI systems and their accuracy
   - AI in drug discovery and development
   - Personalized medicine through AI
   - Administrative efficiency improvements
   - Ethical considerations and patient privacy

2. Research methodologies to consider:
   - Literature review of recent medical journals
   - Case studies of hospital AI implementations
   - Comparative analysis of outcomes before/after AI adoption
   - Expert interviews with healthcare professionals

3. Suggested sources:
   - Academic: JAMA, The Lancet, Nature Medicine
   - Industry: Healthcare IT News, HIMSS publications
   - Research orgs: MIT Technology Review, Stanford HAI

I notice from our previous conversations that you're particularly 
interested in ethical implications of technology. You might want to 
focus on patient privacy concerns and algorithmic bias in healthcare AI.
```

## Optimization Strategies

### 1. Knowledge Source Optimization

- **Topic Clustering**: Group news by topic for better retrieval
- **Metadata Enrichment**: Add source credibility ratings, topic tags, and publication dates
- **Chunking Strategy**: Use semantic chunking based on article sections

### 2. Prompt Engineering

- **Persona Customization**: Adjust tone based on user preferences
- **Query Reformulation**: Implement techniques to clarify ambiguous queries
- **Response Templates**: Create templates for common query types (briefings, deep dives, research plans)

### 3. Memory Utilization

- **Interest Tracking**: Store user topic interests in metadata
- **Preference Learning**: Track which headlines users engage with
- **Continuity Management**: Reference previous research questions in related new queries

### 4. Performance Tuning

- **Caching Strategy**: Cache embeddings for headlines that don't change frequently
- **Update Optimization**: Only re-embed changed headlines
- **Retrieval Limits**: Adjust based on query complexity

## Troubleshooting

### Common Issues and Solutions

1. **Outdated News**
   - Check if the news updater is running
   - Verify RSS feed or API is accessible
   - Check file permissions for headline files

2. **Poor Relevance**
   - Adjust embedding parameters for better semantic matching
   - Review chunking strategy for knowledge sources
   - Check if too many irrelevant topics are in fixed knowledge

3. **Memory Issues**
   - Verify SQLite database is accessible
   - Check retention policy settings
   - Ensure interaction records are being properly stored

4. **Performance Problems**
   - Reduce the number of knowledge sources
   - Implement caching for frequently accessed content
   - Optimize embedding generation

## Advanced Customization

### 1. Multi-Source News Integration

Extend the news updater to pull from multiple sources:

```python
def fetch_news(self) -> Dict[str, str]:
    """Fetch news from multiple sources."""
    sources = {
        "tech": "https://news.google.com/rss/search?q=technology&hl=en-US&gl=US&ceid=US:en",
        "business": "https://news.google.com/rss/search?q=business&hl=en-US&gl=US&ceid=US:en",
        "science": "https://news.google.com/rss/search?q=science&hl=en-US&gl=US&ceid=US:en"
    }
    
    headlines = {}
    for category, url in sources.items():
        feed = feedparser.parse(url)
        for entry in feed.entries[:1]:  # Top headline from each category
            headline = f"[{category.upper()}] {entry.title}"
            abstract = f"{entry.title}\n\n{entry.summary}\n\nCategory: {category}\nSource: {entry.link}"
            headlines[headline] = abstract
    
    return headlines
```

### 2. User Preference Settings

Implement explicit preference tracking:

```python
def update_user_preferences(self, user_id: str, preferences: Dict[str, Any]) -> None:
    """Update user preferences in adaptive memory metadata."""
    # Create a record with metadata containing preferences
    record = InteractionRecordPydantic(
        query="USER_PREFERENCE_UPDATE",
        response="Preferences updated",
        timestamp=datetime.now(timezone.utc),
        additional_metadata={
            "preferences": preferences,
            "update_type": "explicit"
        }
    )
    
    self.engine.add_interaction_record(record)
```

### 3. Topic-Based Filtering

Implement filtering based on user interests:

```python
def filter_headlines_by_interests(self, headlines: Dict[str, str], interests: List[str]) -> Dict[str, str]:
    """Filter headlines based on user interests."""
    if not interests:
        return headlines
    
    filtered_headlines = {}
    for headline, abstract in headlines.items():
        # Simple keyword matching (could be enhanced with embeddings)
        if any(interest.lower() in headline.lower() or interest.lower() in abstract.lower() for interest in interests):
            filtered_headlines[headline] = abstract
    
    # If filtering removed everything, return at least one headline
    if not filtered_headlines and headlines:
        return {next(iter(headlines.keys())): next(iter(headlines.values()))}
    
    return filtered_headlines
```

## Best Practices

1. **Regular Updates**: Keep news fresh with frequent updates
2. **Source Diversity**: Include multiple news sources for balanced coverage
3. **User Feedback**: Implement mechanisms to capture explicit user feedback
4. **Privacy Considerations**: Be transparent about what is stored in memory
5. **Attribution**: Always include sources for news content
6. **Fact Verification**: Include mechanisms to verify information accuracy

## Future Enhancements

1. **Sentiment Analysis**: Add sentiment scoring to news articles
2. **Trend Detection**: Identify emerging topics across multiple sources
3. **Multimedia Integration**: Include images and videos in briefings
4. **Scheduled Briefings**: Implement automated delivery of personalized briefings
5. **Collaborative Research**: Allow multiple users to contribute to research topics
