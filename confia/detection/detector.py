from confia.detection.ics import ICS
from confia.orm.dao import DAO

class Detector:

    def __init__(self, train_ics=False):

        self.__ics = ICS(laplace_smoothing=0.01, omega=0.5)
        dao = DAO()
        try:
            if train_ics == True:
                print("\nIniciando o treinamento do ICS...")
                df_users = self.__ics.fit()
                if isinstance(df_users, int) and not df_users:
                    print('Não há dados para treinamento.')
                # TODO: parametrizar a quantidade mínima de exemplos para o treinamento
                elif len(df_users.index) < 50:
                    print('Não há dados suficientes para treinamento.')
                else:
                    print("\nSalvando os parâmetros de usuário no banco de dados...")
                    dao.insert_update_user_accounts_db(df_users)
                    print("\nParâmetros dos usuários salvos com sucesso!\n")

            # verificando se usuários com reputação (i.e. usuários cujos parâmetros 'prob' diferente de 0.5) compartilharam alguma nova notícia.
            news_shared_by_users_with_params_ics = dao.get_news_shared_by_users_with_params_ics()

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
                    dao.update_news_labels(id_news, bool(predicted_label), ground_truth_label, prob_label)
                
                print("\nAs seguintes notícias foram atualizadas:")
                print(*news, sep=', ')

        except Exception as e:
            print("Ocorreu um erro ao atualizar os dados.\n{0}.".format(e.args))

    def predict_news(self, id_news):
        label, prob = self.__ics.predict(id_news)
        
        print(f"Notícia {id_news} legítima com probabilidade de {round(prob * 100, 3)}% de acordo com o ICS.") if label == 0 else print(f"Notícia {id_news} falsa com probabilidade de {round(prob * 100, 3)}% de acordo com o ICS.")
        return label, prob
