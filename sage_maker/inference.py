import tensorflow as tf
import json
import io
from pydub import AudioSegment


SAMPLE_RATE = 32000
F_MIN = 0
F_MAX = 12000

def _compute_mfccs(audio):
    hop_lenght = int(audio.shape[1] / 128)
    stft = tf.signal.stft(audio, 1024, hop_lenght)
    
    spectrograms = tf.abs(stft)
    
    num_spectrogram_bins = stft.shape[-1]
    lower_edge_hertz, upper_edge_hertz, num_mel_bins = 500, 12500, 48 
    linear_to_mel_weight_matrix = tf.signal.linear_to_mel_weight_matrix(
        num_mel_bins, num_spectrogram_bins, SAMPLE_RATE, lower_edge_hertz,
        upper_edge_hertz)
    
    mel_spectrograms = tf.tensordot(
        spectrograms, linear_to_mel_weight_matrix, 1)
    mel_spectrograms.set_shape(spectrograms.shape[:-1].concatenate(
        linear_to_mel_weight_matrix.shape[-1:]))
    
    log_mel_spectrograms = tf.math.log(mel_spectrograms + 1e-6)

    mfccs = tf.signal.mfccs_from_log_mel_spectrograms(log_mel_spectrograms)
    mfccs = mfccs - tf.reduce_min(mfccs)
    mfccs = mfccs / tf.reduce_max(mfccs)
    return mfccs


def _format_response(message, status_code):
    return {
        'statusCode': str(status_code),
        'body': json.dumps(message),
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
            }
        }

def handler(data, context):
    audio = json.loads(data)['body']
    audio = json.loads(audio)
    audio = tf.constant(audio, dtype=tf.float32)
    audio = tf.reshape(audio, (1, audio.shape[0]))
    audio = audio[:,:SAMPLE_RATE*5]
    processed_img = _compute_mfccs(audio)[0]
    processed_img = tf.reshape(processed_img, (processed_img.shape[0], processed_img.shape[1], 1))
    processed_img = tf.image.resize_with_crop_or_pad(processed_img, 128, 48)
    data = [processed_img.numpy().tolist()]
    return _format_response(data, 200)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    