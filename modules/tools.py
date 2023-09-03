import os
from langchain.tools.base import BaseTool
from typing import Dict
import logging
import random
import requests
from requests.exceptions import JSONDecodeError
from urllib.parse import quote
from datetime import date, datetime, timedelta
import chainlit as cl

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# TOOLS
class NewsSearchTool(BaseTool):
    name = "News"
    description = "Use this when you want to get information about the top headlines of current news stories. The input should be a question in natural language that this API can answer."

    def _run(self, query: str) -> Dict:
        # URL-encode the query parameter
        encoded_query = quote(query)

        # Calculate the date range for the last week
        today = datetime.today()
        last_week = today - timedelta(days=5)
        from_date = last_week.strftime('%Y-%m-%d')
        to_date = today.strftime('%Y-%m-%d')

        url = ('https://newsapi.org/v2/everything?'
            f'q={encoded_query}&'
            f'from={from_date}&'
            f'to={to_date}&'
            'language=en&'
            'sortBy=popularity&'
            'apiKey=27161a2559d247abb02c031f5e065837')
        
        response = requests.get(url)
        json_response = response.json()

        # Limit the results to the top 10 articles
        top_10_articles = json_response['articles'][:10]
        json_response['articles'] = top_10_articles

        # Generate a markdown ordered list
        markdown_list_items = []
        for i, article in enumerate(top_10_articles):
            source_name = article['source'].get('name') or article['source'].get('Name') or "Unknown"
            markdown_list_items.append(f"1. {article['title']} [({source_name})]({article['url']})")

        markdown_output = f"## {query} News\n\n" + "\n".join(markdown_list_items)

        # Generate a plain text ordered list
        plain_text_list_items = []
        for i, article in enumerate(top_10_articles):
            source_name = article['source'].get('name') or article['source'].get('Name') or "Unknown"
            plain_text_list_items.append(f"- {article['title']} ({article['url']})\n")

        clipboard = "".join(plain_text_list_items)

        cl.user_session.set("clipboard", clipboard)

        return markdown_output

    async def _arun(self, query: str) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("News API does not support async")


class WikipediaSearchTool(BaseTool):
    name = "Wikipedia"
    description = "Use this when you want to search wikipedia about things you have no knowledge of. The input to this should be a single search term."

    def get_wiki_image(self, query, response):
        data = response.json()

        if data.get('originalimage') and data['originalimage'].get('source'):
            return data['originalimage']['source']

        url = f'https://en.wikipedia.org/api/rest_v1/page/media-list/{query}'
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            # Parse the data and return the desired value
            return data['items'][0]['srcset'][0]['src']
        else:
            # Handle the error or return a default value
            return None

    def _run(self, query: str) -> str:
        queryUnderscored = query.replace(" ", "_")
        url = ('https://en.wikipedia.org/api/rest_v1/page/summary/'
            f'{queryUnderscored}?redirect=false')

        response = requests.get(url)

        if response.status_code == 200:
            try:
                data = response.json()
            except JSONDecodeError:
                return f"🧑‍🦲 I'm so sorry! The Wikipedia entry on {query} is unavailable at the moment. Please try again later."

            # Parse the data and return the desired value
            wikiTitle = data.get('title', 'No title available')
            wikiURL = data['content_urls']['desktop']['page']
            wikiExtract = data.get('extract', 'No summary available')
            wikiImage = self.get_wiki_image(queryUnderscored, response)

            markdown = f"![{wikiTitle}]({wikiImage})\n\n## {wikiTitle}\n{wikiExtract}\n**Source:** [{wikiTitle} Wikipedia page]({wikiURL})"

            clipboard = f"{wikiTitle}\n{wikiExtract}\n\nSource: {wikiURL}"

            cl.user_session.set("clipboard", clipboard)

            return markdown
        else:
            # Handle the error or return a default value
            return f"🧑‍🦲 I'm so sorry! The Wikipedia entry on {query} is unavailable at the moment. Please try again later."

    async def _arun(self, query: str) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("Wikipedia API does not support async")
    

