import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from tensorflow.keras.utils import to_categorical
import matplotlib.pyplot as plt

# Load the CSV files
train_data = pd.read_csv('sign_mnist_train.csv')
test_data = pd.read_csv('sign_mnist_test.csv')

# Extract features and labels
X_train = train_data.iloc[:, 1:].values  # Pixels
y_train = train_data.iloc[:, 0].values  # Labels

X_test = test_data.iloc[:, 1:].values
y_test = test_data.iloc[:, 0].values

# Reshape data to 28x28 grayscale images
X_train = X_train.reshape(-1, 28, 28, 1) / 255.0  # Normalize to [0, 1]
X_test = X_test.reshape(-1, 28, 28, 1) / 255.0

# Convert labels to one-hot encoding
y_train = to_categorical(y_train, num_classes=25)  # 25 classes (excluding J and Z)
y_test = to_categorical(y_test, num_classes=25)

# Visualize a sample
plt.imshow(X_train[0].reshape(28, 28), cmap='gray')
plt.title(f'Label: {np.argmax(y_train[0])}')
plt.show()
