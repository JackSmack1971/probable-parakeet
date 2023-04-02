import os
import whisper
import torch
import json
import datetime
import logging
import argparse
import yaml
from tqdm import tqdm

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

def main(args):
    # Check if GPU is available
    if torch.cuda.is_available():
        device = torch.device("cuda:0")
        logging.info("Using GPU")
    else:
        device = torch.device("cpu")
        logging.info("Using CPU")

    # Load pre-trained model
    if not os.path.exists(args.model):
        raise ValueError(f"Model file {args.model} does not exist")
    logging.info("Loading model...")
    t0 = datetime.datetime.now()
    model = whisper.load_model(args.model)
    t1 = datetime.datetime.now()
    logging.info(f"Model loaded in {t1-t0}")

    # Transcribe audio file
    if not os.path.exists(args.audio):
        raise ValueError(f"Audio file {args.audio} does not exist")
    logging.info("Transcribing audio...")
    t2 = datetime.datetime.now()
    with open(args.audio, "rb") as f:
        output = model.transcribe(f.read(), device=device, progress_hook=tqdm.write)
    t3 = datetime.datetime.now()
    logging.info(f"Transcription completed in {t3-t2}")

    # Save output in specified format
    if args.format == "json":
        output_filename = args.output + ".json"
        with open(output_filename, "w") as f:
            json.dump(output, f)
        logging.info(f"Transcription saved to {output_filename}")
    elif args.format == "text":
        output_filename = args.output + ".txt"
        with open(output_filename, "w") as f:
            f.write(output["text"])
        logging.info(f"Transcription saved to {output_filename}")
    elif args.format == "csv":
        output_filename = args.output + ".csv"
        with open(output_filename, "w") as f:
            f.write("time,word\n")
            for word in output["words"]:
                f.write(f"{word['start']},{word['word']}\n")
        logging.info(f"Transcription saved to {output_filename}")
    else:
        raise ValueError(f"Invalid output format: {args.format}")

def parse_args():
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)

    parser = argparse.ArgumentParser(description='Audio transcription using Whisper')
    parser.add_argument('audio', metavar='audio', type=str, default=config['audio']['file_path'], nargs='?', help='path to input audio file')
    parser.add_argument('model', metavar='model', type=str, default=config['model']['file_path'], nargs='?', help='path to pre-trained model')
    parser.add_argument('output', metavar='output', type=str, default=config['output']['file_path'], nargs='?', help='path to output file (without extension)')
    parser.add_argument('--format', type=str, default=config['output']['format'], choices=['json', 'text', 'csv'],
                        help='output format (default: json)')
    parser.add_argument('--sampling-rate', type=int, default=config['transcription']['sampling_rate'],
                        help='sampling rate of audio file in Hz (default: 16000)')
    parser.add_argument('--language', type=str, default=config['transcription']['language'],
                        help='language code of audio file (default: en)')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    main
