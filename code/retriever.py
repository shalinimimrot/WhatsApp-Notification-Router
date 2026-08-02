from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class MessageRetriever:

    def __init__(self, history_df):

        self.history = history_df.copy()

        # Convert NaN to empty strings
        self.history["message_text"] = (
            self.history["message_text"]
            .fillna("")
            .astype(str)
        )

        self.vectorizer = TfidfVectorizer(
            stop_words="english"
        )

        self.matrix = self.vectorizer.fit_transform(
            self.history["message_text"]
        )

    def retrieve(self, query, top_k=2):

        query_vector = self.vectorizer.transform([query])

        similarity = cosine_similarity(
            query_vector,
            self.matrix
        )[0]

        indices = similarity.argsort()[-top_k:][::-1]

        results = []

        for idx in indices:

            score = similarity[idx]

            if score > 0.15:

                row = self.history.iloc[idx]

                results.append({
                    "message_id": row["message_id"],
                    "text": row["message_text"],
                    "score": float(score)
                })

        return results