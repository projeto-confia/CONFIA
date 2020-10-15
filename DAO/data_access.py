import pandas as pd
import numpy as np

class User:
    def __init__(self):
        self.count_similar_users = 0
        self.users_df = pd.read_csv("DAO/users.csv")
        self.users_id_arr = self.users_df["UserId"].to_numpy()
    
    def is_user_in_dataset(self, userID):
        return (userID in self.users_id_arr)
    