import pandas as pd

expected = pd.read_csv("../../dataset/sample_messages.csv")
predicted = pd.read_csv("../../dataset/output.csv")

print("Expected rows:", len(expected))
print("Predicted rows:", len(predicted))

print("\nExpected message_ids:")
print(expected["message_id"].head())

print("\nPredicted message_ids:")
print(predicted["message_id"].head())

merged = expected.merge(
    predicted,
    on="message_id",
    suffixes=("_expected", "_predicted")
)

print("\nMerged rows:", len(merged))