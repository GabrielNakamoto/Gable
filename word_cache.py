import random
from nltk.corpus import words

all_words = words.words()

five_letter_words = [word.upper() for word in all_words if len(word) == 5]

random_word = random.choice(five_letter_words)
print(random_word)
