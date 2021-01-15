import pandas as pd
import numpy as np

class User:

    def write_in_csv(self, tweet, userID):
        import csv, os
        from datetime import datetime

        path = os.path.join("confia", "data", datetime.today().strftime('%Y-%m-%d') + ".csv")

        with open(path, mode='a') as tweet_file:
            now = datetime.now()
            writer = csv.writer(tweet_file, delimiter=',')
            writer.writerow(["{0}:{1}:{2}".format(now.hour, now.minute, now.second), userID, tweet.replace('\n', ' ')])