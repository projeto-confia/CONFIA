import pandas as pd
import numpy as np

class User:
    def __init__(self):
        self.count_similar_users = 0
        self.users_df = pd.read_csv("confia/monitor/users.csv")
        self.users_id_arr = self.users_df["UserId"].to_numpy()
    
    def is_user_in_dataset(self, userID):
        return (userID in self.users_id_arr)

    def write_in_csv(self, tweet, userID, count_tweets):
        import csv, os
        from datetime import datetime

        path = os.path.join("confia", "data", datetime.today().strftime('%Y-%m-%d') + ".csv")

        with open(path, mode='a') as tweet_file:
            now = datetime.now()
            writer = csv.writer(tweet_file, delimiter=',')
            writer.writerow(["{0}:{1}:{2}".format(now.hour, now.minute, now.second), userID, tweet.replace('\n', ' '), count_tweets])