import streamlit as st
import base64
import requests
import json
import numpy as np
import pandas as pd


st.title("Bird Sound Identification")

st.subheader('Upload file below')
uploaded_file = st.file_uploader('')
if uploaded_file is not None:
    
    classes = ['amerob','gnwwere1','grekis','houspa','mallar', 'redcro']

    string_data = uploaded_file.read()
    audio = base64.b64encode(string_data).decode('utf-8')

    url = "https://uo8jn9b563.execute-api.us-east-1.amazonaws.com/default"
    payload = {"content" : audio}
    resp = requests.post(url, data=json.dumps(payload))
    preds = json.loads(resp.text)
    preds = json.loads(preds['body'])
    preds = json.loads(preds)

    pred_dict = {col:[p] for col,p in zip(classes, preds[0])}
    df = pd.DataFrame.from_dict(pred_dict, orient='index', columns=['confidence'])
    st.subheader('Prediction')
    st.text('')
    st.table(df.sort_values(by='confidence', ascending=False).head(10))
