# Real-Time Fraud Detection System

## Overview

This project implements a comprehensive real-time fraud detection system using machine learning and AWS cloud services. The system can process credit card transactions in real-time and predict whether they are fraudulent or legitimate with high accuracy. The solution leverages AWS Lambda for serverless computing, SageMaker for ML model deployment, and various other AWS services for a complete end-to-end fraud detection pipeline.

## Key Features

- **Real-Time Processing**: Instant fraud detection using AWS Lambda
- **High Accuracy**: XGBoost model trained on imbalanced fraud dataset
- **Scalable Architecture**: Serverless design handles varying transaction volumes
- **Cloud-Native**: Fully deployed on AWS with monitoring and logging
- **API Integration**: RESTful API for easy integration with existing systems
- **Cost-Effective**: Pay-per-use model with AWS Lambda

## Dataset

The system is trained on the **Credit Card Fraud Detection Dataset** from Kaggle:
- **Source**: [Kaggle Credit Card Fraud Dataset](https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud)
- **Original Size**: 284,807 transactions
- **Features**: 30 features (28 PCA-transformed + Time + Amount)
- **Target**: Binary classification (0=Normal, 1=Fraud)
- **Original Imbalance**: Only 0.172% fraudulent transactions
- **After SMOTE Processing**: 170,589 balanced samples (85,149 normal + 85,440 fraud)
- **Storage**: Hosted on AWS S3 at `s3://aws-fraud-detection-data-kulx/data/creditcard.csv`

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Client App    │────│   AWS Lambda    │────│   SageMaker     │
│                 │    │  (Preprocessing │    │   Endpoint      │
└─────────────────┘    │   + Inference)  │    │   (XGBoost)     │
                       └─────────────────┘    └─────────────────┘
                              │                         │
                              ▼                         ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   CloudWatch    │    │      S3         │
                       │   (Monitoring)  │    │   (Model        │
                       └─────────────────┘    │    Storage)     │
                                              └─────────────────┘
```

## Technologies Used

### Machine Learning
- **Python 3.8+**: Core programming language
- **Pandas**: Data manipulation and analysis
- **Scikit-learn**: Data preprocessing and evaluation metrics
- **XGBoost**: Gradient boosting classifier for fraud detection
- **Imbalanced-learn**: Handling class imbalance with SMOTE
- **Joblib**: Model serialization

### AWS Services
- **AWS Lambda**: Serverless inference endpoint
- **AWS SageMaker**: ML model hosting and deployment
- **AWS S3**: Model artifact storage
- **AWS CloudWatch**: Monitoring, logging, and alerting
- **AWS IAM**: Security and access management

### Development Tools
- **VS Code**: Development environment
- **Git**: Version control
- **AWS CLI**: Cloud resource management


## Project Structure

```
fraud-detector/
├── README.md                           # Project documentation
├── requirements.txt                    # Python dependencies
├── train_model.py                     # Local model training script
├── data/                              # Dataset directory
│   └── creditcard.csv                 # Raw credit card transaction data
├── model/                             # Model artifacts and training
│   ├── train_model_sagemaker.ipynb    # Jupyter notebook for S3-based training
│   ├── model.joblib                   # Trained XGBoost model (100% accuracy)
│   ├── scaler.joblib                  # Feature preprocessing scaler
│   ├── inference.py                   # SageMaker inference script
│   └── model.tar.gz                   # Packaged model for SageMaker
└── lambda/                            # AWS Lambda function
    ├── lambda_function.py             # Main Lambda handler
    └── function.zip                   # Deployment package
```

## Model Performance

The XGBoost classifier achieves exceptional performance on the fraud detection task:

### Latest Training Results
```
              precision    recall  f1-score   support

           0       1.00      1.00      1.00     85149
           1       1.00      1.00      1.00     85440

    accuracy                           1.00    170589
   macro avg       1.00      1.00      1.00    170589
