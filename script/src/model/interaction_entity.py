class Interaction:
    def __init__(self, timestamp, user_id, user_question, bot_response):
        self.timestamp = timestamp
        self.user_id = user_id
        self.user_question = user_question
        self.bot_response = bot_response