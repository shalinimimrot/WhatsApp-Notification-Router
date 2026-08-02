import pandas as pd


class FeatureEngineer:
    def __init__(self, data):
        self.data = data

    def build_user_features(self):
        users = self.data["users"].copy()

        users["engagement_score"] = (
            users["messages_opened_30d"] / 120
        ).clip(0, 1)

        users["reply_rate"] = (
            users["messages_replied_30d"]
            / users["messages_opened_30d"].clip(lower=1)
        )

        users["dismiss_rate"] = (
            users["notifications_dismissed_30d"]
            / (
                users["notifications_dismissed_30d"]
                + users["messages_opened_30d"]
            )
        )

        users["spam_sensitivity"] = (
            users["messages_reported_30d"]
            / users["messages_opened_30d"].clip(lower=1)
        )

        return users

    def build_group_features(self):
        groups = self.data["groups"].copy()

        priority = {
            "family": 5,
            "extended_family": 5,
            "coworker": 5,
            "safety": 5,
            "school_group": 4,
            "college_faculty": 4,
            "college_students": 3,
            "friends": 3,
            "society": 3,
            "book_club": 2,
            "sports": 2,
            "marketplace": 1,
            "investment_tips": 1,
            "real_estate": 1,
        }

        groups["group_priority"] = (
            groups["group_type"]
            .map(priority)
            .fillna(2)
        )

        groups["noise_score"] = (
            groups["messages_30d"]
            / groups["member_count"]
        )

        return groups

    def build_business_features(self):
        businesses = self.data["business_accounts"].copy()

        trust = []

        for _, row in businesses.iterrows():

            score = 0

            if row["verified"] == 1:
                score += 50

            if (
                str(row["official_domain"])
                == str(row["domain_used_by_sender"])
            ):
                score += 25

            score += min(row["account_age_days"] / 100, 15)

            score -= row["user_reports_30d"]

            trust.append(max(score, 0))

        businesses["trust_score"] = trust

        return businesses