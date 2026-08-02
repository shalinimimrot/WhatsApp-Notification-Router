class FusionEngine:

    def decide(
        self,
        llm,
        router_score,
        behavior_score,
        retrieval_score
    ):

        final = (
            router_score * 0.35
            + behavior_score * 0.25
            + retrieval_score * 0.20
            + llm["importance"] * 4
            + llm["urgency"] * 4
            - llm["risk"] * 5
            - llm["spam"] * 8
        )

        return final