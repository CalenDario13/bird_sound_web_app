from json import dumps, loads
from boto3 import client, Session
from base64 import b64decode
from io import BytesIO
from pydub import AudioSegment

def format_response(message, status_code):
    return {
        'statusCode': str(status_code),
        'body': dumps(message),
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
            }
        }
        
def lambda_handler(event, context):
    
    # Declare Variables:
    SR = 32000
    DURATION  = SR*5

    
    # Decalare IDs:
    id_class = {0:"comrav", 
                1: "gbwwre", 
                2: "grekis", 
                3: "mallar", 
                4: "redcro", 
                5:"roahaw", 
                6:"rucspa"}
    
    # Extract Audio and Decode:
    body= loads(event['body'])
    
    audio = b64decode(body['data'])
    audio = AudioSegment.from_file(BytesIO(audio)).set_channels(1).set_frame_rate(SR)
    audio = audio.get_array_of_samples()[:DURATION].tolist()
    
    
    # Transform Audio to Spectrogram image:
    lam = client('lambda')
    invoke_response = lam.invoke(FunctionName="scipy",
                                 InvocationType='RequestResponse',
                                 Payload=dumps(audio))
    stft = invoke_response.get('Payload').read()
    
    
    # Get the SageMaker Evaluation:
    runtime = Session().client(service_name='sagemaker-runtime', 
                               region_name='us-east-1')
    response = runtime.invoke_endpoint(EndpointName='tensorflow-training-2021-09-01-07-51-28-475',
                                        ContentType='application/json', 
                                        Body=stft)
                                       
    pred = response['Body'].read().decode()
    pred = loads(pred)['predictions'][0]
    
    # Get the ID and prob:
    arg_max = 0
    max_val = pred[0]
    for i in range(len(pred)):
        if pred[i] > max_val:
            max_val = pred[i]
            arg_max = i

    return format_response(dumps([id_class[arg_max], max_val]), 200)  


