import sys
import logging
from youtube_scraper import main as youtube_main
from twitter_thread_prompt import create_twitter_thread_prompt
from openai_module import get_openai_completion
from email_sender import send_daily_digest
import pandas as pd

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    try:
        logging.info("Script started")

        youtube_handles = ['tahirmajithia', 'rebelagent1223', 'walikhanenglish']
        logging.info(f"Fetching videos for handles: {youtube_handles}")

        recent_videos_df = youtube_main(youtube_handles, hours=24)
        logging.info(f"Retrieved {len(recent_videos_df)} videos")

        logging.info("Generating Twitter thread prompts")
        recent_videos_df['twitterThreadPrompt'] = recent_videos_df['videoTranscript'].apply(create_twitter_thread_prompt)

        logging.info("Reading demo data")
        recent_videos_df = pd.read_csv('demodata1.csv')
        logging.info(f"Demo data loaded, shape: {recent_videos_df.shape}")

        logging.info("Sending daily digest")
        send_daily_digest(recent_videos_df, ["mdnishan006@gmail.com", 'mnsn.n006@gmail.com'])

        logging.info("Script completed successfully")

    except FileNotFoundError as e:
        logging.error(f"File not found: {e}")
        sys.exit(1)
    except pd.errors.EmptyDataError:
        logging.error("The CSV file is empty")
        sys.exit(1)
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
