import sys
import os
import re
from pydub import AudioSegment
from pathlib import Path
import music_tag

# Define necessary constants
NUMBER_ALLOWED_ARGUMENTS = 3;

# ChartMetadata class definition
class ChartMetadata:
    def __init__(self, file_path):
        self.file_path = file_path
        self.metadata = self._extract_metadata()

    def _extract_metadata(self):
        metadata = {}
        with open(self.file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            
            # Extracting title
            title_match = re.search(r'#TITLE:(.*?);', content)
            if title_match:
                metadata['title'] = title_match.group(1).strip()
            else:
                title_match = re.search(r'#TITLE:(.*?);', content)
                if title_match:
                    metadata['title'] = title_match.group(1).strip()
            
            # Extracting artist
            artist_match = re.search(r'#ARTIST:(.*?);', content)
            if artist_match:
                metadata['artist'] = artist_match.group(1).strip()
            else:
                artist_match = re.search(r'#ARTIST:(.*?);', content)
                if artist_match:
                    metadata['artist'] = artist_match.group(1).strip()

            # Extracting jacket image
            jacket_match = re.search(r'#JACKET:(.*?);', content)
            if jacket_match:
                metadata['jacket'] = jacket_match.group(1).strip()
            else:
                jacket_match = re.search(r'#JACKET:(.*?);', content)
                if jacket_match:
                    metadata['jacket'] = jacket_match.group(1).strip()
        
        return metadata

    def get_song_title(self):
        return self.metadata.get('title', 'Unknown Title')

    def get_song_artist(self):
        return self.metadata.get('artist', 'Unknown Artist')

    def get_song_jacket(self):
        jacket = self.metadata.get('jacket', 'Unknown Jacket')
        if jacket != 'Unknown Jacket':
            return os.path.join(os.path.dirname(self.file_path), jacket)
        return jacket


# Check for an appropriate number of arguments
argument_count = len(sys.argv)

if (argument_count != NUMBER_ALLOWED_ARGUMENTS):
    print("Error: Incorrect number of arguments supplied (Expected " 
          + str(NUMBER_ALLOWED_ARGUMENTS) 
          + ", received " 
          + str(argument_count)
          + ").", file=sys.stderr)
    exit(1)
    
# Check if the second argument is a valid directory
input_directory = sys.argv[1]
destination_directory = sys.argv[2]
directory_contents = []

try:
    directory_contents = os.listdir(input_directory)
except:
    print("Error: directory '" 
          + input_directory 
          + "' could not be found.", file = sys.stderr)
    exit(1)
    
# Convert all chart folders to .mp3 files with metadata and place them in the destination folder
for directory_item in directory_contents:
    # Check that the next directory item is a directory
    directory_item_contents = []
    audio_filepath = None
    chart_filepath = None

    try:
        directory_item_contents = os.listdir(input_directory + "/" + directory_item)
    except:
        print(directory_item + " is not a directory, moving to the next file.")
    else:
        # Search the directory for the necessary files
        for chart_directory_item in directory_item_contents:
            item_filepath = input_directory + "/" + directory_item + "/" + chart_directory_item
            if (".ogg" in chart_directory_item):
                audio_filepath = item_filepath
            elif (".ssc" in chart_directory_item):
                chart_filepath = item_filepath

    # Convert song to a .mp3 file
    if (audio_filepath != None):
        original_audio = AudioSegment.from_ogg(audio_filepath)
        audio_filename = Path(audio_filepath).stem
        print("Current Audio File: " + audio_filename)

        # Export converted audio to destination filepath
        converted_audio_filepath = destination_directory + "/" + audio_filename + ".mp3"
        original_audio.export(converted_audio_filepath, format="mp3")

        # Perform necessary metadata editions
        chart = ChartMetadata(chart_filepath)
        converted_audio = music_tag.load_file(converted_audio_filepath)
        converted_audio["title"] = str(chart.get_song_title())
        converted_audio["artist"] = str(chart.get_song_artist())
        try:
            converted_audio["artwork"] = open(chart.get_song_jacket(), "rb").read()
        except:
            print("Unable to convert image for " 
                  + chart_filepath 
                  + ", moving on to the next folder.", file=sys.stderr)
        converted_audio.save()