class YouTubeSearchTool(BaseTool):
    name = "YouTube"
    description = "Use this when you want to search for videos. The input to this should be a single search term."

    def _run(self, query: str) -> str:
        # URL-encode the query parameter
        encoded_query = quote(query)
        url = ('https://www.googleapis.com/youtube/v3/search?maxResults=5&q='
            f'{encoded_query}&key={os.environ.get("YOUTUBE_API_KEY")}&type=video&part=snippet')

        response = requests.get(url)

        if response.status_code == 200:
            try:
                data = response.json()
                # Parse the data and return the desired value
                ytVideoId = None
                for item in data['items']:
                    if 'videoId' in item['id']:
                        ytVideoId = item['id']['videoId']
                        break

                if ytVideoId:
                    html = f"""
    <div class="card text-bg-light text-center">
        <div class='card-header text-uppercase pt-3 pb-2 px-3'>
            <a href="https://www.youtube.com/watch?v={ytVideoId}" target="_blank" style='text-decoration: none'><h2 class='text-primary text-uppercase'>{query}</h2></a>
        </div>
        <div class='card-body pt-2 pb-1 px-2' style='max-width: 100%'>
            <iframe width="100%" height="280" src="https://www.youtube-nocookie.com/embed/{ytVideoId}" title="" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>
        </div>
        <div class="card-footer pt-2 pb-2 px-2">
            <a href="https://www.youtube.com/watch?v={ytVideoId}" target="_blank"><button class="btn btn-secondary btn-lg text-center" style='width: 80%'>SEE MORE...</button></a>
        </div>
    </div>
                    """
                    return html
                else:
                    # Handle the error or return a default value
                    return "🧑‍🦲 I'm so sorry! I couldn't find a YouTube video about that unfortunately."
            except JSONDecodeError:
                return "🧑‍🦲 I'm so sorry! I can't find that YouTube video at the moment. Please try again later."
            
    async def _arun(self, query: str) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("YouTube API does not support async")


class GoogleMapsSearchTool(BaseTool):
    name = "Google Maps"
    description = "Use this when you want to search for a location or get a map. The input to this should be a single search term."

    def _run(self, query: str) -> str:
        # URL-encode the query parameter
        encoded_query = quote(query)
        url = "https://www.google.com/maps/embed/v1/place?"f"key={os.environ.get('GOOGLE_MAPS_API_KEY')}&q={encoded_query}"

        return f"""
            <div class="card text-bg-light text-center">
                <div class='card-header text-uppercase pt-3 pb-2 px-3'>
                    <a href="https://www.google.com/maps/search/{encoded_query}" target="_blank" style='text-decoration: none'><h2 class='text-primary text-uppercase'>{query}</h2></a>
                </div>
                <div class='card-body pt-2 pb-1 px-2' style='width: 100%'>
                    <iframe width="100%" height="315" frameborder="0" style="border:0" referrerpolicy="no-referrer-when-downgrade" src={url} allowfullscreen></iframe>
                </div>
                <div class="card-footer pt-2 pb-2 px-2">
                    <a href="https://www.google.com/maps/search/{encoded_query}" target="_blank"><button class="btn btn-secondary btn-lg text-center" style='width: 80%'>SEE MORE...</button></a>
                </div>
            </div>
                """
            
    async def _arun(self, query: str) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("YouTube API does not support async")


class GoogleImageSearchTool(BaseTool):
    name = "Google Images"
    description = "Use this when you want to search for images. The input to this should be a single search term."

    def _run(self, query: str) -> str:
        # URL-encode the query parameter
        encoded_query = quote(query)

        url = 'https://customsearch.googleapis.com/customsearch/v1'
        params = {
            'key': os.environ.get("GOOGLE_SEARCH_API_KEY"),
            'cx': os.environ.get("GOOGLE_SEARCH_ENGINE_ID"),
            'q': encoded_query,
            'searchType': 'image'
        }

        response = requests.get(url, params=params)

        if response.status_code == 200:
            try:
                data = response.json()
                # Parse the data and return the desired value
                results = data['items']

                # Get a random sample of 6 items
                random_items = random.sample(results, 6)

                # Save images to user session
                for idx, item in enumerate(random_items):
                    cl.user_session.set(f"image{idx + 1}", item["link"])

                # Get links for clipboard
                links = []  # Initialise an empty list to hold the links
                for idx, item in enumerate(random_items):
                    links.append(item["link"])  # Append each link to the list

                clipboard = "\n".join(links)

                cl.user_session.set("clipboard", clipboard)

                return "## Here are your images:"

            except JSONDecodeError:
                return "🧑‍🦲 I'm so sorry! I can't find respond to that image search at the moment. Please try again later."
            
    async def _arun(self, query: str) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("Google search API does not support async")


