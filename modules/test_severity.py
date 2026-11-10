
from severity_prediction import predict_severity
description = "Heavy rainfall caused flooding and many houses were damaged"
affected_people = 250

severity, confidence = predict_severity(
    description,
    affected_people
)

print("Predicted Severity:", severity)
print("Model Confidence:", confidence, "%")
