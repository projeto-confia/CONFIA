from functools import total_ordering
from math import remainder
from fuzzywuzzy import fuzz
from nltk.tag import pos_tag
from nltk.corpus import stopwords
from googletrans import Translator
import emoji, nltk, re, string, slugify
from src.config import Config as config
from nltk.tokenize import TweetTokenizer
from nltk.stem.wordnet import WordNetLemmatizer

class TextPreprocessing:

    def __init__(self, threshold=config.TEXT_PREPROCESSOR.DEFAULT_THRESHOLD, install_nltk_packages=False):
        """Classe provedora de métodos para tokenização, normalização, lematização e denoising de posts em redes sociais. 
        Necessária como pré-requisito para a análise de sentimento do texto.
        """
        
        self.__check_nltk_packages(install_nltk_packages)
        self.__translator = Translator()
        self.__tokenizer = TweetTokenizer()
        self.__lemmatizer = WordNetLemmatizer()
        self.__stopwords = nltk.corpus.stopwords.words('portuguese')
        self._threshold = threshold
        self.__punctuation = '!"$%&\'()*+,-./:;<=>?[\]^_`{|}~'

    
    def __check_nltk_packages(self, install_nltk_packages):
        if install_nltk_packages == True:
            nltk.download('punkt')
            nltk.download('averaged_perceptron_tagger')
            nltk.download('wordnet')
            nltk.download('stopwords')

    
    
    def text_cleaning(self, text):
        """remove hyperlinks, nomes de usuário precedidos pelo '@', pontuações e caracteres especiais."""

        text_cleaned = re.sub('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+#]|[!*\(\),]|''(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text, flags=re.MULTILINE)
        text_cleaned = "".join([char.lower() for char in text_cleaned if char not in self.__punctuation])
        text_cleaned = re.sub(r" #\w+\b(?!\s+\w+)", '', text_cleaned, flags=re.MULTILINE)
        text_cleaned = text_cleaned.replace('#', '')
        text_cleaned = re.sub("(@[A-Za-z0-9_]+)", "", text_cleaned, flags=re.MULTILINE)
        text_cleaned = re.sub('\s+', ' ', text_cleaned).strip()
        text_cleaned = re.sub(emoji.get_emoji_regexp(), r"", text_cleaned)
        text_cleaned = text_cleaned.replace('\n', ' ')
        
        return text_cleaned.lower()

    
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

    
    def check_duplications(self, news1_cleaned, news2_cleaned):
        """Verifica se os textos em 'news1' e 'news2', após o processo de limpeza, têm seus conteúdo duplicados. Utiliza o algoritmo de Levenshtein.

        Args:
            news1_cleaned (string): texto limpo da primeira mensagem.
            news2_cleaned (string): texto limpo da segunda mensagem.

        Returns:
            bool: retorna 'True' se os textos são semelhantes; falso se não.
            int: o valor da semelhança entre os dois textos.
        """
        
        value = fuzz.token_sort_ratio(news1_cleaned, news2_cleaned)
        return value >= self._threshold, value
    
    @staticmethod
    def slugify(text: str) -> str:
        return slugify.slugify(text.lower())
    
    
    @staticmethod
    def prepare_tweet_for_posting(title: str, content: str, slug: str) -> str:
        
        title = title + "\n\n"
        allowed_length = config.TWITTER_SETTINGS.TWEET_MAX_CHARS
        
        link_info = f"... Saiba mais em: {config.CONFIA_API.SITE_URL_HMG + slug}"
                
        total_length_without_content = len(title) + len(link_info)
        remainder_chars_for_content = allowed_length - total_length_without_content
        
        return title + content[:remainder_chars_for_content] + link_info \
            if remainder_chars_for_content > len(title) else title + link_info
