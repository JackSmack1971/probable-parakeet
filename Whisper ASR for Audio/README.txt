Name: Whisper Transcriber 

Whisper Transcriber is a Python script that uses the Whisper library to transcribe audio files into text. The script can handle different audio file formats and outputs the transcription in either JSON, text, or CSV format. 

Requirements 

• Python 3 

• Whisper library 

• PyTorch library 

• tqdm library 

Installation 

To install the required libraries, run the following command: 

pip install whisper torch tqdm 

Usage 

The basic usage of Whisper Transcriber is: 

python whisper_transcriber.py audio_file model_file output_file --format [json|text|csv] 

• audio_file: Path to the audio file to transcribe. 

• model_file: Path to the pre-trained model to use for transcription. 

• output_file: Path to the output file (without extension). 

• --format: Output format, default is JSON. Possible values are json, text, and csv. 

For example, to transcribe an audio file named my_audio.wav using a pre-trained model my_model.pt and save the output in JSON format as my_output.json, run the following command: 

python whisper_transcriber.py my_audio.wav my_model.pt my_output --format json 

Options 

Whisper Transcriber supports the following optional arguments: 

• --sampling-rate: Sampling rate of audio file in Hz, default is 16000. 

• --language: Language code of audio file, default is en. 

License 

This script is licensed under the MIT License.
