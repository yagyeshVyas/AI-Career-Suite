import requests
from bs4 import BeautifulSoup
import re

def fetch_job_description(url: str) -> dict:
    """
    Fetches job details from a URL and returns a dict with title, company, and text.
    """
    res = {"title": "", "company": "", "text": "Failed to extract text."}
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # 1. Try to find Job Title
        # Heuristic: First H1, or OG Title, or page Title
        title_tag = soup.find('h1')
        og_title = soup.find('meta', property='og:title')
        if og_title and og_title.get('content'):
            res["title"] = og_title.get('content').split('|')[0].split('-')[0].strip()
        elif title_tag:
            res["title"] = title_tag.get_text(strip=True)
        else:
            res["title"] = soup.title.string.split('|')[0].split('-')[0].strip() if soup.title else ""

        # 2. Try to find Company
        # Heuristic: meta og:site_name or looking for common company classes
        og_site = soup.find('meta', property='og:site_name')
        if og_site:
            res["company"] = og_site.get('content')
        else:
            # Fallback: Greenhouse/Lever usually have company name in title
            if soup.title and "at" in soup.title.string.lower():
                parts = soup.title.string.lower().split(" at ")
                if len(parts) > 1:
                    res["company"] = parts[1].split('|')[0].split('-')[0].strip().capitalize()

        # 3. Get Full Text
        for element in soup(["script", "style", "nav", "footer", "header", "aside"]):
            element.extract()
        
        text = soup.get_text(separator=' ', strip=True)
        text = re.sub(r'\s+', ' ', text)
        if len(text) > 10000:
            text = text[:10000]
        
        res["text"] = text
        return res

    except Exception as e:
        res["text"] = f"Error: {str(e)}"
        return res
