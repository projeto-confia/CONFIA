import pandas as pd
import nltk
from googletrans import Translator
from nltk.tokenize import TweetTokenizer
from nltk.tag import pos_tag
from nltk.stem.wordnet import WordNetLemmatizer

class TextPreprocessing:

    def __init__(self, install_nltk_packages=False):
        """
        Classe provedora de métodos para tokenização, normalização, lematização e denoising de posts em redes sociais. 
        Necessária como pré-requisito para a análise de sentimento do texto.
        """
        self.__check_nltk_packages(install_nltk_packages)
        self.__translator   = Translator()
        self.__tokenizer    = TweetTokenizer()
        self.__lemmatizer   = WordNetLemmatizer()

    def __check_nltk_packages(self, install_nltk_packages):
        if install_nltk_packages == True:
            nltk.download('punkt')
            nltk.download('averaged_perceptron_tagger')
            nltk.download('wordnet')

    def translate(self, tweet):
        """
        Traduz os tweets em PT-BR para EN-US.
        """
        return self.__translator.translate(tweet).text

    def tokenize(self, tweet):
        return self.__tokenizer.tokenize(tweet)

    def lemmatizer(self, tokens):
        lemmatized_text = []
        
        for word, tag in pos_tag(tokens):
            if tag.startswith('NN'):
                pos = 'n'
            elif tag.startswith('VB'):
                pos = 'v'
            else:
                pos = 'a'
            lemmatized_text.append(self.__lemmatizer.lemmatize(word, pos))
        
        return lemmatized_text

    def print_preprocessing(self, tweet):
        tweet           = self.translate(tweet)
        tokens          = self.tokenize(tweet)
        lemmatized_text = self.lemmatizer(tokens)

        print("\nTweet processado: {0}\n".format(lemmatized_text))