from string import punctuation, printable
import config



def read_file(file):     # Function to read positive words, negative words dictionaries etc
    with open(file, encoding="utf-8") as f:
        data_words = f.read().splitlines()
    return data_words



def sentiment(tweet_text):

    ascii = set(printable)

    prev_word = ''
    pw = ''

    positive_words = read_file(config.path_pos)
    negative_words = read_file(config.path_neg)
    incrementers = read_file(config.path_inc)
    decrementers = read_file(config.path_dec)
    inverters = read_file(config.path_inv)

    tweet_text = "".join(list(filter(lambda x: x in ascii, tweet_text)))   # Remove smileys and non-ascii characters

    # Calculate positive or negative counters of the tweet_text

    word_list = tweet_text.split('\n')  # Split the sentences in the review text
    positive_counter = 0
    negative_counter = 0

    for word in word_list:

        word_processed = word.lower()

        word_processed = word_processed.replace('n\'t',' not')  # Replace n't to not in review text for better sentiment analysis result

        for p in list(punctuation):
            word_processed = word_processed.replace(p, ' ')

        words = word_processed.split(' ')

        #word_count = len(words)

        for word in words:  # Basic sentiment analysis

            if word in positive_words:
                if prev_word in incrementers:  # If current word is preceeded by 'very' etc. increase the positive point
                    positive_counter = positive_counter + 1.5
                elif prev_word in decrementers:
                    positive_counter = positive_counter + 0.5  # If current word is preceeded by 'barely' etc. decrease the positive point
                elif prev_word in inverters or pw in inverters:
                    negative_counter = negative_counter + 1  # If current word is preceeded by 'not' etc. change polarity
                else:
                    positive_counter = positive_counter + 1

            elif word in negative_words:
                if prev_word in incrementers:
                    negative_counter = negative_counter + 1.5
                elif prev_word in decrementers:
                    negative_counter = negative_counter + 0.5
                elif prev_word in inverters or pw in inverters:
                    positive_counter = positive_counter + 1
                else:
                    negative_counter = negative_counter + 1

            pw = prev_word  # 2nd previous word than current word, to check for words like "not a negative"
            prev_word = word  # Previous word to check for incrementers, decrementers & inverters

    if (positive_counter + negative_counter) > 0:
        positive_percentage = (positive_counter / (positive_counter + negative_counter)) * 100  # Positive percentage among the adjectives/adverbs considered
    else:
        positive_percentage = 0


    if positive_percentage > 0 and positive_percentage < 40:
        label = 'Negative'
    elif positive_percentage >= 40 and positive_percentage <= 60:
        label = 'Neutral'
    elif positive_percentage > 60:
        label = 'Positive'
    elif positive_percentage == 0:
        label = 'Neutral'

    return label


#label = sentiment("This is a positive review")
#print(label)

