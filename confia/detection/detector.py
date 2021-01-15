from confia.detection.ics import ICS
from confia.orm.dao import DAO

class Detector:

    def __init__(self, train_ics=False):

        self.__ics = ICS(laplace_smoothing=0.01, omega=0.5)
        dao = DAO()
        
        if train_ics == True:
            print("\nIniciando o treinamento do ICS...")
            df_users = self.__ics.fit()

            try:
                print("\nSalvando os parâmetros de usuário no banco de dados...")
                dao.insert_update_user_accounts_db(df_users)
                print("Parâmetros dos usuários salvos com sucesso!")
            except Exception as e:
                print("Ocorreu um erro ao atualizar os parâmetros dos usuários\n{0}.".format(e.args))

    def predict_news(self, id_news):
        label = self.__ics.predict(id_news)
        print("Notícia {0} legítima de acordo com o ICS.".format(id_news)) if label == 0 else print("Notícia {0} falsa de acordo com o ICS.\nEnviando para as agências de checagem...".format(id_news))
    

   