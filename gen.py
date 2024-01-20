from openai import OpenAI
import requests
import json
from moviepy.editor import AudioFileClip, VideoFileClip, concatenate_videoclips
import os
import datetime

def generate_story(file_path, story_topic):
    """
    Generates a story based on a given prompt and then asks GPT to create a list of topics
    for searching GIFs related to different parts of the story.

    :param story_prompt: The prompt for creating the story.
    """

    # Create a new OpenAI client, get api key from api_keys.json
    with open('api_keys.json', 'r') as f:
        api_key = json.load(f)['openai']
    client = OpenAI(api_key=api_key)

    # add extra information to the story prompt
    #story_prompt = f'Create a shortform video script about the following topic: {story_topic}\nONLY return a response of the following type: it should be a json object with key part, each part should have a text and either a value of gif or code not both, the gif should be a search term for a gif fitting with the story, the code should be a piece of code as an example or explanation of the story. \nHere is a very simple example \n\n "part1": "text": "C has also influenced many other popular programming languages.", "gif": "Influence on programming languages" or "part2": "text": "Lets see a practical example of C in action. This is code does ...", "code": "some c code ...".\n'
    story_prompt = f'Create a shortform video script about the following topic: {story_topic}\nONLY return a response of the following type: it should be a json object with key part, each part should have a text and a value of gif, the gif should be a search term for a gif fitting with the story and it should be meme like so keep the search terms simple. \nHere is a very simple example \n\n "part1": "text": "C has also influenced many other popular programming languages.", "gif": "Influence on programming languages"\n'

    # Generate the story
    story_response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": story_prompt}],
    )
    story = story_response.choices[0].message.content

    # Save the story to a txt file
    json_file_path = f'{file_path}/story.json'
    with open(json_file_path, 'w') as f:
        f.write(story)

    
def generate_audio(file_path):
    # Read the story from the JSON file
    json_file_path = f'{file_path}/story.json'
    with open(json_file_path, 'r') as f:
        json_data = json.load(f)

    # Process each part in the JSON file
    for part in json_data:
        text = json_data[part]['text']
        output_audio_path = f"{file_path}/{part}_sound.mp3"
        
        # Convert text to speech and save as an MP3 file
        elevenlabs_text_to_speech_from_file(text, output_audio_path)
        
        # Update JSON data with the audio file path
        json_data[part]['audio'] = output_audio_path

    # Save the updated JSON data back to the file
    with open(json_file_path, 'w') as f:
        json.dump(json_data, f, indent=4)

def generate_video(file_path):
    # Read the story from the JSON file
    json_file_path = f'{file_path}/story.json'
    with open(json_file_path, 'r') as f:
        json_data = json.load(f)

    # Process each part in the JSON file
    for part in json_data:
        if 'gif' in json_data[part]:
            # Search Giphy for a GIF matching the topic
            gif_search_term = json_data[part]['gif']
            output_video_path = f"{file_path}/{part}_video.mp4"
            search_and_convert_gif_to_mp4(gif_search_term, output_video_path)

            # Update JSON data with the video file path
            json_data[part]['video'] = output_video_path

        elif 'code' in json_data[part]:
            pass

    # Save the updated JSON data back to the file
    with open(json_file_path, 'w') as f:
        json.dump(json_data, f, indent=4)

def generate_final_video(file_path):
    # Load JSON data
    json_file_path = f'{file_path}/story.json'
    with open(json_file_path, 'r') as file:
        data = json.load(file)

    final_clips = []

    for part, content in data.items():
        audio_path = content['audio']
        video_path = content['video']

        # Load audio and video
        audio_clip = AudioFileClip(audio_path)
        video_clip = VideoFileClip(video_path)

       # Manually loop video if it's shorter than the audio
        while video_clip.duration < audio_clip.duration:
            video_clip = concatenate_videoclips([video_clip, VideoFileClip(video_path)])

        # Trim the video clip to match the audio duration
        video_clip = video_clip.subclip(0, audio_clip.duration)

        # Set the audio of the video clip
        video_clip = video_clip.set_audio(audio_clip)

        final_clips.append(video_clip)

    # Concatenate all parts
    final_video = concatenate_videoclips(final_clips, method="compose")

    # Write the final video to a file
    output_video_path = f'{file_path}/final_video.mp4'
    final_video.write_videofile(output_video_path, codec='libx264', audio_codec='aac')

def elevenlabs_text_to_speech_from_file(text, output_audio_path):
    """
    Generate a voiceover using ElevenLabs API from text in a file.

    :param text: string of text.
    :param output_audio_path: Path to save the generated audio file.
    """
    CHUNK_SIZE = 1024
    
    # Get api key from api_keys.json
    with open('api_keys.json', 'r') as f:
        api_key = json.load(f)['elevenlabs']

    voice_id = 'J38PuyTrfO3nPkVqNQGl'
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": api_key
    }

    try:
        data = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.5
            }
        }

        response = requests.post(url, json=data, headers=headers)

        # Save audio to a file
        with open(output_audio_path, 'wb') as audio_file:
            for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                if chunk:
                    audio_file.write(chunk)

        return True
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

def search_and_convert_gif_to_mp4(keyword, output_video_path):
    """ Search Giphy for GIFs matching a keyword and convert to MP4. """

    # Giphy API Setup
    with open('api_keys.json', 'r') as f:
        api_key = json.load(f)['giphy']
    base_url = 'http://api.giphy.com/v1/gifs/search'

    # Search for GIF
    params = {'api_key': api_key, 'q': keyword, 'limit': 1}
    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        data = response.json()['data']
        if data:
            gif_url = data[0]['images']['original']['url']

            # Download GIF
            gif_response = requests.get(gif_url)
            if gif_response.status_code == 200:
                gif_filename = 'temp_gif.gif'
                with open(gif_filename, 'wb') as file:
                    file.write(gif_response.content)

                # Convert GIF to MP4
                clip = VideoFileClip(gif_filename)
                clip.write_videofile(output_video_path, codec='libx264', audio=False)

                # Clean up the temporary GIF file
                os.remove(gif_filename)

                return True
    return False

if __name__ == "__main__":
    story_topic = input("What is the topic of the story?: ")

    # Create a new folder for the story named the current date and time
    now = datetime.datetime.now()
    file_path = f'{now.strftime("%Y-%m-%d-%H-%M-%S")}'
    os.mkdir(file_path)

    # generate story
    generate_story(file_path, story_topic)

    # Generate audio
    generate_audio(file_path)

    # Generate video
    generate_video(file_path)

    # Generate final video
    generate_final_video(file_path)
