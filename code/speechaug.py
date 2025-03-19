import sys
import os
import random
import numpy as np
from pydub import AudioSegment
from pydub.generators import WhiteNoise, PinkNoise, BrownNoise

def add_noise(audio, noise_type, noise_level):
    duration_ms = len(audio)
    try:
        if noise_type == 'white':
            noise = WhiteNoise().to_audio_segment(duration=duration_ms)
        elif noise_type == 'pink':
            noise = PinkNoise().to_audio_segment(duration=duration_ms)
        elif noise_type == 'brown':
            noise = BrownNoise().to_audio_segment(duration=duration_ms)
        else:
            raise ValueError(f"Invalid noise type: {noise_type}")
        
        if len(audio) == 0:
            return audio
            
        noise = noise - (noise.dBFS - audio.dBFS - noise_level)
        return audio.overlay(noise)
    except Exception as e:
        print(f"Error adding noise: {e}")
        return audio  

def time_stretch(audio, rate):
    try:
        return audio._spawn(audio.raw_data, overrides={
            "frame_rate": int(audio.frame_rate * rate)
        }).set_frame_rate(audio.frame_rate)
    except Exception as e:
        print(f"Error in time stretching: {e}")
        return audio

def pitch_shift(audio, semitones):
    try:
        new_sample_rate = int(audio.frame_rate * (2 ** (semitones / 12)))
        return audio._spawn(audio.raw_data, overrides={
            "frame_rate": new_sample_rate
        }).set_frame_rate(audio.frame_rate)
    except Exception as e:
        print(f"Error in pitch shifting: {e}")
        return audio

def volume_adjust(audio, db_change):
    try:
        return audio + db_change
    except Exception as e:
        print(f"Error adjusting volume: {e}")
        return audio

def reverb_effect(audio, decay=0.5):
    try:
        orig = audio
        echo = audio - 6 
        delay = int(decay * 1000)
        
        silence = AudioSegment.silent(duration=delay)
        echo = silence + echo
        
        result = orig.overlay(echo, position=delay)
        return result
    except Exception as e:
        print(f"Error adding reverb: {e}")
        return audio

def augment_audio(audio):
    augmentations = [
        lambda a: add_noise(a, random.choice(['white', 'pink', 'brown']), random.uniform(-20, -10)),
        lambda a: time_stretch(a, random.uniform(0.9, 1.1)),
        lambda a: pitch_shift(a, random.uniform(-2, 2)),
        lambda a: volume_adjust(a, random.uniform(-3, 3)),
        lambda a: reverb_effect(a, random.uniform(0.1, 0.5))
    ]
    
    num_effects = random.randint(1, 3)
    selected_augmentations = random.sample(augmentations, min(num_effects, len(augmentations)))
    
    result = audio
    for augmentation in selected_augmentations:
        result = augmentation(result)
    
    return result

def main(input_folder, output_folder, num_augmentations):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    processed = 0
    skipped = 0
    valid_extensions = ('.mp3', '.wav', '.flac', '.ogg')
    
    audio_files = [f for f in os.listdir(input_folder) 
                  if os.path.isfile(os.path.join(input_folder, f)) 
                  and f.lower().endswith(valid_extensions)]
    
    total_files = len(audio_files)
    print(f"Found {total_files} audio files to process")
    
    for filename in audio_files:
        try:
            input_path = os.path.join(input_folder, filename)
            file_ext = os.path.splitext(filename)[1].lower()
            
            if file_ext == '.mp3':
                audio = AudioSegment.from_mp3(input_path)
            elif file_ext == '.wav':
                audio = AudioSegment.from_wav(input_path)
            elif file_ext == '.flac':
                audio = AudioSegment.from_file(input_path, "flac")
            elif file_ext == '.ogg':
                audio = AudioSegment.from_ogg(input_path)
            
            base_name = os.path.splitext(filename)[0]
            
            output_path = os.path.join(output_folder, f"{base_name}_original{file_ext}")
            audio.export(output_path, format=file_ext[1:])
            
            for i in range(num_augmentations):
                try:
                    augmented_audio = augment_audio(audio)
                    output_path = os.path.join(output_folder, f"{base_name}_aug_{i+1}{file_ext}")
                    augmented_audio.export(output_path, format=file_ext[1:])
                except Exception as e:
                    print(f"Error creating augmentation {i+1} for {filename}: {e}")
            
            processed += 1
            print(f"Processed: {filename} ({processed}/{total_files})")
            
        except Exception as e:
            print(f"Error processing {filename}: {e}")
            skipped += 1
    
    print(f"\nSummary: {processed} audio files processed, {skipped} skipped")
    print(f"Total augmentations created: {processed * num_augmentations}")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python audio_augment.py <input folder> <output folder> <number of augmented samples per audio>")
        sys.exit(1)
    
    input_folder = sys.argv[1]
    output_folder = sys.argv[2]
    
    try:
        num_augmentations = int(sys.argv[3])
        if num_augmentations <= 0:
            raise ValueError("Number of augmentations must be positive")
    except ValueError as e:
        print(f"Error: {e}")
        print("Number of augmentations must be a positive integer")
        sys.exit(1)
    
    if not os.path.exists(input_folder):
        print(f"Error: Input folder '{input_folder}' does not exist")
        sys.exit(1)
    
    main(input_folder, output_folder, num_augmentations)
