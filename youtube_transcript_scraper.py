from youtube_transcript_api import YouTubeTranscriptApi as ytt
import pandas as pd
import scrapetube
from pytube import YouTube
import datetime
import sys

def text_from_transcript(transcript):
    txt = ''
    for entry in transcript:
        txt += entry['text'] + ' '
    return txt

date_string = sys.argv[1]

try:
    end_date = datetime.datetime.strptime(date_string, '%Y-%m-%d')
    print(f'Scraping to {end_date.strftime("%Y-%m-%d")}')
except ValueError:
    print('Invalid date format. Please enter the date in YYYY-MM-DD format.')
    quit()

yt_news_df = pd.DataFrame(columns=['video_id', 'publish_date', 'title', 'source', 'description', 'text'])

channel_ids = {
    'ABC News': 'UCBi2mrWuNuyYy4gbM6fU18Q',
    'CNN': 'UC8p1vwvWtl6T73JiExfWs1g',
    'BBC News': 'UC16niRr50-MSBwiO3YDb3RA',
    'Fox News': 'UCXIJgqnII2ZOINSWNOGFThA'
}

for channel_name, channel_id in channel_ids.items():
    print(f'Scraping {channel_name}')

    videos = scrapetube.get_channel(channel_id, sort_by='newest')

    vids_scraped = 0
    failures = 0

    for vid in videos:
        vid_id = vid['videoId']

        try:
            vid_transcript = ytt.get_transcript(vid_id)
            yt_video = YouTube(f"https://www.youtube.com/watch?v={vid_id}")
        except:
            failures += 1
            continue

        vid_date = yt_video.publish_date
        if vid_date < end_date:
            break

        vid_text = text_from_transcript(vid_transcript)
        vid_title = vid['title']['runs'][0]['text']
        vid_description = vid['descriptionSnippet']['runs'][0]['text']

        vid_dict = {
            'video_id': vid_id,
            'publish_date': vid_date,
            'title': vid_title,
            'source': channel_name,
            'description': vid_description,
            'text': vid_text
        }

        yt_news_df = pd.concat([yt_news_df, pd.DataFrame([vid_dict])], ignore_index=True)

        vids_scraped += 1


    print(f'Videos Scraped: {vids_scraped}\nScrapes Failed: {failures}\n')


yt_news_df.to_csv('youtube_news_transcripts.csv', index=False)