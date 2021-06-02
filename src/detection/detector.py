from src.detection.ics import ICS
from src.orm.dao import DAO
import logging

class Detector:

    def __init__(self):
        self.__ics = ICS(laplace_smoothing=0.01, omega=0.5)
        self.__logger = logging.getLogger()
        self.__logger.setLevel(logging.INFO)
        self.__dao = DAO()

    def fit(self):
        try:
            print("Iniciando o treinamento do ICS...")
            self.__ics.fit()
                # TODO: parametrizar a quantidade mínima de exemplos para o treinamento
                # elif len(df_users.index) < 50:
                #     print('Não há dados suficientes para treinamento.')
        except Exception as e:
            self.__logger.error(f"Ocorreu um erro durante o treinamento do ICS: {e.args}")

    def run(self):
        try:
            # verificando se usuários com reputação (i.e. usuários cujos parâmetros 'prob' diferente de 0.5) compartilharam alguma nova notícia.
            news_shared_by_users_with_params_ics = self.__dao.get_news_shared_by_users_with_params_ics()

            if len(news_shared_by_users_with_params_ics) == 0:
                print("Nenhuma nova notícia compartilhada por usuários reputados.\n")
            else:
                print("Atualizando notícias compartilhadas por usuários reputados...\n")
                news = []
                for _, row in news_shared_by_users_with_params_ics.iterrows():
                    id_news = row["id_news"]
                    predicted_label, prob_label = self.predict_news(id_news)
                    ground_truth_label = row["ground_truth_label"] 
                    news.append(id_news)

                    # atualiza os labels da notícia 'id_news'.
                    self.__dao.update_news_labels(id_news, bool(predicted_label), ground_truth_label, prob_label)
                
                print("\nAs seguintes notícias foram atualizadas:")
                print(*news, sep=', ')

        except Exception as e:
            self.__logger.error(f"Ocorreu um erro ao atualizar os parâmetros de usuário: {e.args}")

    def predict_news(self, id_news):
        label, prob = self.__ics.predict(id_news)
        
        print(f"Notícia {id_news} legítima com probabilidade de {round(prob * 100, 3)}% de acordo com o ICS.") if label == 0 else print(f"Notícia {id_news} falsa com probabilidade de {round(prob * 100, 3)}% de acordo com o ICS.")
        return label, prob
