user_id = 0


class User:

    def __init__(self):
        global user_id
        self.user_id = user_id
        user_id += 1
        self.cost = 0
