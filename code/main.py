from data_loader import DataLoader
from router import MessageRouter
from llm_provider import LLMProvider
from retriever import MessageRetriever
from media_processor import MediaProcessor
from preference_engine import PreferenceEngine
import pandas as pd

# Load datasets
loader = DataLoader("../dataset")
data = loader.load_all()

preferences = PreferenceEngine(
    data["user_business_history"]
)


# Initialize components
router = MessageRouter(
    data,
    preferences
)
llm = LLMProvider()
media = MediaProcessor()
retriever = MessageRetriever(data["message_history"])


messages = data["messages"]

predictions = []

# Process ALL messages
start_from = 80

for i, (_, message) in enumerate(messages.iloc[start_from:].iterrows(), start=start_from + 1):
    print(f"Processing {i}/{len(messages)}")

    message_text = media.process(message, data)

    analysis = llm.analyze(message_text)

    history = retriever.retrieve(message_text)

    prediction = router.classify(message, analysis)

    if history:
        prediction["evidence_message_ids"] = ";".join(
            h["message_id"] for h in history
        )
    else:
        prediction["evidence_message_ids"] = "none"

    predictions.append({
    "message_id": message["message_id"],
    **prediction
})

# Save progress after every processed message
pd.DataFrame(predictions).to_csv("../dataset/output_partial.csv", index=False)

# Save final output after completion
output = pd.DataFrame(predictions)
output.to_csv("../dataset/output_new.csv", index=False)

print(output.head())

print(f"\nGenerated {len(output)} predictions.")
print("output.csv generated successfully!")