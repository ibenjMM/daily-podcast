# Multi-Show Podcast Generator

This project automatically generates multiple, distinct daily podcasts from Reddit posts using Google Text-to-Speech. It's designed to be highly customizable, allowing you to create different "shows" for various topics, each with its own style and voice accent.

## How it Works

1.  A GitHub Action runs on a schedule or can be triggered manually.
2.  You specify which "show" to generate.
3.  The script reads the configuration for that show from `src/shows.json`.
4.  It fetches the top posts from the show's specified subreddit using the RSS feed.
5.  A conversational, human-like script is generated, including a host persona, intros, transitions, and commentary.
6.  It uses Google Text-to-Speech (`gTTS`) to convert the transcript to an MP3 audio file.
7.  The resulting MP3 file is saved as a GitHub Action artifact, ready for you to download.

## Setup: Configuring Your Shows

All podcast configuration is done in the `src/shows.json` file. Open this file to define your different podcast shows.

The file is a list of show objects, each with the following properties:
-   `"name"`: The name of your podcast show (e.g., "Tech Today").
-   `"subreddit"`: The subreddit to use as the content source (e.g., "technology").
-   `"tts_tld"`: The Google Text-to-Speech "top-level domain", which controls the voice's accent.

Here is an example configuration for three shows:
```json
[
  {
    "name": "Tech Today",
    "subreddit": "technology",
    "tts_tld": "com"
  },
  {
    "name": "Science Weekly",
    "subreddit": "science",
    "tts_tld": "co.uk"
  },
  {
    "name": "Business Buzz",
    "subreddit": "business",
    "tts_tld": "com.au"
  }
]
```

To add a new show, simply copy one of the objects, paste it, and change the values.

### Choosing a Voice Accent (`tts_tld`)
You can change the host's accent by changing the `tts_tld` value. Here are some popular options:
-   `com`: Standard US English
-   `co.uk`: British English
-   `com.au`: Australian English
-   `ca`: Canadian English
-   `co.in`: Indian English
-   `ie`: Irish English
-   `co.za`: South African English

## Usage & Testing

You can generate a podcast in two ways:

### 1. Manual Generation (Recommended for testing)
1.  In your repository, go to the **Actions** tab.
2.  In the left sidebar, click on the **"Generate Daily Podcast"** workflow.
3.  Click the **"Run workflow"** dropdown button.
4.  You will see an input field labeled **"The name of the show to generate"**. Type the name of the show you want to generate exactly as it appears in `shows.json` (e.g., "Science Weekly").
5.  Click the green **"Run workflow"** button.

### 2. Scheduled Generation
The workflow is scheduled to run every day at 8 AM UTC. By default, it will generate the **"Tech Today"** show. You can change this default in the `.github/workflows/daily-podcast.yml` file.

After a workflow run is complete, you can download the generated MP3 file from the "Artifacts" section of the workflow summary page.

## Customization
Beyond `shows.json`, you can customize the host's personality by editing the lists of phrases (e.g., `host_intros`, `transitions`, `commentary_intros`) at the top of the `generate_daily_podcast` function in `src/generate_podcast.py`.
