import json, boto3, base64, io
from pydub import AudioSegment


SR = 32000
SIGNAL_LENGTH = 5 
SPEC_SHAPE = (48, 128) 
FMIN = 500
FMAX = 12500
HOP_LENGHT = int(SIGNAL_LENGTH * SR / (SPEC_SHAPE[1] - 1))
DURATION  = SR*15
endpoint = 'tensorflow-inference-2021-07-18-17-35-20-866'


class_id = {1:'amerob',2:'gnwwere1',3:'grekis', 4:'houspa',5:'mallar', 6:'redcro'}

def format_response(message, status_code):
    return {
        'statusCode': str(status_code),
        'body': json.dumps(message),
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
            }
        }
 
def lambda_handler(event, context):

    audio = event['content']
    audio = base64.b64decode(audio)
    audio = AudioSegment.from_file(io.BytesIO(audio)).set_channels(1).set_frame_rate(SR)
    audio = audio.get_array_of_samples()[:DURATION].tolist()

    lam = boto3.client('lambda')
    invoke_response = lam.invoke(FunctionName="scipy",
                                           InvocationType='RequestResponse',
                                           Payload=json.dumps(audio))
    stft = invoke_response.get('Payload').read()
    runtime = boto3.Session().client(service_name='sagemaker-runtime', region_name='us-east-1')
    response = runtime.invoke_endpoint(EndpointName=endpoint, ContentType='application/json', Body=stft)
    pred = response['Body'].read().decode()
    pred = json.loads(pred)['predictions']
    return format_response(json.dumps(pred), 200)     