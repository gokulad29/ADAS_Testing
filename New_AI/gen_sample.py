import os
import librosa
import numpy as np
import soundfile as sf
# Set the path to the directory containing the audio files
audio_dir = r"D:\NEW_AI\Audacity\in_noise_beep"

# Set the output directory for augmented audio files
output_dir = r"D:\NEW_AI\Audacity\out_noise_Beep_9"

# Set the augmentation parameters
time_stretch_factors = [0.8, 1.2]  # Time stretch factors
pitch_shift_steps = [-2, 2]  # Pitch shift steps in semitones
noise_factor = 0.05  # Noise factor

# Ensure the output directory exists
os.makedirs(output_dir, exist_ok=True)

# Iterate over the audio files in the input directory
for filename in os.listdir(audio_dir):
    if filename.endswith(".wav"):
        file_path = os.path.join(audio_dir, filename)

        # Load the audio file
        audio, sr = librosa.load(file_path, sr=None)
        for i in range(5000):
        # Apply time stretching
            for stretch_factor in time_stretch_factors:
                stretched_audio = librosa.effects.time_stretch(audio,rate=stretch_factor)

                # Save the augmented audio
                output_file = f"time_stretch_{stretch_factor}_{filename}"
                output_path = os.path.join(output_dir, output_file)
                sf.write(output_path, stretched_audio, sr)
                time_stretch_factors[0]+=0.0001
                time_stretch_factors[1]+=0.0001



        # Add noise
        noisy_audio = audio + noise_factor * np.random.randn(len(audio))

        # Save the augmented audio
        output_file = f"noise_{filename}"
        output_path = os.path.join(output_dir, output_file)
        sf.write(output_path, noisy_audio, sr)
