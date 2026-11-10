
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

# Sample training data
descriptions = [
    "minor water logging in streets",
    "light rainfall with small water accumulation",
    "few houses affected by flood",
    "moderate flooding in residential areas",
    "several people affected by heavy rainfall",
    "roads and houses damaged by flood",
    "many villages submerged in flood water",
    "large number of people trapped in flood",
    "severe flooding with major destruction",
    "entire region submerged and people need rescue",
    "small fire in a dustbin",
    "minor electrical fire quickly controlled",
    "fire in a small shop",
    "fire spreading across multiple buildings",
    "large fire with many people trapped",
    "massive fire causing major destruction"
]

severity_labels = [
    "Low", "Low", "Low", "Medium",
    "Medium", "Medium", "High", "High",
    "Critical", "Critical", "Low", "Low",
    "Medium", "High", "High", "Critical"
]

# Build and train the model
model = Pipeline([
    ("tfidf", TfidfVectorizer()),
    ("classifier", LogisticRegression(max_iter=1000))
])

model.fit(descriptions, severity_labels)

def predict_severity(description, affected_people):
    prediction = model.predict([description])[0]

    # Adjust severity using affected people
    if affected_people >= 500:
        prediction = "Critical"
    elif affected_people >= 100:
        prediction = "High"
    elif affected_people >= 20 and prediction == "Low":
        prediction = "Medium"

    probabilities = model.predict_proba([description])[0]
    confidence = max(probabilities) * 100

    return prediction, round(confidence, 2)