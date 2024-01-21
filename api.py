from openai import OpenAI
import requests
from moviepy.editor import VideoFileClip
import os
import tempfile

class openai():

    def __init__(self, api_key, model='gpt-4', audio_model='tts-1'):
        self.api_key = api_key
        self.client = OpenAI(api_key=self.api_key)
        self.model = model
        self.audio_model = audio_model
                     
    """
    Generates a story based on a given prompt and a corresponding gif for each part of the story.

    :param story_prompt: The prompt for creating the story.	

    :return: The generated story in string format.
    """   
    def generate_story(self, story_topic):
        # add extra information to the story prompt
        #story_prompt = f'Create a shortform video script about the following topic: {story_topic}\nONLY return a response of the following type: it should be a json object with key part, each part should have a text and either a value of gif or code not both, the gif should be a search term for a gif fitting with the story, the code should be a piece of code as an example or explanation of the story. \nHere is a very simple example \n\n "part1": "text": "C has also influenced many other popular programming languages.", "gif": "Influence on programming languages" or "part2": "text": "Lets see a practical example of C in action. This is code does ...", "code": "some c code ...".\n'
        story_prompt = f'Create a shortform video script about the following topic: {story_topic}\n \
                        ONLY return a response of the following type: it should be a json object where the key is the part, \
                        each part should have a text and a value of gif, the gif should be a search term for a gif fitting with the story \
                        and it should be meme like so keep the search terms simple. \n \
                        Here is a very simple example \n\n "part1": "text": "C has also influenced many other popular programming languages.", "gif": "Influence on programming languages"\n'

        # Generate the story
        story_response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": story_prompt}],
        )
        story = story_response.choices[0].message.content

        return story
    
    """
    Generates a voiceover from text using OpenAI's API.

    :param file_path: The path to save the audio file to.
    :param text: The text to generate a voiceover from.

    :return: True if the audio file was generated successfully, False otherwise.
    """
    def text_to_speech(self, file_path, text):
        response = self.client.audio.speech.create(
            model=self.audio_model,
            voice='alloy',
            input=text
        )

        # save the audio file
        response.stream_to_file(file_path)

        return True

class giphy():

    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = 'http://api.giphy.com/v1/gifs/search'

    """
    Downloads a GIF from Giphy based on a given keyword.

    :param keyword: The keyword to search for GIFs.
    :param file_path: The path to save the GIF to.

    :return: True if the GIF was downloaded successfully, False otherwise.
    """
    def get_gif(self, file_path, keyword):
        params = {'api_key': self.api_key, 'q': keyword, 'limit': 1}
        response = requests.get(self.base_url, params=params)

        if response.status_code == 200:
            data = response.json().get('data')
            if data:
                gif_url = data[0]['images']['original']['url']

                gif_response = requests.get(gif_url)
                if gif_response.status_code == 200:
                    # Use a temporary file
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.gif') as file:
                        file.write(gif_response.content)
                        gif_filename = file.name

                    clip = VideoFileClip(gif_filename)
                    # save the mp4 file
                    clip.write_videofile(file_path, codec='libx264', audio=False)
                    # Clean up the temporary GIF file
                    os.remove(gif_filename)

                    return True
        else:
            print(f"Error: Unable to download GIF for keyword '{keyword}'. Status Code: {response.status_code}")
            return False
        