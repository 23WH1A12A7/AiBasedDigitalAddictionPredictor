# 📦 Import Libraries
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

import joblib

# 📁 Load Dataset
df = pd.read_csv('mobile_phone_addiction_dataset.csv')

print(df.head())
print(df.tail())
print(df.shape)
print(df.info())

#  Data Cleaning
print("Missing values:\n", df.isnull().sum())
df.dropna(inplace=True)

# Drop useless index column
if 'Unnamed: 0' in df.columns:
    df.drop(columns=['Unnamed: 0'], inplace=True)

# Encode target variable correctly
df['addicted'] = df['addicted'].map({
    'addicted': 1,
    'not addicted': 0
})

# Verify encoding
print("\nTarget value counts:\n", df['addicted'].value_counts())

# 📊 EDA (Exploratory Data Analysis)
sns.histplot(df['daily_screen_time'], kde=True)
plt.title('Daily Screen Time Distribution')
plt.show()

sns.pairplot(df, hue='addicted')
plt.suptitle('Pairplot of Features vs Target', y=1.02)
plt.show()

# 🎯 Features & Target
X = df[
    [
        'daily_screen_time',
        'gaming_time',
        'social_media_usage',
        'app_sessions',
        'notifications',
        'night_usage'
    ]
]

y = df['addicted']

# 🔀 Train-Test Split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# 🧠 Train Random Forest Model
model = RandomForestClassifier(
    n_estimators=100,
    random_state=42,
    class_weight='balanced'
)

model.fit(X_train, y_train)

# 🔎 Model Evaluation
y_pred = model.predict(X_test)

print("\n✅ Accuracy:", accuracy_score(y_test, y_pred))
print("\n✅ Classification Report:\n", classification_report(y_test, y_pred))

sns.heatmap(
    confusion_matrix(y_test, y_pred),
    annot=True,
    fmt='d',
    cmap='Blues'
)
plt.title('Confusion Matrix')
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.show()

# 🔍 Feature Importance
importances = pd.Series(model.feature_importances_, index=X.columns)
importances.sort_values().plot(kind='barh')
plt.title('Feature Importances (Random Forest)')
plt.show()

# 💾 Save the model
joblib.dump(model, "random_forest_addiction_model.pkl")
print("\n🎉 Model saved as random_forest_addiction_model.pkl")
