class TokenAuth:
    def __init__(self, valid_token: str):
        self.valid_token = valid_token

    def validate_token(self, token: str) -> bool:
        """ Validate the token string directly """
        return token == self.valid_token
