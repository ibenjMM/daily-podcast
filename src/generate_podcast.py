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
import json
import argparse
import sys

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
            posts.append({'title': title, 'url': url, 'selftext': selftext, 'author': author})
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
    text = re.sub('<[^<]+?>', ' ', text)
    text = re.sub(r'http\S+', '', text)
    submitted_by_str = f"submitted by /u/{post_author}"
    text_start_index = text.lower().find(submitted_by_str)
    if text_start_index != -1:
        text = text[text_start_index + len(submitted_by_str):]
    text = text.replace('[link]', '').replace('[comments]', '').strip()
    text = text.replace('*', '').replace('_', '').replace('`', '')
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def generate_daily_podcast(show_config):
    """
    Generate a more natural and engaging daily podcast based on a show configuration.
    """
    show_name = show_config['name']
    subreddit = show_config['subreddit']
    tts_tld = show_config.get('tts_tld', 'com') # Default to 'com' if not specified

    print(f"--- Starting Podcast Generation for show: '{show_name}' ---")
    print(f"Target subreddit: {subreddit}, TTS TLD: {tts_tld}")
    posts = get_reddit_posts(subreddit, limit=3)

    if not posts:
        print("No posts found. Exiting.")
        return

    # --- Host Persona and Script Elements ---
    host_intros = [
        f"Hello and welcome to {show_name}! I'm your host, Jules, and we've got some fascinating stories lined up for you today.",
        f"Good morning, and welcome to your daily download of news from the world of {subreddit}. I'm Jules, and here is what is making headlines today.",
        f"Welcome back to {show_name}. It's {datetime.now().strftime('%A, %B %d')}, and we're ready to dive into the latest updates. So, let's get to it.",
    ]

    # ... (The rest of the persona lists remain the same)
    transitions = [ "Alright, moving on...", "In other news...", "Next up...", ]
    commentary_intros = [ "Now, my first thought on this is...", "What a fascinating development...", "Honestly, I'm not surprised by this...", ]
    commentary_outros = [ "What do you think?", "It'll be interesting to see how this plays out.", "Definitely something to keep an eye on.", ]
    outros = [ "And that's all the time we have for today. Thanks for tuning in!", "That wraps up our briefing for today. I'm Jules, signing off.", ]
    ctas = [ "Be sure to subscribe for more daily updates. Talk to you tomorrow!", "Don't forget to follow our podcast. All links are in the show notes.", ]

    # --- Building the Transcript ---
    print("Creating enhanced transcript...")
    transcript_parts = [random.choice(host_intros) + " ... \n\n"]
    transcript_parts.append("Coming up on today's show: ...\n")
    for post in posts:
        transcript_parts.append(f"{post['title']}. ...\n")
    transcript_parts.append("\nWe'll dive into the details, right after this. ...\n\n")

    for i, post in enumerate(posts):
        if i > 0:
            transcript_parts.append(f"{random.choice(transitions)} ...\n\n")
        transcript_parts.append(f"Our {'first' if i == 0 else 'next'} story is titled: {post['title']}. ...\n\n")
        if post['selftext']:
            clean_content = clean_text_for_tts(post['selftext'], post['author'])
            if len(clean_content) > 30:
                transcript_parts.append(f"{clean_content[:800]} ...\n\n")
                transcript_parts.append(f"{random.choice(commentary_intros)} ... {random.choice(commentary_outros)} ...\n\n")

    transcript_parts.append(random.choice(outros) + " ...\n")
    transcript_parts.append(random.choice(ctas) + "\n")

    final_transcript = "".join(transcript_parts)

    # --- Saving and Generating Audio ---
    # Sanitize show name for filenames
    safe_show_name = re.sub(r'\W+', '', show_name.replace(' ', '_'))
    output_filename_base = f"{safe_show_name}_{datetime.now().strftime('%Y%m%d')}"

    transcript_file = f"{output_filename_base}.txt"
    print(f"Saving transcript to: {os.path.abspath(transcript_file)}")
    with open(transcript_file, 'w', encoding='utf-8') as f:
        f.write(final_transcript)

    output_file = f"{output_filename_base}.mp3"
    print(f"Attempting to generate podcast audio file with gTTS at: {os.path.abspath(output_file)}")

    try:
        tts = gTTS(text=final_transcript, lang='en', tld=tts_tld, slow=False)
        tts.save(output_file)

        if os.path.exists(output_file):
            print(f"SUCCESS: Podcast generated and saved at: {output_file}")
            return output_file
        else:
            print("FAILURE: gTTS did not create the output file.")
            return None
    except Exception as e:
        print(f"FATAL ERROR: An exception occurred while generating podcast with gTTS: {e}")
        traceback.print_exc()
        return None

def main():
    """
    Main function to load shows, parse arguments, and generate the selected podcast.
    """
    parser = argparse.ArgumentParser(description="Generate a daily podcast from a configured show.")
    parser.add_argument("--show", required=True, help="The name of the show to generate, as defined in shows.json.")
    args = parser.parse_args()

    try:
        with open("shows.json", "r") as f:
            shows = json.load(f)
    except FileNotFoundError:
        print("ERROR: shows.json not found. Please create it.")
        sys.exit(1)
    except json.JSONDecodeError:
        print("ERROR: shows.json is not valid JSON.")
        sys.exit(1)

    show_to_generate = None
    for show in shows:
        if show['name'] == args.show:
            show_to_generate = show
            break

    if show_to_generate:
        generate_daily_podcast(show_to_generate)
    else:
        print(f"ERROR: Show '{args.show}' not found in shows.json.")
        sys.exit(1)

if __name__ == "__main__":
    main()
    print("--- Podcast Generation Script Finished ---")
