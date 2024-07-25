user_id = 0


class User:

    def __init__(self, enable_share, start_latitude, start_longitude, end_latitude, end_longitude, start_time):
        global user_id
        self.user_id = user_id
        user_id += 1
        self.cost = 0
        self.enable_share = enable_share
        self.start_latitude = start_latitude
        self.start_longitude = start_longitude
        self.end_latitude = end_latitude
        self.end_longitude = end_longitude
        self.start_time = start_time
