import json
from moviepy.editor import concatenate_videoclips, AudioFileClip, VideoFileClip
import datetime
from api import openai, giphy
import os

class script():

    def __init__(self, story_topic):
        self.file_path = f'{datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}'
        os.mkdir(self.file_path)
        self.json_file_path = f'{self.file_path}/script.json'
        self.json_data = None
        self.story_topic = story_topic

        # initialize all the APIs from api_keys.json
        with open('api_keys.json', 'r') as f:
            api_keys = json.load(f)

            self.openai = openai(api_keys['openai'])
            self.giphy = giphy(api_keys['giphy'])

    def generate_script(self):
        # Generate the story
        story = self.openai.generate_story(self.story_topic)

        # Convert the story to a JSON object (story is a string in JSON format)
        self.json_data = json.loads(story)
        
    def generate_audio(self):
        # Process each part in the JSON file
        for part in self.json_data:
            text = self.json_data[part]['text']
            self.openai.text_to_speech(f'{self.file_path}/{part}_sound.mp3', text)

            # Update JSON data with the audio file path
            self.json_data[part]['audio'] = f'{self.file_path}/{part}_sound.mp3'

    def generate_video(self):
        # Process each part in the JSON file
        for part in self.json_data:
            if 'gif' in self.json_data[part]:
                # Search Giphy for a GIF matching the topic
                gif_search_term = self.json_data[part]['gif']
                self.giphy.get_gif(f'{self.file_path}/{part}_video.mp4', gif_search_term)

                # Update JSON data with the video file path
                self.json_data[part]['video'] = f'{self.file_path}/{part}_video.mp4'

            elif 'code' in self.json_data[part]:
                pass

    def generate_final_video(self):
        final_clips = []

        for part, content in self.json_data.items():
            audio_clip = AudioFileClip(content['audio'])
            video_clip = VideoFileClip(content['video'])

            # Manually loop video if it's shorter than the audio
            while video_clip.duration < audio_clip.duration:
                video_clip = concatenate_videoclips([video_clip, VideoFileClip(content['video'])])

            # Trim the video to the length of the audio
            video_clip = video_clip.subclip(0, audio_clip.duration)

            # Add the audio to the video
            video_clip = video_clip.set_audio(audio_clip)

            # Add the final clip to the list
            final_clips.append(video_clip)

        # Concatenate all parts
        final_video = concatenate_videoclips(final_clips, method="compose")

        # Write the final video to a file
        output_video_path = f'{self.file_path}/final_video.mp4'
        final_video.write_videofile(output_video_path, codec='libx264', audio_codec='aac')

        # save script.json
        with open(self.json_file_path, 'w') as f:
            json.dump(self.json_data, f, indent=4)
