import ast

import pandas as pd
pd.options.mode.chained_assignment = None
import logging
import csv
import os

COMBINATIONS4 = [("JJ", "NN","NN", "NN"),("RB", "JJ","NN", "NN"),("JJ", "JJ","NN", "NN"),("RB","JJ","JJ","NN"),("JJ","CC", "JJ", "NN")]
COMBINATIONS3 = [("NN","NN", "NN"),("JJ","NN", "NN"),("RB","JJ","NN"),("JJ","JJ", "NN"), ("NN", "CC", "NN")]
COMBINATIONS2 = [("NN", "NN"), ("JJ", "NN")]
ADJECTIVES = ["JJ", "JJR", "JJS"]
NOUNS = ["NN", "NNP", "NNPS", "NNS"]
ADVERBS = ["RB", "RBR", "RBS"]

def open_file(file, type):
    if type == "warriner":
        logging.debug("Entering open file warriner")
        raw_table = pd.read_csv(file, sep=',', encoding='utf-8')
    else:
        logging.debug("Entering open file pandas")
        raw_table = pd.read_csv(file, sep=';', encoding='utf-8')
    # This transforms the csv-string back to a list
        if 'lemma_tag_dep' in raw_table:
            raw_table['lemma_tag_dep'] = raw_table['lemma_tag_dep'].map(ast.literal_eval)
    return raw_table


def save_file(file, name):
    logging.debug("Entering writing pandas to file")
    try:
        filepath = "./save/"
        if not os.path.exists(filepath):
            os.makedirs(filepath)
        file.to_csv(filepath + name + ".csv", encoding='utf-8', sep=";", quoting=csv.QUOTE_NONNUMERIC)
    except IOError as exception:
        print("Couldn't save the file. Encountered an error: %s" % exception)
    logging.debug("Finished writing: " + name)


def new_find_noun_phrases(raw_list):
    logging.debug("Entering find noun phrases")
    list_of_noun_phrases = []
    list_of_grouped_words = []
    for sentence in raw_list:
        inclusion_check = False
        for i, word in enumerate(sentence):
            if i+1 < len(sentence):
                first_word = sentence[i]
                if any(first_word[1] in wrd for wrd in ADJECTIVES + NOUNS + ADVERBS):
                    next_word = sentence[i+1]
                # This part checks for tri-grams
                if any(next_word[1] in wrd for wrd in ADJECTIVES + NOUNS + ADVERBS):
                    if i+2 < len(sentence):
                        subsequent_word = sentence[i + 2]
                        for x1, x2, x3 in COMBINATIONS3:
                            if x1 == first_word[1] and x2 == next_word[1] and x3 == subsequent_word[1]:
                                list_of_grouped_words.append((first_word, next_word, subsequent_word))
                                inclusion_check = True
                    if i+2 >= len(sentence):
                        inclusion_check = False
                # This part checks for bigrams
                if not inclusion_check:
                    for x1, x2 in COMBINATIONS2:
                        if x1 == first_word[1] and x2 == next_word[1]:
                            list_of_grouped_words.append((first_word, next_word))
                            inclusion_check = True
        # This creates every sentence as its own list of lists
        if len(list_of_grouped_words) != 0:
            list_of_noun_phrases.append(list_of_grouped_words)
        list_of_grouped_words = []
    # This returns a list, where evey noun is its own list
    return list_of_noun_phrases


def assign_vad_scores(noun_phrases, score_list):
    logging.debug("Entering assign vad scores")
    phrase_scores = []
    all_scores = []
    for x in noun_phrases:
        count_chunks = 0
        for phrase in x:
            i = 0
            while i < len(phrase):
                # The way to access the word in the list is through phrase[i][0]
                score = [item for item in score_list if phrase[i][0] in item]
                if len(score) != 0:
                    # The * ensures that only the list contents from score are returned
                    phrase_scores.append(*score)
                else:
                    phrase_scores.append((phrase[i][0], 5.00, 5.00, 5.00))
                i += 1
            if len(phrase_scores) != 0:
                all_scores.append(phrase_scores)
            phrase_scores = []
    return all_scores
    # The first number in the score list is the number of the word, the second one is [0]
    # for name, [1] for valence, [2] for arousal, [3] for dominance


def calculate_new_vad_scores(noun_phrases):
    all_new_scores = []
    phrase_scores = []
    for phrase in noun_phrases:
        new_word = []
        valence = []
        arousal = []
        dominance = []
        for word, v, a, d in phrase:
            new_word.append(word)
            valence.append(v)
            arousal.append(a)
            dominance.append(d)
        new_string = ' '.join(new_word)
        new_valence = float(format(sum(valence)/len(valence), '.2f'))
        new_arousal = float(format(sum(arousal)/len(arousal), '.2f'))
        new_dominance = float(format(sum(dominance)/len(dominance), '.2f'))
        print(new_string, str(new_valence), str(new_arousal), str(new_dominance))

def new_format_tags(tagged_texts):
    logging.debug("Entering format tags")
    formatted_list = []
    formatted_list_by_sentence = []
    for sentence in tagged_texts:
        for word in sentence:
            word2 = None
            if (word[1] in ADJECTIVES):
                word2 = (word[0], ADJECTIVES[0], word[2])
                formatted_list.append(word2)
            if (word[1] in NOUNS):
                word2 = (word[0], NOUNS[0], word[2])
                formatted_list.append(word2)
            if (word[1] in ADVERBS):
                word2 = (word[0], ADVERBS[0], word[2])
                formatted_list.append(word2)
            else:
                if word2 == None:
                    formatted_list.append(word)
        # This creates every sentence as its own list of tuples
        formatted_list_by_sentence.append(formatted_list)
        formatted_list = []
    return formatted_list_by_sentence


# def lemmatize_words(phrase_list):
#     logging.debug("Entering lemmatization")
#     for x in phrase_list:
#         for phrase in x:
#             print(phrase)

def main():
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
    logging.debug("Entering main")
    df = open_file("Sample10.csv", "pandas")


    # Old version
    #raw_list_of_nouns_adjectives = find_nouns_adjectives(df.head(20))
    #listed_nouns = group_nouns(raw_list_of_nouns_adjectives)
    # print(listed_nouns)

    # New version
    # This creates a new column, where the tags are shortened to basic forms.
    tagged_texts = df["lemma_tag_dep"]
    df["formatted"] = new_format_tags(tagged_texts)
    noun_phrases = new_find_noun_phrases(df["formatted"])

    warriner_scores = open_file("Short_Warriner.csv", "warriner")
    zipped_scores = list(zip(warriner_scores["word"], warriner_scores["valence"], warriner_scores["arousal"], warriner_scores["dominance"]))

    short_nouns = noun_phrases
    vad_scores_phrases = assign_vad_scores(short_nouns, zipped_scores)
    calculate_new_vad_scores(vad_scores_phrases)

if __name__ == '__main__':
    main()