class GoogleSearchTool(BaseTool):
    name = "Google Search"
    description = "Use this when you want to search the internet to answer questions about things you have no knowledge of. The input to this should be a single search term."

    def _run(self, query: str) -> str:
        # URL-encode the query parameter
        encoded_query = quote(query)

        url = 'https://customsearch.googleapis.com/customsearch/v1'
        params = {
            'key': os.environ.get("GOOGLE_SEARCH_API_KEY"),
            'cx': os.environ.get("GOOGLE_SEARCH_ENGINE_ID"),
            'q': encoded_query,
            'dateRestrict': 'm1',
            'safe': 'active'
        }

        response = requests.get(url, params=params)

        if response.status_code == 200:
            try:
                data = response.json()
                results = data['items']

                MAX_ITEMS = 5  # Constant to specify maximum items to be processed
                markdown_items = []

                def extract_image_src(item):
                    if "pagemap" in item:
                        return item["pagemap"]["cse_image"][0]["src"] if "cse_image" in item["pagemap"] and item["pagemap"]["cse_image"] else None
                    return None

                def should_process_item(item):
                    return item['snippet'].count('%20') <= 2

                count = 0
                for item in results:
                    if should_process_item(item):
                        image_src = extract_image_src(item)
                        
                        markdown_items.append(f"### [{item['title']}]({item['link']})")
                        
                        if image_src:
                            markdown_items.append(f"![{item['title']}]({image_src})")
                        
                        markdown_items.append(f"{item['snippet']}\n")
                        
                        count += 1

                    if count == MAX_ITEMS:
                        break

                markdown_output = f"## {query} Search Results\n{markdown_items}\n___\nSee more results [here](https://www.google.com/search?q={encoded_query}&dateRestrict=m1&safe=active)"

                # Create text items for clipboard
                text_items = []

                def should_process_item(item):
                    return item['snippet'].count('%20') <= 2

                count2 = 0
                for item in results:
                    if should_process_item(item):
                        text_item = f"{item['title']}\n{item['snippet']}\nSource: {item['link']}\n"
                        
                        text_items.append(text_item)
                        
                        count2 += 1

                    if count2 == MAX_ITEMS:
                        break

                # Join them all to get a single string if needed
                clipboard = '\n'.join(text_items)


                cl.user_session.set("clipboard", clipboard)

                return markdown_output

            except JSONDecodeError:
                return "🧑‍🦲 I'm so sorry! I can't find respond to that search at the moment. Please try again later."
            
    async def _arun(self, query: str) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("Google search API does not support async")

class SpotifySearchTool(BaseTool):
    name = "Spotify Search"
    description = "Use this when you want to search for music. The input to this should be a single search term."

    def get_spotify_access_token(self):
        data = {
            "grant_type": "client_credentials",
            "client_id": os.environ.get("SPOTIFY_CLIENT_ID"),
            "client_secret": os.environ.get("SPOTIFY_CLIENT_SECRET"),
        }
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }
        response = requests.post(os.environ.get("SPOTIFY_TOKEN_URL"), data=data, headers=headers)
        response.raise_for_status()
        return response.json()["access_token"]


    def get_playlist_url(self, query: str, access_token: str):
        # URL-encode the query parameter
        encoded_query = quote(query)
        headers = {
            "Authorization": f"Bearer {access_token}",
        }
        params = {
            "q": encoded_query,
            "type": "playlist",
        }
        response = requests.get(os.environ.get("SPOTIFY_SEARCH_URL"), headers=headers, params=params)
        response.raise_for_status()
        items = response.json()["playlists"]["items"]
        for item in items:
            if item["owner"]["display_name"] == "Spotify":
                return item["external_urls"]["spotify"]
        return None

    def _run(self, query: str) -> str:
        # URL-encode the query parameter
        access_token = self.get_spotify_access_token()
        playlist_url = self.get_playlist_url(query, access_token)

        if not playlist_url:
            return f"I'm sorry! I couldn't find any music when I searched for {query} 🧑‍🦲"

        params = {
            "url": playlist_url,
        }
        response = requests.get(os.environ.get("SPOTIFY_EMBED_URL"), params=params)
        response.raise_for_status()
        html_data = response.json()["html"]

        # Remove escape characters by loading the string as a JSON object
        unescaped_html_data = html_data.replace('\\', '')

        html_content = f"""<div class="spotifyMusicAnswer">{unescaped_html_data}</div>"""
        return html_content
    
    async def _arun(self, query: str) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("Spotify search API does not support async")
            

