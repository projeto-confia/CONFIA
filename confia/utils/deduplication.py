from confia.utils.text_preprocessing import TextPreprocessing
from fuzzywuzzy import fuzz

class DuplicationAnalyzer:
    
    def __init__(self, threshold = 70):
        self._text_processing = TextPreprocessing()
        self._threshold = threshold

    def check_duplications(self, news1, news2):
        news1_cleaned = self._text_processing.text_cleaning(news1)
        news2_cleaned = self._text_processing.text_cleaning(news2)
        similarity = fuzz.token_sort_ratio(news1_cleaned, news2_cleaned)

        return similarity >= self._threshold, news1_cleaned, news2_cleaned


    