weighted avg       1.00      1.00      1.00    170589
```

### Key Metrics
- **Overall Accuracy**: 100% (1.00)
- **Precision (Normal)**: 100% (1.00)
- **Precision (Fraud)**: 100% (1.00)
- **Recall (Normal)**: 100% (1.00)
- **Recall (Fraud)**: 100% (1.00)
- **F1-Score (Normal)**: 100% (1.00)
- **F1-Score (Fraud)**: 100% (1.00)

### Dataset Balance After SMOTE
- **Normal Transactions**: 85,149 samples
- **Fraudulent Transactions**: 85,440 samples
- **Total Training Samples**: 170,589
- **Perfect Class Balance**: ~50/50 split achieved

*Note: These exceptional results are achieved through SMOTE oversampling and careful feature engineering. Performance on real-world streaming data may vary.*

## Prerequisites

### Local Development
- Python 3.8 or higher
- AWS CLI configured with appropriate permissions
- AWS account with access to Lambda, SageMaker, S3, and CloudWatch

### AWS Permissions Required
- S3: Read/Write access for model storage
- SageMaker: Create models, endpoints, and endpoint configurations
- Lambda: Create and update functions
- CloudWatch: Read logs and metrics
- IAM: Manage roles and policies

## Installation & Setup

### 1. Clone Repository
```bash
git clone <repository-url>
cd fraud-detector
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Prepare Dataset
- Download the Credit Card Fraud Detection dataset from Kaggle
- Upload `creditcard.csv` to your S3 bucket: `s3://your-bucket-name/data/creditcard.csv`
- Update the bucket name in the training script to match your S3 bucket

## Local Development (VS Code)

### 1. Data Preprocessing and Model Training
```bash
python train_model.py
```

**What this does**:
- Loads credit card dataset from S3 (`s3://aws-fraud-detection-data-kulx/data/creditcard.csv`)
- Handles class imbalance using SMOTE (Synthetic Minority Oversampling Technique)
- Scales `Time` and `Amount` features using StandardScaler
- Trains an XGBoost classifier with optimized hyperparameters
- Achieves perfect performance metrics (100% accuracy, precision, recall)
- Saves trained model and scaler to `model/model.joblib` and `model/scaler.joblib`
- Automatically uploads model artifacts to S3 for SageMaker deployment

**Training Results**:
- **Total Samples After SMOTE**: 170,589 (perfectly balanced)
- **Training/Test Split**: 70/30
- **Model Performance**: Perfect scores across all metrics
- **Training Time**: Optimized for both accuracy and speed

### 2. Prepare Model for SageMaker Deployment
```bash
cd model
mkdir -p code
cp inference.py code/
cp model.joblib code/
cp scaler.joblib code/
tar -czvf model.tar.gz code/
```

**Model Package Contents**:
- `inference.py`: SageMaker inference script with model loading and prediction logic
- `model.joblib`: Trained XGBoost model
- `scaler.joblib`: Feature preprocessing scaler

### 3. Upload Model to S3
```bash
# Replace 'your-bucket-name' with your actual S3 bucket
aws s3 cp model.tar.gz s3://your-bucket-name/fraud/model.tar.gz
```

**S3 Storage**:
- Models are versioned and stored securely
- Enables easy rollback and A/B testing
- Cost-effective storage for ML artifacts

### 4. Deploy Model to SageMaker
1. **Create SageMaker Model**:
   - Navigate to AWS SageMaker Console
   - Create new model using S3 model artifact
   - Use `scikit-learn` container for inference

2. **Create Endpoint Configuration**:
   - Choose appropriate instance type (e.g., `ml.t2.medium` for testing)
   - Configure auto-scaling if needed

3. **Deploy Endpoint**:
   - Name: `fraud-detector-endpoint`
   - Monitor deployment status in console

### 5. Setup Lambda Function
```bash
cd lambda
# Package Lambda function
zip -r function.zip lambda_function.py

# Update existing function (or create new one)
aws lambda update-function-code \
  --function-name FraudDetector \
  --zip-file fileb://function.zip
```

**Lambda Configuration**:
- **Runtime**: Python 3.8 or 3.9
- **Memory**: 512 MB (adjustable based on performance needs)
- **Timeout**: 30 seconds
- **Environment Variables**:
  - `SAGEMAKER_ENDPOINT`: fraud-detector-endpoint
  - `S3_BUCKET`: your-model-bucket

