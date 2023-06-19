import requests
from bs4 import BeautifulSoup
from summarizer import Summarizer
import openai

# Set up the OpenAI API credentials
openai.api_key = 'YOUR_API_KEY'

# Define the ChatGPT model
MODEL_NAME = 'gpt-3.5-turbo'

async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()

async def search_papers(query):
    async with aiohttp.ClientSession() as session:
        search_query = scholarly.search_pubs(query)
        tasks = [fetch(session, pub.bib['url']) for pub in search_query]
        papers = await asyncio.gather(*tasks)
        return papers

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

    def create_content_outline(self):
        outline = {
            "Topic": self.topic,
            "Introduction": {
                "Hook": "An engaging opening statement to capture the reader's attention.",
                "Background": "Brief background information on the topic.",
                "Thesis Statement": "A clear statement of the main argument or point."
            },
            "Body": {
                f"Point {i+1}": {
                    "Main Idea": summary,
                    "Supporting Evidence": "Relevant data, quotes, or anecdotes that support the main idea.",
                    "Explanation": "An explanation of how the evidence supports the main idea."
                }
                for i, summary in enumerate(self.summaries)
            },
            "Conclusion": {
                "Summary": "A summary of the main points discussed in the body.",
                "Restatement of Thesis": "A restatement of the thesis statement in light of the evidence discussed.",
                "Closing Thoughts": "Final thoughts or implications of the topic."
            },
            "References": "A list of sources cited in the article."
        }
        return outline

    def generate_outline_with_gpt(self):
        outline_prompt = f"Outline the content for a research article on the topic: {self.topic}\n\n"
        response = openai.Completion.create(
            model=MODEL_NAME,
            prompt=outline_prompt,
            max_tokens=500,
            stop=None,
            temperature=0.7,
            n=1,
            return_prompt=False
        )
        return response.choices[0].text.strip()

# Use your Autonomous Researcher
researcher = AutonomousResearcher()

# Get the top 5 trending topics
trending_topics = researcher.get_trending_topics()
print("Trending topics:", trending_topics)

# Pick one topic and do extensive research on it
researcher.topic = trending_topics[0]
researcher.papers = await search_papers(researcher.topic)
researcher.summaries = summarize_papers(researcher.papers)

# Create a content creation outline using ChatGPT
outline = researcher.generate_outline_with_gpt()
print("Content creation outline:", outline)
