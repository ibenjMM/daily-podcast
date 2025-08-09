import os
import requests
from datetime import datetime
from gtts import gTTS
from dotenv import load_dotenv
import traceback
import xml.etree.ElementTree as ET
import html
import re
import random

# Load environment variables
load_dotenv()

def get_reddit_posts(subreddit, limit=3):
    """
    Fetch top posts from a subreddit using its RSS feed.
    """
    print(f"Fetching posts from subreddit RSS feed: r/{subreddit}")
    url = f"https://www.reddit.com/r/{subreddit}/top/.rss"
    headers = {'User-agent': 'daily-podcast-bot'}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        ET.register_namespace('atom', 'http://www.w3.org/2005/Atom')
        root = ET.fromstring(response.content)
        posts = []

        for entry in root.findall('{http://www.w3.org/2005/Atom}entry')[:limit]:
            title = entry.find('{http://www.w3.org/2005/Atom}title').text
            url = entry.find('{http://www.w3.org/2005/Atom}link').get('href')

            author_element = entry.find('{http://www.w3.org/2005/Atom}author/{http://www.w3.org/2005/Atom}name')
            author = author_element.text.replace('/u/', '') if author_element is not None else 'Unknown'

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

def clean_text_for_tts(text, post_author):
    """
    Cleans text by removing URLs, markdown, and other non-speech-friendly content.
    """
    # Remove all HTML tags
    text = re.sub('<[^<]+?>', ' ', text)

    # Remove URLs
    text = re.sub(r'http\S+', '', text)

    # Remove boilerplate from Reddit RSS feed content
    submitted_by_str = f"submitted by /u/{post_author}"
    text_start_index = text.lower().find(submitted_by_str)
    if text_start_index != -1:
        text = text[text_start_index + len(submitted_by_str):]

    # Remove markdown links and other common artifacts
    text = text.replace('[link]', '').replace('[comments]', '').strip()

    # Replace markdown for italics/bold with nothing, as we can't control emphasis
    text = text.replace('*', '').replace('_', '').replace('`', '')

    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()

    return text

def generate_daily_podcast():
    """
    Generate a more natural and engaging daily podcast from top Reddit posts.
    """
    print("--- Starting Enhanced Podcast Generation ---")
    subreddit = os.getenv('SUBREDDIT', 'technology')
    print(f"Target subreddit: {subreddit}")
    posts = get_reddit_posts(subreddit, limit=3)

    if not posts:
        print("No posts found. Exiting.")
        return

    # --- Host Persona and Script Elements ---
    host_intros = [
        f"Hello and welcome to the Daily {subreddit.capitalize()} Briefing! I'm your host, Jules, and we've got some fascinating stories for you today.",
        f"Good morning, tech enthusiasts, and welcome to your daily dose of {subreddit.capitalize()} news. I'm Jules, and here's what's making headlines.",
        f"Welcome back to the Daily {subreddit.capitalize()} Podcast. It's {datetime.now().strftime('%A, %B %d')}, and we're ready to dive into the latest updates. Let's get started.",
    ]

    transitions = [
        "Alright, moving on to our next story...",
        "In other news...",
        "Next up, we have a story about...",
        "Let's shift gears and talk about...",
    ]

    outros = [
        "And that's all the time we have for today. Thanks for tuning in to the Daily Podcast.",
        "That wraps up our briefing for today. I'm Jules, thanks for listening.",
        "And that's a wrap! We'll be back tomorrow with more of the latest news.",
    ]

    ctas = [
        "Be sure to subscribe for more daily updates, and check out the links to these stories in the description. Talk to you tomorrow!",
        "Don't forget to follow our podcast for your daily tech news fix. All links are in the show notes. See you next time!",
        "For more details on today's topics, check the links in the description. Thanks again for listening, and have a great day!",
    ]

    # --- Building the Transcript ---
    print("Creating enhanced transcript...")

    # Intro
    transcript_parts = [random.choice(host_intros) + " ... \n\n"]

    # Teaser
    transcript_parts.append("Coming up on today's show: ...\n")
    for post in posts:
        transcript_parts.append(f"{post['title']}. ...\n")
    transcript_parts.append("\nStay tuned for the details. ...\n\n")

    # Stories with transitions
    for i, post in enumerate(posts):
        if i > 0:
            transcript_parts.append(f"{random.choice(transitions)} ...\n\n")

        transcript_parts.append(f"Our {'first' if i == 0 else 'next'} story is titled: {post['title']}. ...\n\n")

        if post['selftext']:
            clean_content = clean_text_for_tts(post['selftext'], post['author'])
            if len(clean_content) > 30: # Only add content if it's substantial
                transcript_parts.append(f"{clean_content[:800]} ...\n\n")

    # Outro and Call to Action
    transcript_parts.append(random.choice(outros) + " ...\n")
    transcript_parts.append(random.choice(ctas) + "\n")

    final_transcript = "".join(transcript_parts)
    print(f"Transcript created. Length: {len(final_transcript)} characters.")

    transcript_file = f"transcript_{datetime.now().strftime('%Y%m%d')}.txt"
    print(f"Saving transcript to: {os.path.abspath(transcript_file)}")
    with open(transcript_file, 'w', encoding='utf-8') as f:
        f.write(final_transcript)
    print("Transcript saved successfully.")

    output_file = f"daily_podcast_{datetime.now().strftime('%Y%m%d')}.mp3"
    print(f"Attempting to generate podcast audio file with gTTS at: {os.path.abspath(output_file)}")

    try:
        tts = gTTS(text=final_transcript, lang='en', slow=False)
        tts.save(output_file)

        if os.path.exists(output_file):
            print(f"SUCCESS: Podcast generated and saved at: {output_file}")
            return output_file
        else:
            print("FAILURE: gTTS did not create the output file.")
            return None
    except Exception as e:
        print(f"FATAL ERROR: An exception occurred while generating podcast with gTTS: {e}")
        print("--- Traceback ---")
        traceback.print_exc()
        print("-----------------")
        return None

if __name__ == "__main__":
    generate_daily_podcast()
    print("--- Podcast Generation Script Finished ---")
