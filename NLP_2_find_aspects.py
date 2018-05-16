import ast

import pandas as pd
pd.options.mode.chained_assignment = None
import logging
import csv
import numpy as np
import os

NOUN_PHRASE_COMBINATIONS = [(("NN", "compound"),("NN", "dobj")), (("DT", "det"),("NN", "pobj")), (("JJ", "amod"), ("NN", "attr"))]
COMBINATIONS2 = [("NN", "NN"), ("DT", "NN"), ("JJ", "NN"), ("RB", "JJ")]
ADJECTIVES = ["JJ", "JJR", "JJS"]
NOUNS = ["NN", "NNP", "NNPS", "NNS"]
ADVERBS = ["RB", "RBR", "RBS"]

def open_file(file):
    logging.debug("Entering open file")
    raw_table = pd.read_csv(file, sep=';', encoding='utf-8')
    # This transforms the csv-string back to a list
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


def find_nouns_adjectives(file):
    logging.debug("Entering finding nouns and asjectives")
    list_of_nouns_adjectives = []
    sentences = file["lemma_pos"]
    # Start going through every row in the list
    for row in sentences:
        row_of_words = []
        # Go through every tuple pair in the row to find nouns. Add them
        # and possibly the previous or next tuple to the list.
        for i, pair in enumerate(row):
            if pair[1] == "NOUN":
                # if i >= 1:
                #     previous_pair = row[i-1]
                #     if previous_pair[1] == "NOUN":
                #         row_of_nouns.append((str(i-1), previous_pair[0], previous_pair[1]))

                # Doesn't work if (row_of_nouns[:-1] != pair[1]) and (row_of_nouns[:-2] != pair[0]):
                row_of_words.append((str(i),pair[0], pair[1]))

                # if i+1 < len(row):
                #     next_pair = row[i+1]
                #     if next_pair[1] == "NOUN":
                #         row_of_nouns.extend((str(i+1), next_pair[0], next_pair[1]))

            if pair[1] == "ADJ" and pair[0] != "which" and pair[0] != "what":
                if i >= 1:
                    previous_pair = row[i-1]
                    if previous_pair[1] == "ADV":
                        row_of_words.append((str(i-1), previous_pair[0], previous_pair[1]))

                # Doesn't work if (row_of_nouns[:-1] != pair[1]) and (row_of_nouns[:-2] != pair[0]):
                row_of_words.append((str(i),pair[0], pair[1]))

                # if i+1 < len(row):
                #     next_pair = row[i+1]
                #     if next_pair[1] == "NOUN":
                #         row_of_nouns.extend((str(i+1), next_pair[0], next_pair[1]))

            elif pair[1] == "PUNCT":
                #Add current list to upper list (if it is not empty) and reset the current list.
                if row_of_words:
                    list_of_nouns_adjectives.extend([row_of_words])
                row_of_words  = []
        if row_of_words:
            list_of_nouns_adjectives.extend([row_of_words])
        # print(row)
    return list_of_nouns_adjectives


def group_nouns(raw_list):
    list_by_sentence = []
    list_of_grouped_nouns = []
    for sentence in raw_list:
        inclusion_check = False
        print(sentence)
        for i, word in enumerate(sentence):
            if i+1 < len(sentence):
                next_word = sentence[i+1]
                # This part checks for tri-grams
                if i+2 < len(sentence):
                    subsequent_word = sentence[i+2]
                    if (int(subsequent_word[0]) - int(next_word[0])) == 1 and (int(next_word[0]) - int(word[0])) == 1:
                        if (subsequent_word[2] == "NOUN") and (next_word[2] == "NOUN") and ((word[2] == "NOUN") or (word[2] == "ADJ")):
                            list_of_grouped_nouns.append([(word[1] + " " + next_word[1] + " " + subsequent_word[1])])
                            inclusion_check = True
                if i+2 >= len(sentence):
                    inclusion_check = False
            # This part checks for bigrams
            if inclusion_check == False and (int(next_word[0]) - int(word[0])) == 1:
                    if (next_word[2] == "NOUN") and ((word[2] == "NOUN") or (word[2] == "ADJ")):
                        list_of_grouped_nouns.append([(word[1] + " " + next_word[1])])
                        inclusion_check = True
            #This part is for unigrams
            if inclusion_check == False and (word[2] == "NOUN"):
                    list_of_grouped_nouns.append([word[1]])
            # else:
            #     if word[2] == "NOUN":
            #         list_of_grouped_nouns.append([word[1]])
        # This creates every sentence as its own list of lists
        # list_by_sentence.append(list_of_grouped_nouns)
        # list_of_grouped_nouns = []

    # This returns a list, where evey noun is its own list
    return list_of_grouped_nouns
    # return list_by_sentence


def new_find_noun_phrases(raw_list):
    logging.debug("Entering find noun phrases")
    list_by_sentence = []
    list_of_grouped_nouns = []
    for sentence in raw_list:
        inclusion_check = False
        # print(sentence)
        for i, word in enumerate(sentence):
            if i+1 < len(sentence):
                first_word = sentence[i]
                if any(first_word[1] in adj for adj in ADJECTIVES + NOUNS + ADVERBS):
                    next_word = sentence[i+1]
                    for pair1, pair2 in COMBINATIONS2:
                        if pair1 == first_word[1] and pair2 == next_word[1]:
                            #print(sentence)
                            print(first_word + next_word)
            # This part checks for bigrams
            # if inclusion_check == False:
            #         if (next_word[2] == "NOUN") and ((word[2] == "NOUN") or (word[2] == "ADJ")):
            #             list_of_grouped_nouns.append([(word[1] + " " + next_word[1])])
            #             inclusion_check = True
            # #This part is for unigrams
            # if inclusion_check == False and (word[2] == "NOUN"):
            #         list_of_grouped_nouns.append([word[1]])

    # This returns a list, where evey noun is its own list
    # return list_of_grouped_nouns
    # return list_by_sentence


def assign_vad_scores(raw_list):
    pass


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

def main():
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
    logging.debug("Entering main")
    df = open_file("Sample10.csv")
    warriner_scores = []

    # Old version
    #raw_list_of_nouns_adjectives = find_nouns_adjectives(df.head(20))
    #listed_nouns = group_nouns(raw_list_of_nouns_adjectives)
    # print(listed_nouns)

    # New version
    # This creates a new column, where the tags are shortened to basic forms.
    tagged_texts = df["lemma_tag_dep"]
    df["formatted"] = new_format_tags(tagged_texts)
    new_find_noun_phrases(df["formatted"])

    # new_find_noun_phrases(tagged_texts.head())
    # for row in tagged_texts.head():
    #     for word in row:
    #         print(word[1])
    # for pair1, pair2 in COMBINATIONS2:
    #
    #     print(pair1)
    #     print(pair2)
    #     print(type(pair2))
    # find_noun_phrases(df["lemma_tag_dep"].head(20))

if __name__ == '__main__':
    main()