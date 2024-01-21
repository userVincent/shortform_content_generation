from script import script

if __name__ == "__main__":
    story_topic = input("What is the topic of the story?: ")
    script = script(story_topic)
    script.generate_script()
    script.generate_audio()
    script.generate_video()
    script.generate_final_video()
    