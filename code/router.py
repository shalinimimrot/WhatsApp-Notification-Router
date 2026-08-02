print("NEW ROUTER LOADED")
import pandas as pd


class MessageRouter:

    def __init__(self, data, preferences):

        self.users = data["users"].set_index("user_id")
        self.groups = data["groups"].set_index("group_id")
        self.businesses = data["business_accounts"].set_index("business_id")
        self.user_business_history = data["user_business_history"]
        self.message_events = data["message_events"]
        self.daily_summary = data["daily_notification_summary"]
        self.preferences = preferences

    def classify(self, message, analysis):

        text = str(message.get("message_text", "")).lower()
        sender_type = str(message.get("sender_type", "")).lower()

        score = 50

    # -----------------------
    # AI Analysis
    # -----------------------

        score += analysis["urgency"] * 4
        score += analysis["importance"] * 3
        score -= analysis["risk"] * 6
        score -= analysis["spam"] * 10

        message_type = analysis["message_type"]

        evidence = "none"

        # -----------------------
        # Load Context
        # -----------------------

        user = None
        group = None
        business = None

        user_id = message.get("user_id")
        group_id = message.get("group_id")
        business_id = message.get("business_id")

        if user_id in self.users.index:
            user = self.users.loc[user_id]

        if pd.notna(group_id):
            if group_id in self.groups.index:
                group = self.groups.loc[group_id]

        if pd.notna(business_id):
            if business_id in self.businesses.index:
                business = self.businesses.loc[business_id]

        # -----------------------
        # User Preference Score
        # -----------------------

        preference_score = self.preferences.get_score(
            user_id,
            business_id
        )


        if preference_score >= 40:
            score += 20

        elif preference_score >= 20:
            score += 10

        elif preference_score <= -20:
            score -= 15

        elif preference_score <= -40:
             score -= 25        

        # -----------------------
        # Prompt Injection
        # -----------------------

        prompt_words = [
            "ignore previous",
            "system prompt",
            "override",
            "routing rules",
            "mark this"
        ]

        if any(x in text for x in prompt_words):

            return {
                "action": "mute",
                "message_type": "scam",
                "reason": "Prompt injection detected.",
                "confidence": 0.98,
                "evidence_message_ids": "none"
            }

        # -----------------------
        # Scam
        # -----------------------

        scam_words = [
            "otp",
            "kyc",
            "password",
            "verify",
            "urgent payment",
            "click here",
            "reward"
        ]

        scam_matches = sum(x in text for x in scam_words)

        if scam_matches >= 2:
             score -= 60
             message_type = "scam"

        # -----------------------
        # Payment
        # -----------------------

        payment_words = [
              "payment",
              "invoice",
              "bill",
              "upi",
              "bank",
              "transaction",
              "credited",
              "debited",
              "due",
              "reminder"
         ]

        if any(x in text for x in payment_words):
            score += 20

            if message_type == "unknown":
                  message_type = "payment"
        # -----------------------
        # Promotions
        # -----------------------

        promo_words = [
            "sale",
            "offer",
            "discount",
            "cashback",
            "coupon"
        ]

        promo_matches = sum(x in text for x in promo_words)

        if promo_matches >= 1 and analysis["importance"] <= 5:
             score -= 25
             message_type = "promotion"

        # -----------------------
        # Medical
        # -----------------------

        medical_words = [
            "doctor",
             "hospital",
             "appointment",
             "clinic",
             "medicine",
              "ambulance",
             "emergency",
             "icu",
              "surgery",
             "prescription"
        ]

        if any(x in text for x in medical_words):
             score += 35

             if message_type not in ["scam", "spam"]:
               message_type = "urgent"

        # -----------------------
        # Meetings
        # -----------------------

        meeting_words = [
            "meeting",
            "deadline",
            "presentation",
            "zoom",
            "interview",
            "webinar",
            "exam",
            "lecture"
        ]

        if any(x in text for x in meeting_words):
            score += 30
            message_type = "event"

        # -----------------------
        # User Behaviour
        # -----------------------

        if user is not None:

            if user["messages_replied_30d"] > 20:
                score += 10

            if user["notifications_dismissed_30d"] > 50:
                score -= 10

        # -----------------------
        # Group Type
        # -----------------------

        if group is not None:

            if group["group_type"] == "family":
                score += 25

            elif group["group_type"] == "coworker":
                score += 20

            elif group["group_type"] == "school_group":
                score += 15

            elif group["group_type"] == "marketplace":
                score -= 15

        # -----------------------
        # Business
        # -----------------------

        if business is not None:

            if business["verified"] == 1:

               score += 15

               if message_type == "scam":
                    message_type = "business_update"

            if business["user_reports_30d"] > 40:
                 score -= 40

            if message_type == "unknown":
                 message_type = "business_update"

        # --------------------------------
        # User-Business Relationship
        # --------------------------------

        if business_id is not None:

            history = self.user_business_history[
                 (self.user_business_history["user_id"] == user_id) &
                 (self.user_business_history["business_id"] == business_id)
             ]

            if not history.empty:

                 row = history.iloc[0]

                 if row["messages_opened_30d"] >= 5:
                    score += 10

                 if row["messages_replied_30d"] >= 2:
                     score += 15

                 if row["messages_dismissed_30d"] >= 5:
                       score -= 10

                 if row["allows_promotions"] == 0:
                     score -= 10

        # -----------------------
        # Sender
        # -----------------------

        if sender_type == "group":
            score += 10

        elif sender_type == "business":
            score += 5

        else:
            score += 10

        # --------------------------------
        # Notification Fatigue
        # --------------------------------

        summary = self.daily_summary[
             self.daily_summary["user_id"] == user_id
        ]

        if not summary.empty:

             avg_sent = summary["notifications_sent"].mean()

             if avg_sent > 8:
                 score -= 10

        # --------------------------------
        # Historical Message Behaviour
        # --------------------------------

        events = self.message_events[
              self.message_events["user_id"] == user_id
        ]

        if not events.empty:

             if events["message_reported"].sum() >= 3:
                 score -= 5

             if events["message_opened"].mean() > 0.7:
                 score += 5

             if events["notification_dismissed"].mean() > 0.6:
                 score -= 5

             if events["muted_after_message"].mean() > 0.4:
                 score -= 10          

        # -----------------------
        # Final Decision
        # -----------------------

        if score >= 70:
            action = "notify"

        elif score >= 40:
            action = "digest"

        else:
            action = "mute"

        if action == "notify":
             confidence = round(min(max(0.80 + (score - 70) / 200, 0.80), 0.98), 2)

        elif action == "digest":
              confidence = round(min(max(0.65 + (score - 40) / 200, 0.65), 0.90), 2)

        else:
              confidence = round(min(max(0.70 + (40 - score) / 200, 0.70), 0.95), 2)

        if action == "notify":

            if message_type == "urgent":
                 reason = "Urgent message requiring immediate attention."

            elif message_type == "payment":
                  reason = "Important payment-related update."

            elif message_type == "business_update":
                 reason = "Trusted business update requiring attention."

            elif message_type == "event":
                 reason = "Upcoming event or scheduled reminder."

            elif message_type == "personal":
                  reason = "High-priority personal conversation."

            elif business is not None and business["verified"] == 1:
                 reason = "Verified business with trusted communication."

            elif group is not None:
                  reason = f"Important update from {group['group_type']} group."

            elif preference_score >= 40:
                  reason = "User frequently engages with this sender."

            else:
                 reason = "Important message requiring immediate attention."

            if message_type == "promotion":
                 reason = "Promotional content that can be viewed later."

            elif message_type == "business_update":
                  reason = "Useful business update that is not urgent."

            elif message_type == "greeting":
                reason = "Greeting message suitable for later viewing."

            elif message_type == "forward":
                 reason = "Forwarded message with low immediate priority."

            else:
                 reason = "Useful information that does not require immediate attention."

        else:

              if message_type == "scam":
                  reason = "Potential phishing or scam indicators detected."

              elif message_type == "spam":
                  reason = "Likely spam or repetitive unwanted content."

              elif message_type == "promotion":
                     reason = "Low-priority promotional content."

              elif preference_score <= -20:
                     reason = "User typically ignores messages from this sender."

              else:
                     reason = "Low-priority message based on user behaviour."

        return {
            "action": action,
            "message_type": message_type,
            "reason": reason,
            "confidence": confidence,
            "evidence_message_ids": evidence
        }