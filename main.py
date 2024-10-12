from youtube_scraper import main
from twitter_thread_prompt import create_twitter_thread_prompt
from openai_module import get_openai_completion
from email_sender import send_daily_digest
import pandas as pd

if __name__ == "__main__":
    # youtube_handles = ['backstagewithmillionaires', 'mreflow']
    youtube_handles = ['tahirmajithia', 'rebelagent1223', 'walikhanenglish']
    recent_videos_df = main(youtube_handles, hours=24)

    # Generating the prompt from transcript
    recent_videos_df['twitterThreadPrompt'] = recent_videos_df['videoTranscript'].apply(lambda x: create_twitter_thread_prompt(x))

    # # Generating the thread using OpenAI
    # recent_videos_df['twitterThread'] = recent_videos_df['twitterThreadPrompt'].apply(lambda x: get_openai_completion(x))

    recent_videos_df = pd.read_csv('demodata1.csv')

    # Sending the daily email digest
    send_daily_digest(recent_videos_df, ["mdnishan006@gmail.com", 'mnsn.n006@gmail.com'])
