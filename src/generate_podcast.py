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

def generate_daily_podcast():
    """
    Generate a more natural and engaging daily podcast from top Reddit posts.
    """
    print("--- Starting Super-Enhanced Podcast Generation ---")
    subreddit = os.getenv('SUBREDDIT', 'technology')
    tts_tld = os.getenv('TTS_TLD', 'com') # Default to .com accent
    print(f"Target subreddit: {subreddit}, TTS TLD: {tts_tld}")
    posts = get_reddit_posts(subreddit, limit=3)

    if not posts:
        print("No posts found. Exiting.")
        return

    # --- Expanded Host Persona and Script Elements ---
    host_intros = [
        f"Hello and welcome to the Daily {subreddit.capitalize()} Briefing! I'm your host, Jules, and we've got some fascinating stories lined up for you today.",
        f"Good morning, and welcome to your daily download of {subreddit.capitalize()} news. I'm Jules, and here is what is making headlines today.",
        f"Welcome back to the Daily {subreddit.capitalize()} Podcast. It's {datetime.now().strftime('%A, %B %d')}, and we are ready to dive into the latest updates. So, let's get to it.",
    ]

    transitions = [
        "Alright, moving on to our next story, and this one is a bit of a head-scratcher.",
        "In other news, something I've been following closely...",
        "Next up, let's talk about something completely different.",
        "And to follow up on that, here's a related piece of news.",
        "Let's shift gears for a moment, shall we?",
    ]

    commentary_intros = [
        "Now, my first thought on this is...",
        "You know, this reminds me of...",
        "What a fascinating development. It makes you wonder...",
        "Honestly, I'm not surprised by this at all. Here's why...",
    ]

    commentary_outros = [
        "What do you think? Let me know.",
        "It'll be interesting to see how this plays out.",
        "Definitely something to keep an eye on.",
        "Just some food for thought.",
    ]

    outros = [
        "And that's all the time we have for today. It's been a pleasure bringing you the latest. Thanks for tuning in!",
        "That wraps up our briefing for today. I'm Jules, signing off. Thanks for listening.",
        "And that's a wrap for today's episode! We'll be back tomorrow with more of the latest news.",
    ]

    ctas = [
        "Be sure to subscribe for more daily updates, and check out the links to these stories in the show notes. Talk to you tomorrow!",
        "Don't forget to follow our podcast wherever you're listening. All links are in the description. See you next time!",
        "For more details on today's topics, all the links are waiting for you in the description. Thanks again for listening, and have a wonderful day!",
    ]

    # --- Building the Transcript ---
    print("Creating super-enhanced transcript...")

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
                # Add post-story commentary
                transcript_parts.append(f"{random.choice(commentary_intros)} ... {random.choice(commentary_outros)} ...\n\n")

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
        print("--- Traceback ---")
        traceback.print_exc()
        print("-----------------")
        return None

if __name__ == "__main__":
    generate_daily_podcast()
    print("--- Podcast Generation Script Finished ---")
