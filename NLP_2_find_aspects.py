import ast

import pandas as pd
pd.options.mode.chained_assignment = None
import logging
import csv
import numpy as np
import os


def open_file(file):
    logging.debug("Entering open file")
    raw_table = pd.read_csv(file, sep=';', encoding='utf-8')
    # This transforms the csv-string back to a list
    raw_table['lemma_pos'] = raw_table['lemma_pos'].map(ast.literal_eval)
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
    list_of_grouped_nouns = []
    for sentence in raw_list:
        inclusion_check = False
        print(sentence)
        for i, word in enumerate(sentence):
            if i+1 < len(sentence):
                next_word = sentence[i+1]
                if i+2 < len(sentence):
                    subsequent_word = sentence[i+2]
                    if (int(subsequent_word[0]) - int(next_word[0])) == 1 and (int(next_word[0]) - int(word[0])) == 1:
                        list_of_grouped_nouns.append([(word[1] + " " + next_word[1] + " " + subsequent_word[1])])
                        inclusion_check = True
                if i+2 >= len(sentence):
                    inclusion_check = False
            if inclusion_check == False and (int(next_word[0]) - int(word[0])) == 1:
                    if (next_word[2] == "NOUN") and (word[2] == "NOUN"):
                        list_of_grouped_nouns.append([(word[1] + " " + next_word[1])])
                        inclusion_check = True
            if inclusion_check == False and (word[2] == "NOUN"):
                    list_of_grouped_nouns.append([word[1]])
            # else:
            #     if word[2] == "NOUN":
            #         list_of_grouped_nouns.append([word[1]])
    print(list_of_grouped_nouns)


def main():
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
    logging.debug("Entering main")
    df = open_file("Sample10.csv")
    raw_list_of_nouns_adjectives = find_nouns_adjectives(df)
    print(type(raw_list_of_nouns_adjectives))
    group_nouns(raw_list_of_nouns_adjectives)


if __name__ == '__main__':
    main()