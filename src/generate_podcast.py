import os
import requests
from datetime import datetime
from podcastfy.client import generate_podcast
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_reddit_posts(subreddit, limit=3, time_filter="day"):
    """
    Fetch top posts from a subreddit
    """
    url = f"https://www.reddit.com/r/{subreddit}/top/.json?limit={limit}&t={time_filter}"
    headers = {'User-agent': 'daily-podcast-bot'}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        posts = []
        for post in data['data']['children']:
            post_data = post['data']
            posts.append({
                'title': post_data['title'],
                'url': post_data['url'],
                'selftext': post_data.get('selftext', ''),
                'author': post_data['author']
            })
        return posts
    else:
        print(f"Error fetching posts: {response.status_code}")
        return []

def generate_daily_podcast():
    """
    Generate a daily podcast from top Reddit posts
    """
    # Get top posts from subreddit
    subreddit = os.getenv('SUBREDDIT', 'technology')
    posts = get_reddit_posts(subreddit)

    if not posts:
        print("No posts found. Exiting.")
        return

    # Create a transcript from the posts
    transcript = f"Welcome to the Daily {subreddit.capitalize()} Podcast!\n\n"
    transcript += f"Today is {datetime.now().strftime('%B %d, %Y')}.\n\n"

    for i, post in enumerate(posts, 1):
        transcript += f"Story #{i}: {post['title']}\n"
        if post['selftext']:
            # Limit the selftext to avoid overly long episodes
            transcript += f"{post['selftext'][:500]}...\n\n"
        transcript += f"You can read more at: {post['url']}\n\n"

    transcript += "Thanks for listening to the Daily Podcast. Join us tomorrow for more updates!"

    # Save transcript to a file
    transcript_file = f"transcript_{datetime.now().strftime('%Y%m%d')}.txt"
    with open(transcript_file, 'w') as f:
        f.write(transcript)

    # Generate podcast from transcript
    output_file = f"daily_podcast_{datetime.now().strftime('%Y%m%d')}.mp3"

    # Use Podcastfy to generate the podcast
    try:
        audio_file = generate_podcast(
            content=transcript,
            output_file=output_file,
            voices=os.getenv('VOICE_TYPE', 'default')  # You can customize voices
        )
        print(f"Podcast generated: {audio_file}")
        return audio_file
    except Exception as e:
        print(f"Error generating podcast: {e}")
        return None

if __name__ == "__main__":
    generate_daily_podcast()