class TMDBSearchTool(BaseTool):
    name = "Movie & TV Search"
    description = "Use this when you want to search for movies, tv shows or actors. The input to this should be a single search term."

    def generate_known_for_images(self, known_for):
        images = []
        for item in known_for:
            title = item.get("title", item.get("name", "Unknown"))
            img_md = f"![{title}](https://image.tmdb.org/t/p/w600_and_h900_bestv2/{item['poster_path']})"
            images.append(img_md)
        return "\n\n".join(images)

    def _run(self, query: str) -> str:
        url = 'https://api.themoviedb.org/3/search/multi?'
        params = {
            'query': query,
            'api_key': os.environ.get("TMDB_API_KEY")
        }

        response = requests.get(url, params=params)

        if response.status_code == 200:
            try:
                data = response.json()
                results = data['results']

                if not results:
                    return "I'm so sorry! I can't find that at the moment. Please try again later 🧑‍🦲"

                first_item = results[0]

                if first_item["media_type"] == "person":
                    id = first_item["id"]
                    name = first_item["name"]
                    url_name = first_item["name"].replace(" ", "-")
                    image = first_item["profile_path"]
                    known_for = first_item["known_for"]
                    known_for_images = self.generate_known_for_images(known_for)

                    markdown_output = f"## {name}\n![{name}](https://image.tmdb.org/t/p/w600_and_h900_bestv2/{image})\n___\n### Known for:\n{known_for_images}\n\nSee info more [here](https://www.themoviedb.org/person/{id}-{url_name})"

                    clipboard = f"{name}\nSource: https://www.themoviedb.org/person/{id}-{url_name}"

                    cl.user_session.set("clipboard", clipboard)

                elif first_item["media_type"] == "movie":
                    id = first_item["id"]
                    name = first_item["title"]
                    url_name = first_item["title"].replace(" ", "-")
                    overview = first_item["overview"]
                    image = first_item["poster_path"]
                    release_date = first_item["release_date"]
                    date_obj = datetime.strptime(release_date, "%Y-%m-%d")
                    formatted_date = date_obj.strftime("%-dth %B %Y")
                    rating = first_item["vote_average"]
                    formatted_rating = "{:.1f}".format(round(rating, 1))

                    markdown_output = f"## {name}\n![{name}](https://image.tmdb.org/t/p/w600_and_h900_bestv2/{image})\n**RELEASE DATE**: {formatted_date}\n**TMDB RATING**: {formatted_rating}\n**Overview:** {overview}\n\nSee info more [here](https://www.themoviedb.org/movie/{id}-{url_name})"

                    clipboard = f"{name}\n{overview}\nRelease Date: {formatted_date}\nTMDB Rating: {formatted_rating}\nSource: https://www.themoviedb.org/movie/{id}-{url_name}"

                    cl.user_session.set("clipboard", clipboard)

                elif first_item["media_type"] == "tv":
                    id = first_item["id"]
                    name = first_item["name"]
                    url_name = first_item["name"].replace(" ", "-")
                    overview = first_item["overview"]
                    image = first_item["poster_path"]
                    release_date = first_item["first_air_date"]
                    date_obj = datetime.strptime(release_date, "%Y-%m-%d")
                    formatted_date = date_obj.strftime("%-dth %B %Y")
                    rating = first_item["vote_average"]
                    formatted_rating = "{:.1f}".format(round(rating, 1))

                    markdown_output = f"## {name}\n![{name}](https://image.tmdb.org/t/p/w600_and_h900_bestv2/{image})\n**RELEASE DATE**: {formatted_date}\n**TMDB RATING**: {formatted_rating}\n**Overview:** {overview}\n\nSee info more [here](https://www.themoviedb.org/tv/{id}-{url_name})"

                    clipboard = f"{name}\n{overview}\nRelease Date: {formatted_date}\nTMDB Rating: {formatted_rating}\nSource: https://www.themoviedb.org/movie/{id}-{url_name}"

                    cl.user_session.set("clipboard", clipboard)

                return markdown_output

            except JSONDecodeError:
                return "I'm so sorry! I can't find that at the moment. Please try again later 🧑‍🦲"
            
    async def _arun(self, query: str) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("Google search API does not support async")