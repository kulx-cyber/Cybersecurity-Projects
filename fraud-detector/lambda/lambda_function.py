import json
import boto3
import joblib
import os
import numpy as np
import tempfile
from sklearn.preprocessing import StandardScaler

s3 = boto3.client('s3')
bucket = 'aws-fraud-detection-data-kulx' # Replace with your actual bucket name

model_key = 'model/model.joblib'
scaler_key = 'model/scaler.joblib'

def lambda_handler(event, context):
    # Extract features from JSON body
    data = json.loads(event['body'])
    features = [data.get(f"V{i}", 0.0) for i in range(1, 29)]
    time = data.get("Time", 0.0)
    amount = data.get("Amount", 0.0)

    # Download model/scaler to /tmp
    model_path = "/tmp/model.joblib"
    scaler_path = "/tmp/scaler.joblib"
    s3.download_file(bucket, model_key, model_path)
    s3.download_file(bucket, scaler_key, scaler_path)

    model = joblib.load(model_path)
    scaler = joblib.load(scaler_path)

    # Apply scaling
    scaled_time, scaled_amount = scaler.transform([[time, amount]])[0]
    features.insert(0, scaled_time)
    features.insert(1, scaled_amount)

    prediction = model.predict([features])[0]
    result = {"prediction": int(prediction)}

    return {
        'statusCode': 200,
        'body': json.dumps(result)
    }