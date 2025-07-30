# Intrusion Detection System using Machine Learning

## Overview

This project implements a machine learning-based Intrusion Detection System (IDS) using the NSL-KDD dataset. The system uses a Random Forest classifier to detect network intrusions and classify network traffic as either normal or malicious.

## Features

- **Binary Classification**: Distinguishes between normal network traffic and various types of attacks
- **Random Forest Algorithm**: Utilizes ensemble learning for robust attack detection
- **Feature Engineering**: Automatic encoding of categorical features for ML processing
- **Performance Metrics**: Comprehensive evaluation with accuracy scores and classification reports
- **Visualization**: Graphical representation of model performance

## Dataset

The system uses the NSL-KDD dataset, which is an improved version of the KDD Cup 1999 dataset:
- **Training Data**: `KDDTrain+.txt`
- **Testing Data**: `KDDTest.txt`

### Dataset Features

The dataset contains 41 features including:
- **Basic Features**: Duration, protocol type, service, flag
- **Content Features**: Number of failed logins, root shell access attempts
- **Traffic Features**: Connection counts, error rates
- **Host-based Features**: Host count statistics and service patterns

## Project Structure

```
intrusion-detection-system/
├── IDS_ML.py          # Main implementation file
├── README.md          # Project documentation
├── data/              # Dataset directory
└── results/           # Output and results directory
```

## Requirements

Install the required dependencies:

```bash
pip install pandas numpy scikit-learn matplotlib
```

### Dependencies
- **pandas**: Data manipulation and analysis
- **numpy**: Numerical computing
- **scikit-learn**: Machine learning algorithms and metrics
- **matplotlib**: Data visualization

## Usage

1. **Prepare the Dataset**:
   - Place `KDDTrain+.txt` and `KDDTest.txt` in the project directory
   - Ensure the dataset files follow the NSL-KDD format

2. **Run the IDS**:
   ```bash
   python IDS_ML.py
   ```

3. **View Results**:
   - The script will output training completion status
   - Model accuracy percentage
   - Detailed classification report
   - Accuracy visualization graph

## Algorithm Details

### Random Forest Classifier
- **Estimators**: 50 decision trees
- **Random State**: 42 (for reproducible results)
- **Approach**: Ensemble learning with majority voting

### Data Preprocessing
1. **Categorical Encoding**: LabelEncoder for non-numeric features
2. **Label Encoding**: Binary classification (0=normal, 1=attack)
3. **Feature Selection**: Automatic handling of all 41 features

### Evaluation Metrics
- **Accuracy Score**: Overall classification accuracy
- **Classification Report**: Precision, recall, and F1-score
- **Confusion Matrix**: True/false positive and negative rates

## Expected Output

```
Training complete. Model is ready for evaluation.

Model Accuracy: XX.XX%

Classification Report:
              precision    recall  f1-score   support
           0       0.xx      0.xx      0.xx     xxxxx
           1       0.xx      0.xx      0.xx     xxxxx
    accuracy                           0.xx     xxxxx
   macro avg       0.xx      0.xx      0.xx     xxxxx
weighted avg       0.xx      0.xx      0.xx     xxxxx
```

## Model Performance

The Random Forest classifier typically achieves:
- High accuracy rates (>95% on NSL-KDD dataset)
- Good precision and recall for both normal and attack classes
- Robust performance across different attack types

## Attack Types Detected

The system can detect various network attacks including:
- **DoS (Denial of Service)**: neptune, smurf, pod, teardrop
- **Probe**: satan, ipsweep, nmap, portsweep
- **R2L (Remote to Local)**: warezclient, imap, ftp_write, guess_passwd
- **U2R (User to Root)**: buffer_overflow, loadmodule, perl, rootkit

## Future Enhancements

- Multi-class classification for specific attack types
- Real-time network traffic analysis
- Integration with network monitoring tools
- Advanced feature selection techniques
- Deep learning approaches (LSTM, CNN)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is open-source and available under the MIT License.

## Authors

- **Kulkarni** - Initial implementation

## Acknowledgments

- NSL-KDD Dataset creators
- Scikit-learn community
- Network security research community