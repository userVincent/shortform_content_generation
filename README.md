
# Shortform Content Generation Project

This project automates the creation of shortform multimedia content. It generates a story based on a given topic, 
searches for relevant GIFs, converts them to video format, and combines them with generated audio to create a final video. 
This README will guide you through setting up and running the project.

## Prerequisites

Before you begin, ensure you have the following installed:
- Python 3
- Required Python libraries: `requests`, `moviepy`, and `openai`.

You will also need API keys from the following services:
- OpenAI (for GPT-based story generation)
- Giphy (for GIF searching)
- ElevenLabs (for text-to-speech conversion)

## Setup

1. **Clone the Repository**: First, clone this repository to your local machine.

   ```bash
   git clone https://github.com/userVincent/shortform_content_generation.git
   cd shortform_content_generation
   ```

2. **Install Dependencies**: Install the required Python libraries.

3. **API Keys Configuration**:
   - Create a file named `api_keys.json` in the project root directory.
   - Add your API keys to this file in the following format:

     ```json
     {
         "openai": "your_openai_key",
         "giphy": "your_giphy_key",
         "elevenlabs": "your_elevenlabs_key"
     }
     ```

4. **Running the Project**: To run the project, execute the main script.

   ```bash
   python gen.py
   ```

   When prompted, enter the desired topic for your story:

   ```
   What is the topic of the story?:
   ```

## Output

The program will generate a folder named with the current date in the root directory. This folder will contain:
- All the individual audio and video files.
- The generated script.
- The final combined video.

## Examples

There are two examples I already generated: one about the C programming language and one about Anakin Skywalker. 
The C programming example was created using GPT-3.5 Turbo, while the Anakin example was created with GPT-4. 
Using GPT-4 is how the program is currently set up. It is not perfect, but given the way people are addicted to shortform content nowadays, 
maybe some social media algorithm will pick it up if you upload it.

## Contribution

Feel free to fork this repository and contribute to its development. If you encounter any issues or have suggestions, 
please open an issue or submit a pull request.
