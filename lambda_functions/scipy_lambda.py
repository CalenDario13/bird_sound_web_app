from scipy import signal
from numpy import abs, log, min, max, concatenate, empty

def lambda_handler(event, context):
    
    
    audio = event
    stft = signal.stft(audio, nperseg=22050*5//256)[-1]
    stft = abs(stft)
    stft = log(stft + 1e-6)
    stft = stft - min(stft)
    stft = stft/(max(stft) + 1e-6)
    
    
    if stft.shape[1] != 514:
        stft = _padding(stft)
    
    stft = stft.reshape(216, 514, 1)
    return {
        'statusCode': 200,
        'instances': [stft.tolist()]
        
    }

def _padding(stft):
    num_concat = 514//stft.shape[-1] - 1
    new_stft = stft
    for _ in range(num_concat):
        new_stft = concatenate((new_stft,stft), axis=1)
        
    padded_stft = empty((216, 514))
    padded_stft[:new_stft.shape[0], :new_stft.shape[1]] = new_stft
    padded_stft[:, new_stft.shape[1]:] = new_stft[:, :514 - new_stft.shape[1]]
    padded_stft = padded_stft - min(padded_stft)
    padded_stft = padded_stft/max(padded_stft)
    return padded_stft