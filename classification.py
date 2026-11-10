from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

# Training dataset for demonstration
texts = [
    "heavy rainfall caused flooding",
    "water entered residential houses",
    "river overflow damaged villages",
    "roads submerged under water",
    "flood water damaged crops",

    "building caught fire",
    "forest fire spreading rapidly",
    "smoke coming from a factory",
    "electrical short circuit caused fire",
    "large fire damaged houses",

    "strong earthquake shook the city",
    "buildings collapsed after earthquake",
    "ground shaking damaged roads",
    "earthquake caused cracks in buildings",
    "tremors felt across the region",

    "cyclone with strong winds",
    "severe storm hit coastal areas",
    "heavy winds damaged houses",
    "coastal cyclone caused destruction",
    "storm surge affected villages",

    "landslide blocked the mountain road",
    "heavy rain caused mudslide",
    "rocks fell from hillside",
    "soil movement damaged houses",
    "mountain slope collapsed"
]

labels = (
    ["Flood"] * 5 +
    ["Fire"] * 5 +
    ["Earthquake"] * 5 +
    ["Cyclone"] * 5 +
    ["Landslide"] * 5
)

# Create ML pipeline
model = Pipeline([
    ("tfidf", TfidfVectorizer()),
    ("classifier", LogisticRegression(max_iter=1000))
])

# Train model
model.fit(texts, labels)


def classify_disaster(description):

    prediction = model.predict([description])[0]

    probabilities = model.predict_proba([description])[0]

    confidence = max(probabilities) * 100

    return prediction, round(confidence, 2)