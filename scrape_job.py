import requests
from bs4 import BeautifulSoup
import re

def fetch_job_description(url: str) -> str:
    """
    Fetches a webpage, extracts its text, and attempts to return just the readable body
    content without all the scripts and styles.
    """
    try:
        # User-agent spoofing to avoid basic bot blocks
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Remove scripts and styles
        for element in soup(["script", "style", "nav", "footer", "header", "aside"]):
            element.extract()

        # Get text
        text = soup.get_text(separator=' ', strip=True)

        # Cleanup extra newlines and spaces
        text = re.sub(r'\s+', ' ', text)
        
        # Limit to first 10,000 characters just in case it's huge
        if len(text) > 10000:
            text = text[:10000]

        if len(text) < 100:
            return "Failed to extract enough text. The site might be blocking scrapers."
            
        return text

    except Exception as e:
        return f"Error fetching URL: {str(e)}"
