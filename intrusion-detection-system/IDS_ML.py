import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import LabelEncoder
import matplotlib.pyplot as plt

# Define column names based on the NSL-KDD dataset structure
column_names = [
    "duration", "protocol_type", "service", "flag", "src_bytes", "dst_bytes", 
    "land", "wrong_fragment", "urgent", "hot", "num_failed_logins", "logged_in", 
    "num_compromised", "root_shell", "su_attempted", "num_root", "num_file_creations", 
    "num_shells", "num_access_files", "num_outbound_cmds", "is_host_login", 
    "is_guest_login", "count", "srv_count", "serror_rate", "srv_serror_rate", 
    "rerror_rate", "srv_rerror_rate", "same_srv_rate", "diff_srv_rate", 
    "srv_diff_host_rate", "dst_host_count", "dst_host_srv_count", "dst_host_same_srv_rate", 
    "dst_host_diff_srv_rate", "dst_host_same_src_port_rate", "dst_host_srv_diff_host_rate", 
    "dst_host_serror_rate", "dst_host_srv_serror_rate", "dst_host_rerror_rate", 
    "dst_host_srv_rerror_rate", "label", "extra"
]

# Load the training dataset
data_train = pd.read_csv(r"data/KDDTrain+.txt", names=column_names, header=None)

# Drop the "extra" column if it exists
data_train = data_train.drop(columns=["extra"])

# Encode categorical features using LabelEncoder
categorical_features = ["protocol_type", "service", "flag", "land", "logged_in", "is_host_login", "is_guest_login"]
encoder = LabelEncoder()

for feature in categorical_features:
    data_train[feature] = encoder.fit_transform(data_train[feature])

# Encode labels: 1 for attack, 0 for normal
data_train['label'] = data_train['label'].apply(lambda x: 0 if x == 'normal' else 1)

# Debugging: Ensure all columns are numeric
assert data_train.dtypes.apply(lambda x: np.issubdtype(x, np.number)).all(), "Not all columns are numeric!"

# Split features and labels
X_train = data_train.drop("label", axis=1)
y_train = data_train["label"]

# Train the Random Forest Classifier
model = RandomForestClassifier(n_estimators=50, random_state=42)
model.fit(X_train, y_train)

print("Training complete. Model is ready for evaluation.")

# Load the test dataset
data_test = pd.read_csv(r"data/KDDTest.txt", names=column_names, header=None)

# Drop the "extra" column if it exists
data_test = data_test.drop(columns=["extra"])

# Encode categorical features using the same LabelEncoder
for feature in categorical_features:
    data_test[feature] = encoder.fit_transform(data_test[feature])

# Encode labels in the test data
data_test['label'] = data_test['label'].apply(lambda x: 0 if x == 'normal' else 1)

# Split test features and labels
X_test = data_test.drop("label", axis=1)
y_test = data_test["label"]

# Predict on the test set
y_pred = model.predict(X_test)

# Evaluate the model
accuracy = accuracy_score(y_test, y_pred)
report = classification_report(y_test, y_pred)

print(f"\nModel Accuracy: {accuracy * 100:.2f}%")
print("\nClassification Report:\n", report)

# Plot accuracy graph
labels = ["Accuracy"]
values = [accuracy * 100]
plt.bar(labels, values, color='blue')
plt.ylabel("Percentage")
plt.title("Model Accuracy")
plt.ylim(0, 100)
plt.show()