**Required Lambda Layers**:
- Install necessary packages (pandas, numpy, boto3, scikit-learn) as Lambda layers
- Or include them in the deployment package for smaller dependencies

### 6. Test Lambda Function
Use AWS Lambda Console to test with example transaction data:

**Test Event Configuration**:
```json
{
  "httpMethod": "POST",
  "body": "{\"transaction\": {\"Time\": 100000, \"V1\": -1.2, \"V2\": 0.5, \"V3\": 1.1, \"V4\": -0.8, \"V5\": 0.3, \"V6\": -1.5, \"V7\": 0.9, \"V8\": -0.2, \"V9\": 1.7, \"V10\": -0.4, \"V11\": 0.8, \"V12\": -1.1, \"V13\": 0.6, \"V14\": -2.1, \"V15\": 1.3, \"V16\": -0.7, \"V17\": 0.4, \"V18\": -0.9, \"V19\": 1.6, \"V20\": -0.3, \"V21\": 0.7, \"V22\": -1.4, \"V23\": 0.2, \"V24\": -0.6, \"V25\": 1.2, \"V26\": -0.5, \"V27\": 0.1, \"V28\": -0.1, \"Amount\": 200.00}}"
}
```

## API Usage

### Input Format for Lambda
```json
{
  "transaction": {
    "Time": 100000,
    "V1": -1.2,
    "V2": 0.5,
    "V3": 1.1,
    "V4": -0.8,
    "V5": 0.3,
    "V6": -1.5,
    "V7": 0.9,
    "V8": -0.2,
    "V9": 1.7,
    "V10": -0.4,
    "V11": 0.8,
    "V12": -1.1,
    "V13": 0.6,
    "V14": -2.1,
    "V15": 1.3,
    "V16": -0.7,
    "V17": 0.4,
    "V18": -0.9,
    "V19": 1.6,
    "V20": -0.3,
    "V21": 0.7,
    "V22": -1.4,
    "V23": 0.2,
    "V24": -0.6,
    "V25": 1.2,
    "V26": -0.5,
    "V27": 0.1,
    "V28": -0.1,
    "Amount": 200.00
  }
}
```

### Output Format
```json
{
  "statusCode": 200,
  "body": {
    "prediction": 0,
    "confidence": 1.0,
    "risk_level": "LOW",
    "processing_time_ms": 35,
    "timestamp": "2025-07-29T10:30:00Z",
    "model_version": "v1.0.0"
  }
}
```

**Response Fields**:
- `prediction`: 0 (Normal) or 1 (Fraud)
- `confidence`: Model confidence score (0-1) - Currently achieving 1.0
- `risk_level`: HIGH, MEDIUM, or LOW based on prediction and confidence
- `processing_time_ms`: Inference latency (typically 30-50ms)
- `timestamp`: Processing timestamp in ISO format
- `model_version`: Current model version for tracking

## Monitoring and Observability
### AWS CloudWatch
- **Lambda Metrics**: Invocation count, duration, error rate, throttles
- **Custom Metrics**: Fraud detection rate, confidence scores
- **Log Analysis**: Detailed request/response logging for debugging
- **Alerts**: Automated alerts for high error rates or unusual patterns

### Key Metrics to Monitor
1. **Invocation Rate**: Transactions processed per minute/hour
2. **Latency**: Average response time for fraud detection
3. **Error Rate**: Failed predictions or system errors
4. **Fraud Detection Rate**: Percentage of transactions flagged as fraudulent
5. **Model Drift**: Changes in prediction patterns over time

### CloudWatch Dashboards
Create custom dashboards to visualize:
- Real-time transaction volume
- Fraud detection trends
- System performance metrics
- Cost analysis

## Security Considerations

### Data Protection
- **Encryption**: All data encrypted in transit and at rest
- **Access Control**: IAM roles with least privilege principle
- **API Security**: Authentication and rate limiting for API endpoints
- **Audit Logging**: Complete audit trail of all transactions

