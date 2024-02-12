import os
import numpy as np
import tensorflow as tf
import librosa
import pickle
from tensorflow.keras.layers import Input, Dense
from tensorflow.keras.models import Model

# Function to build the autoencoder model
def build_autoencoder(input_dim):
    input_data = Input(shape=(input_dim,))
    encoded = Dense(64, activation='relu')(input_data)
    decoded = Dense(input_dim, activation='sigmoid')(encoded)
    
    autoencoder = Model(input_data, decoded)
    autoencoder.compile(optimizer='adam', loss='mean_squared_error')
    
    return autoencoder

# Function to load audio data from WAV files
def load_wav(file_path, sample_rate=22050):
    audio_data, _ = librosa.load(file_path, sr=sample_rate)
    return audio_data

# Function to preprocess audio data
def preprocess_audio_data(file_paths):
    audio_data = []
    max_len = 0
    
    for file_path in file_paths:
        data = load_wav(file_path)
        audio_data.append(data)
        if len(data) > max_len:
            max_len = len(data)
    
    # Padding to ensure consistent length
    audio_data_padded = [np.pad(data, (0, max_len - len(data))) for data in audio_data]
    return np.array(audio_data_padded)

# Load noisy WAV files
noisy_folder = r"C:\Users\dd53448\Downloads\NEW_AI\NEW_AI\Audacity\out_noise_Beep"
noisy_files = [os.path.join(noisy_folder, f) for f in os.listdir(noisy_folder) if f.endswith('.wav')]
noisy_data = preprocess_audio_data(noisy_files)

# Load noiseless WAV file
clean_file = r"C:\Users\dd53448\Downloads\NEW_AI\NEW_AI\Audacity\without_noise_beep_9\Without_noise_Beep_9.wav"
clean_data = load_wav(clean_file)

# Build and train the autoencoder model
input_dim = len(clean_data)
autoencoder = build_autoencoder(input_dim)
autoencoder.fit(noisy_data, clean_data, epochs=50, batch_size=32, shuffle=True)

# Test the autoencoder model
test_noisy_file = "/content/drive/MyDrive/test_noisy.wav"
test_noisy_data = load_wav(test_noisy_file)
cleaned_sample = autoencoder.predict(test_noisy_data.reshape(1, -1))

print("\nCleaned sample:")
print(cleaned_sample)

# Save the trained model to a pickle file
with open("/content/drive/MyDrive/autoencoder_model.pkl", "wb") as file:
    pickle.dump(autoencoder, file)
