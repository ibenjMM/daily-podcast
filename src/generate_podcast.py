import os
import requests
from datetime import datetime
from podcastfy.client import generate_podcast
from dotenv import load_dotenv
import traceback
import xml.etree.ElementTree as ET
import html
import re

# Load environment variables
load_dotenv()

def get_reddit_posts(subreddit, limit=3):
    """
    Fetch top posts from a subreddit using its RSS feed.
    """
    print(f"Fetching posts from subreddit RSS feed: r/{subreddit}")
    # The time_filter parameter is not supported by RSS feeds.
    url = f"https://www.reddit.com/r/{subreddit}/top/.rss"
    headers = {'User-agent': 'daily-podcast-bot'}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

        # Register namespace to handle Atom feeds properly
        ET.register_namespace('atom', 'http://www.w3.org/2005/Atom')
        root = ET.fromstring(response.content)
        posts = []

        # Find all 'entry' tags. The namespace is required.
        for entry in root.findall('{http://www.w3.org/2005/Atom}entry')[:limit]:
            title = entry.find('{http://www.w3.org/2005/Atom}title').text
            url = entry.find('{http://www.w3.org/2005/Atom}link').get('href')

            author_element = entry.find('{http://www.w3.org/2005/Atom}author/{http://www.w3.org/2005/Atom}name')
            author = author_element.text if author_element is not None else 'Unknown'

            content_html = entry.find('{http://www.w3.org/2005/Atom}content').text
            selftext = html.unescape(content_html) if content_html else ''

            posts.append({
                'title': title,
                'url': url,
                'selftext': selftext,
                'author': author
            })

        print(f"Successfully fetched and parsed {len(posts)} posts.")
        return posts

    except requests.exceptions.RequestException as e:
        print(f"Error fetching RSS feed: {e}")
        return []
    except ET.ParseError as e:
        print(f"Error parsing XML from RSS feed: {e}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred in get_reddit_posts: {e}")
        traceback.print_exc()
        return []


def generate_daily_podcast():
    """
    Generate a daily podcast from top Reddit posts
    """
    print("--- Starting Podcast Generation ---")
    print(f"Current working directory: {os.getcwd()}")

    subreddit = os.getenv('SUBREDDIT', 'technology')
    print(f"Target subreddit: {subreddit}")
    posts = get_reddit_posts(subreddit, limit=3)

    if not posts:
        print("No posts found. Exiting.")
        return

    print("Creating transcript...")
    transcript = f"Welcome to the Daily {subreddit.capitalize()} Podcast!\n\n"
    transcript += f"Today is {datetime.now().strftime('%B %d, %Y')}.\n\n"

    for i, post in enumerate(posts, 1):
        transcript += f"Story #{i}: {post['title']}\n"
        if post['selftext']:
            # Basic HTML tag stripping
            clean_text = re.sub('<[^<]+?>', ' ', post['selftext'])
            # The content from RSS includes a lot of boilerplate. This is a basic attempt to remove it.
            # It finds the "submitted by" link and tries to only get text after it.
            submitted_by_str = f"submitted by /u/{post['author']}"
            text_start_index = clean_text.lower().find(submitted_by_str)
            if text_start_index != -1:
                clean_text = clean_text[text_start_index + len(submitted_by_str):]

            # Further cleanup
            clean_text = clean_text.replace('[link]', '').replace('[comments]', '').strip()

            transcript += f"{clean_text[:500]}...\n\n"
        transcript += f"You can read more at: {post['url']}\n\n"

    transcript += "Thanks for listening to the Daily Podcast. Join us tomorrow for more updates!"
    print(f"Transcript created. Length: {len(transcript)} characters.")

    transcript_file = f"transcript_{datetime.now().strftime('%Y%m%d')}.txt"
    print(f"Saving transcript to: {os.path.abspath(transcript_file)}")
    with open(transcript_file, 'w', encoding='utf-8') as f:
        f.write(transcript)
    print("Transcript saved successfully.")

    output_file = f"daily_podcast_{datetime.now().strftime('%Y%m%d')}.mp3"
    print(f"Attempting to generate podcast audio file at: {os.path.abspath(output_file)}")

    try:
        audio_file = generate_podcast(
            content=transcript,
            output_file=output_file,
            voices=os.getenv('VOICE_TYPE', 'default')
        )
        if audio_file and os.path.exists(audio_file):
            print(f"SUCCESS: Podcast generated and saved at: {audio_file}")
            return audio_file
        else:
            print("FAILURE: generate_podcast function did not return a valid file path or the file was not created.")
            return None
    except Exception as e:
        print(f"FATAL ERROR: An exception occurred while generating podcast: {e}")
        print("--- Traceback ---")
        traceback.print_exc()
        print("-----------------")
        return None

if __name__ == "__main__":
    generate_daily_podcast()
    print("--- Podcast Generation Script Finished ---")
