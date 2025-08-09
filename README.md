# Daily Podcast Generator

This project automatically generates a daily podcast from top Reddit posts using the Podcastfy library.

## How it Works

1. Every day at 8 AM UTC, the GitHub Action will run.
2. It fetches the top posts from the specified subreddit.
3. It generates a transcript from these posts.
4. It uses Podcastfy to convert the transcript to audio.
5. The resulting MP3 file is saved as a GitHub Action artifact.

## Setup

To get this project running, you need to set up repository secrets.

1. In your GitHub repository, go to `Settings` > `Secrets and variables` > `Actions`.
2. Click on `New repository secret`.
3. Create the following secrets:
   - **Name:** `SUBREDDIT`
     **Value:** The name of the subreddit you want to get posts from (e.g., `technology`).
   - **Name:** `VOICE_TYPE`
     **Value:** The voice to use for the podcast. You can choose from the voices available in the Podcastfy library (e.g., `default`).

## Usage & Testing

You can let the podcast be generated automatically on schedule, or you can trigger it manually.

1. In your repository, go to the `Actions` tab.
2. You should see the "Generate Daily Podcast" workflow.
3. Click on it, then click `Run workflow` to test it manually.
4. Wait for the workflow to complete (this may take a few minutes).
5. If successful, you'll see an artifact named "daily-podcast" in the workflow summary.
6. Click on the artifact to download the generated MP3 file.

## Customization

You can customize the podcast in several ways:

- **Change the subreddit:** Update the `SUBREDDIT` secret in your repository settings.
- **Change the voice:** Update the `VOICE_TYPE` secret with a different voice.
- **Modify the transcript:** Edit the `src/generate_podcast.py` file to change the format or content of the transcript.

## Set Up Distribution (Optional)

To automatically upload your podcast to a hosting service (like Anchor.fm, Spotify for Podcasters, etc.), you can extend the GitHub Actions workflow.

1. Get API credentials from your podcast hosting service.
2. Add these credentials as new repository secrets.
3. Modify the `.github/workflows/daily-podcast.yml` file to include an upload step using a relevant GitHub Action or a custom script.

## Enjoy Your Automated Podcast!

Your podcast will now be generated automatically every day. Enjoy your daily dose of content!