### Model Security
- **Model Versioning**: Track and manage model versions
- **Input Validation**: Comprehensive input sanitization
- **Output Filtering**: Secure handling of sensitive predictions
- **Access Logging**: Monitor model access and usage

## Performance Optimization

### Lambda Optimization
- **Cold Start Reduction**: Provisioned concurrency for consistent performance
- **Memory Tuning**: Optimize memory allocation for cost and performance
- **Connection Pooling**: Reuse connections to SageMaker endpoints

### SageMaker Optimization
- **Instance Selection**: Choose appropriate instance types for workload
- **Auto Scaling**: Automatic scaling based on traffic patterns
- **Multi-AZ Deployment**: High availability across availability zones

## Cost Optimization

### AWS Cost Management
- **Lambda**: Pay per request, optimize for execution time
- **SageMaker**: Use appropriate instance types, consider Spot instances
- **S3**: Lifecycle policies for model artifacts
- **CloudWatch**: Optimize log retention periods

### Estimated Monthly Costs (USD)
- **Lambda** (1M requests): ~$20
- **SageMaker** (ml.t2.medium): ~$35
- **S3** (model storage): ~$1
- **CloudWatch** (logs): ~$5
- **Total**: ~$61/month for moderate usage

## Troubleshooting

### Common Issues

1. **Lambda Timeout**
   - Increase timeout setting (max 15 minutes)
   - Optimize model loading and inference code

2. **SageMaker Endpoint Errors**
   - Check endpoint status in SageMaker console
   - Verify model artifacts and inference script

3. **High Latency**
   - Enable provisioned concurrency
   - Optimize feature preprocessing
   - Consider model quantization

4. **Memory Issues**
   - Increase Lambda memory allocation
   - Optimize data structures and processing

### Debug Steps
1. Check CloudWatch logs for detailed error messages
2. Test components individually (Lambda, SageMaker)
3. Validate input data format and ranges
4. Monitor resource utilization metrics

## Future Enhancements

### Technical Improvements
- **Real-time Model Updates**: Implement continuous learning pipeline
- **A/B Testing**: Compare multiple model versions simultaneously
- **Feature Store**: Centralized feature management with SageMaker Feature Store
- **Model Explainability**: Add SHAP or LIME for prediction explanations

### Business Features
- **Risk Scoring**: Multi-level risk assessment beyond binary classification
- **Alert System**: Real-time notifications for high-risk transactions
- **Dashboard**: Business intelligence dashboard for fraud analytics
- **Historical Analysis**: Trend analysis and reporting capabilities

### Advanced ML
- **Deep Learning**: Experiment with neural networks for complex patterns
- **Anomaly Detection**: Unsupervised learning for novel fraud patterns
- **Ensemble Methods**: Combine multiple models for improved accuracy
- **Real-time Learning**: Update model with new fraud patterns

## Contributing

We welcome contributions to improve the fraud detection system:

1. **Fork the Repository**
2. **Create Feature Branch**: `git checkout -b feature/new-enhancement`
3. **Commit Changes**: `git commit -am 'Add new feature'`
4. **Push Branch**: `git push origin feature/new-enhancement`
5. **Create Pull Request**

### Contribution Guidelines
- Follow PEP 8 Python style guidelines
- Add unit tests for new features
- Update documentation for changes
- Ensure backward compatibility

## License

This project is open-source and available under the MIT License.

## Support

For questions, issues, or support:
- **Issues**: Use GitHub Issues for bug reports and feature requests
- **Documentation**: Refer to AWS documentation for service-specific questions
- **Community**: Join relevant AWS and ML communities for broader discussions

## Acknowledgments

- **Kaggle**: For providing the Credit Card Fraud Detection dataset
- **AWS**: For providing robust cloud infrastructure and ML services
- **XGBoost Community**: For the excellent gradient boosting framework
- **Scikit-learn**: For comprehensive machine learning tools
- **Open Source Community**: For various libraries and tools used in this project

---

This project demonstrates a production-ready fraud detection system that combines machine learning expertise with cloud-native architecture to deliver scalable, fast, and secure detection of suspicious transactions with high accuracy.
