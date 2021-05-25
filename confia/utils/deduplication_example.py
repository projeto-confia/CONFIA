from confia.utils.deduplication import DuplicationAnalyzer
from confia.orm.dao import DAO
import random
import time

if __name__ == "__main__":
    duplication_analyzer = DuplicationAnalyzer(70)
    dao = DAO()

    news = dao.read_query_to_dataframe("select * from detectenv.news;")
    similar_news = []
    similar_news_ids = []
    news.to_csv(r"confia/data/news.csv", index=True)
    
    # escolhe um id aleatório para fazer a comparação.
    news_idx = 6 #random.randint(0, len(news))
    chosen_news = news.iloc[news_idx]["text_news"]

    start_time = time.time()

    for i in range(len(news)):
        if i == news_idx: continue
        
        current_news = news.iloc[i]["text_news"]
        is_similar = duplication_analyzer.check_duplications(chosen_news, current_news)

        if is_similar == True:
            similar_news_ids.append(news.iloc[i]["id_news"])
            similar_news.append(current_news)

    end_time = time.time() - start_time
    
    print(f"\nORIGINAL TWEET: {chosen_news}\n\n{len(similar_news)} SIMILAR TWEETS TO: {chosen_news}\n\n")
    for i in range(len(similar_news)):
        print(f"{similar_news_ids[i]} -> {similar_news[i]}")
    print(f"\nExecution time: {end_time} seconds.")