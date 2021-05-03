import pandas as pd
import nltk
import re
import string
from googletrans import Translator
from nltk.tokenize import TweetTokenizer
from nltk.corpus import stopwords
from nltk.tag import pos_tag
from nltk.stem.wordnet import WordNetLemmatizer
import fuzzywuzzy

class TextPreprocessing:

    def __init__(self, install_nltk_packages=False):
        """
        Classe provedora de métodos para tokenização, normalização, lematização e denoising de posts em redes sociais. 
        Necessária como pré-requisito para a análise de sentimento do texto.
        """
        self.__check_nltk_packages(install_nltk_packages)
        self.__translator = Translator()
        self.__tokenizer = TweetTokenizer()
        self.__lemmatizer = WordNetLemmatizer()

    def __check_nltk_packages(self, install_nltk_packages):
        if install_nltk_packages == True:
            nltk.download('punkt')
            nltk.download('averaged_perceptron_tagger')
            nltk.download('wordnet')
            nltk.download('stopwords')

    def translate(self, tweet):
        """
        Traduz os tweets em PT-BR para EN-US.
        """
        return self.__translator.translate(tweet).text

    def tokenize(self, tweet):
        return self.__tokenizer.tokenize(tweet)

    def lemmatizer(self, tokens):
        lemmatized_text = []

        # remove hyperlinks, nomes de usuário precedidos pelo '@', pontuações e caracteres especiais.
        for token, tag in pos_tag(tokens):
            token = re.sub('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+#]|[!*\(\),]|'
                           '(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', token, flags=re.MULTILINE)
            token = re.sub("(@[A-Za-z0-9_]+)", "", token, flags=re.MULTILINE)

            if tag.startswith('NN'):
                pos = 'n'
            elif tag.startswith('VB'):
                pos = 'v'
            else:
                pos = 'a'

            token = self.__lemmatizer.lemmatize(token, pos)

            # verifica se o token (palavra) não é vazia ou irrelevante antes de adicioná-la à 'lemmatized_text'.
            if len(token) > 0 and token not in string.punctuation and token.lower() not in stopwords.words('english'):
                lemmatized_text.append(token.lower())

        return lemmatized_text

    def process_text(self, tweet):
        tweet = self.translate(tweet)
        tokens = self.tokenize(tweet)
        lemmatized_text = self.lemmatizer(tokens)

        print("\nTweet processado: {0}\n".format(lemmatized_text))
