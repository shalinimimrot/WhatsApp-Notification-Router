import pandas as pd


class PreferenceEngine:

    def __init__(self, user_business_history):

        self.preferences = {}

        for _, row in user_business_history.iterrows():

            user = row["user_id"]
            business = row["business_id"]

            if user not in self.preferences:
                self.preferences[user] = {}

            score = 0

            # User opens messages
            score += row["messages_opened_30d"] * 2

            # User replies
            score += row["messages_replied_30d"] * 5

            # User dismisses
            score -= row["messages_dismissed_30d"] * 3

            # Promotion preference
            if row["allows_promotions"] == 1:
                score += 10
            else:
                score -= 10

            self.preferences[user][business] = score

    def get_score(self, user_id, business_id):

        if user_id not in self.preferences:
            return 0

        return self.preferences[user_id].get(
            business_id,
            0
        )