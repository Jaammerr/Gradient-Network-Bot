class Account:
    def __init__(self, id, email: str, password: str, user_id = None, imap_pass: str = None, client_id: str = None, node_password: str = None, is_verified: bool = None):
        self.id = id
        self.user_id = user_id
        self.email = email
        self.password = password
        self.imap_password = imap_pass
        self.client_id = client_id
        self.node_password = node_password
        self.is_verified = is_verified

    def __repr__(self):
        return f"{self.email}"