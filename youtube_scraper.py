# youtube_scraper.py

import pandas as pd
from datetime import datetime, timedelta, timezone
import scrapetube
from youtube_transcript_api import YouTubeTranscriptApi
import logging
import requests
from bs4 import BeautifulSoup
import json
import re
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_timedelta(time_str):
    """Convert a time string to a timedelta."""
    if 'hour' in time_str:
        hours = int(time_str.split()[0])
        return timedelta(hours=hours)
    elif 'day' in time_str:
        days = int(time_str.split()[0])
        return timedelta(days=days)
    elif 'week' in time_str:
        weeks = int(time_str.split()[0])
        return timedelta(weeks=weeks)
    elif 'year' in time_str:
        years = int(time_str.split()[0])
        return timedelta(days=years * 365)  # Approximation for years
    else:
        return timedelta.max  # Return a large timedelta for "out of range" cases

def get_recent_videos_for_handle(handle, hours=24):
    """Retrieve recent videos for a specified YouTube handle."""
    try:
        videos = scrapetube.get_channel(channel_username=handle)
    except Exception as e:
        logging.error(f"Failed to retrieve videos for {handle}: {e}")
        return pd.DataFrame()  # Return empty DataFrame on failure

    video_data = []
    
    for video in videos:
        publish_time_str = video['publishedTimeText']['simpleText']
        timedelta_since_publish = get_timedelta(publish_time_str)

        # Stop processing if older than specified hours
        if timedelta_since_publish > timedelta(hours=hours):
            break
        
        video_dict = {
            'videoPublishTime': publish_time_str,
            'videoID': video['videoId'],
            'videoTitle': video['title']['runs'][0]['text']
        }
        video_data.append(video_dict)

    return pd.DataFrame(video_data)

def get_recent_videos_for_handles(handles, hours=24):
    """Retrieve recent videos for multiple YouTube handles."""
    if isinstance(handles, str):
        handles = [handles]
    
    df_list = []
    for handle in handles:
        df = get_recent_videos_for_handle(handle, hours)
        if not df.empty:
            df['handle'] = handle  # Add handle column
            df_list.append(df)
    
    if df_list:
        return pd.concat(df_list, ignore_index=True)
    else:
        return pd.DataFrame()  # Return empty DataFrame if no videos found

def get_video_transcript(video_id):
    """Retrieve the transcript for a specific video ID using web scraping."""
    url = f"https://www.youtube.com/watch?v={video_id}"

    logging.info(f"Started collecting transcripts for {url}")
    
    try:
        # Send a GET request to the YouTube video page
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the script tag containing the transcript data
        scripts = soup.find_all('script')
        transcript_script = next((s for s in scripts if 'captionTracks' in s.text), None)
        
        if not transcript_script:
            return "ERROR: No transcript found for this video"
        
        # Extract the JSON data from the script
        json_data = re.search(r'ytInitialPlayerResponse\s*=\s*({.+?});', transcript_script.string).group(1)
        data = json.loads(json_data)
        
        # Extract the transcript data
        captions = data['captions']['playerCaptionsTracklistRenderer']['captionTracks']
        
        if not captions:
            return "ERROR: No captions available for this video"
        
        # Use the first available caption track (usually the original language)
        caption_url = captions[0]['baseUrl']
        
        # Download the actual transcript data
        transcript_response = requests.get(caption_url)
        transcript_response.raise_for_status()
        
        # Parse the transcript data
        transcript_soup = BeautifulSoup(transcript_response.text, 'html.parser')
        transcript_parts = transcript_soup.find_all('text')
        
        # Combine all parts of the transcript
        full_transcript = ' '.join(part.text for part in transcript_parts)
        
        return full_transcript
    
    except requests.RequestException as e:
        logging.error(f"Network error occurred while retrieving transcript for {video_id}: {str(e)}")
        return f"ERROR: Network error - {str(e)}"
    except json.JSONDecodeError as e:
        logging.error(f"JSON parsing error occurred for {video_id}: {str(e)}")
        return f"ERROR: JSON parsing error - {str(e)}"
    except Exception as e:
        logging.error(f"Failed to retrieve transcript for {video_id}: {str(e)}")
        return f"ERROR: {str(e)}"

def scrape_youtube(youtube_handles, hours=24):
    """Main function to run the video retrieval and transcript collection."""
    recent_videos_df = get_recent_videos_for_handles(youtube_handles, hours)
    
    # Add more detailed logging
    logging.info(f"Retrieved {len(recent_videos_df)} videos")
    
    # Apply transcript retrieval with more information
    def get_transcript_with_info(row):
        logging.info(f"Attempting to retrieve transcript for video {row['videoID']} from {row['handle']}")
        transcript = get_video_transcript(row['videoID'])
        if transcript.startswith("ERROR:"):
            logging.warning(f"Failed to retrieve transcript for {row['videoID']}: {transcript}")
        else:
            logging.info(f"Successfully retrieved transcript for {row['videoID']}")
        return transcript

    recent_videos_df['videoTranscript'] = recent_videos_df.apply(get_transcript_with_info, axis=1)

    logging.info("Completed retrieving recent videos and transcripts.")
    return recent_videos_df
