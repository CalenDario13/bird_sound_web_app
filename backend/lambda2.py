import json, boto3
from scipy import signal
import numpy as np

TARGET_WIDTH = 514


def lambda_handler(event, context):
    
    
    audio = event
    stft = signal.stft(event, nperseg=22050*5//256)[-1]
    stft = np.abs(stft)
    stft = np.log(stft)
    stft = stft - np.min(stft)
    stft = stft/np.max(stft)
    
    
    
    if stft.shape[1] != TARGET_WIDTH:
        stft = _padding(stft)
    
    stft = stft.reshape(216, TARGET_WIDTH, 1)
    return {
        'statusCode': 200,
        'instances': [stft.tolist()]
        
    }

def _padding(stft):
    num_concat = TARGET_WIDTH//stft.shape[-1] - 1
    new_stft = stft
    for _ in range(num_concat):
        new_stft = np.concatenate((new_stft,stft), axis=1)
        
    padded_stft = np.empty((216, TARGET_WIDTH))
    padded_stft[:new_stft.shape[0], :new_stft.shape[1]] = new_stft
    padded_stft[:, new_stft.shape[1]:] = new_stft[:, :TARGET_WIDTH-new_stft.shape[1]]
    padded_stft = padded_stft - np.min(padded_stft)
    padded_stft = padded_stft/np.max(padded_stft)
    return padded_stft