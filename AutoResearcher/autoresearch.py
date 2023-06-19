import requests
from bs4 import BeautifulSoup 
from scholarly import scholarly
from summarizer import Summarizer
import asyncio 
import aiohttp

async def fetch(session, url): async with session.get(url) as response: return await response.text() async def search_papers(query): async with aiohttp.ClientSession() as session: search_query = scholarly.search_pubs(query) tasks = [fetch(session, pub.bib['url']) for pub in search_query] papers = await asyncio.gather(*tasks) return papers 

def summarize_papers(papers):
    model = Summarizer()
    summaries = [model(paper['abstract']) for paper in papers]
    return summaries 

# Define your Autonomous Researcher
class AutonomousResearcher:
    def __init__(self):
        self.topic = None
        self.papers = None
        self.summaries = None 

    def get_trending_topics(self):
        response = requests.get("https://trends.google.com/trends/trendingsearches/daily?geo=US")
        soup = BeautifulSoup(response.text, 'html.parser')
        topics = [topic.text for topic in soup.find_all('a', {'class': 'topic'})]
        return topics[:5] 

    def create_content_outline(self): outline = { "Topic": self.topic, "Introduction": { "Hook": "An engaging opening statement to capture the reader's attention.", "Background": "Brief background information on the topic.", "Thesis Statement": "A clear statement of the main argument or point." }, "Body": { f"Point {i+1}": { "Main Idea": summary, "Supporting Evidence": "Relevant data, quotes, or anecdotes that support the main idea.", "Explanation": "An explanation of how the evidence supports the main idea." } for i, summary in enumerate(self.summaries) }, "Conclusion": { "Summary": "A summary of the main points discussed in the body.", "Restatement of Thesis": "A restatement of the thesis statement in light of the evidence discussed.", "Closing Thoughts": "Final thoughts or implications of the topic." }, "References": "A list of sources cited in the article." } return outline


# Use your Autonomous Researcher
researcher = AutonomousResearcher() 

# Get the top 5 trending topics
trending_topics = researcher.get_trending_topics()
print("Trending topics:", trending_topics) 

# Pick one topic and do extensive research on it
researcher.topic = trending_topics[0]
researcher.papers = search_papers(researcher.topic)
researcher.summaries = summarize_papers(researcher.papers) 

# Create a content creation outline
outline = researcher.create_content_outline()
print("Content creation outline:", outline)
