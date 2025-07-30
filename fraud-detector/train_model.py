import json
import boto3
import joblib
import os
import numpy as np
import logging
from sklearn.preprocessing import StandardScaler

# Setup logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize S3 client
s3 = boto3.client('s3')
bucket = 'aws-fraud-detection-data-kulx' # Replace with your actual bucket name
model_key = 'model/model.joblib'
scaler_key = 'model/scaler.joblib'

def lambda_handler(event, context):
    try:
        # Log the incoming request body
        logger.info(f"Received event: {json.dumps(event)}")

        # Parse JSON input
        data = json.loads(event['body'])

        # Extract features
        features = [data.get(f"V{i}", 0.0) for i in range(1, 29)]
        time = data.get("Time", 0.0)
        amount = data.get("Amount", 0.0)

        # Download model and scaler to /tmp
        model_path = "/tmp/model.joblib"
        scaler_path = "/tmp/scaler.joblib"
        s3.download_file(bucket, model_key, model_path)
        s3.download_file(bucket, scaler_key, scaler_path)

        # Load model and scaler
        model = joblib.load(model_path)
        scaler = joblib.load(scaler_path)

        # Apply scaling
        scaled_time, scaled_amount = scaler.transform([[time, amount]])[0]
        features.insert(0, scaled_time)
        features.insert(1, scaled_amount)

        # Make prediction
        prediction = model.predict([features])[0]
        result = {"prediction": int(prediction)}

        # Log the prediction result
        logger.info(f"Response: {json.dumps(result)}")

        return {
            'statusCode': 200,
            'body': json.dumps(result)
        }

    except Exception as e:
        # Log any errors
        logger.error(f"Error processing request: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
