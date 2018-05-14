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


def read_sentences(file):
    list_of_nouns = []
    sentences = file["lemma_pos"]
    # Start going through every row in the list
    for row in sentences:
        row_of_nouns = []
        # Go through every tuple pair in the row to find nouns. Add them
        # and possibly the previous or next tuple to the list.
        for i, pair in enumerate(row):
            if pair[1] == "NOUN":
                # if i >= 1:
                #     previous_pair = row[i-1]
                #     if previous_pair[1] == "NOUN":
                #         row_of_nouns.extend((str(i-1), previous_pair[0], previous_pair[1]))

                if (row_of_nouns[:-1] != pair[1]) and (row_of_nouns[:-2] != pair[0]):
                    row_of_nouns.extend((str(i),pair[0], pair[1]))

                # if i+1 < len(row):
                #     next_pair = row[i+1]
                #     if next_pair[1] == "NOUN":
                #         row_of_nouns.extend((str(i+1), next_pair[0], next_pair[1]))
            elif pair[1] == "PUNCT":
                #Add current list to upper list (if it is not empty) and reset the current list.
                if row_of_nouns:
                    list_of_nouns.extend([row_of_nouns])
                row_of_nouns  = []
        if row_of_nouns:
            list_of_nouns.extend([row_of_nouns])
        # print(row)
    print(list_of_nouns)

def main():
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
    logging.debug("Entering main")
    df = open_file("Sample10.csv")
    read_sentences(df.head())


if __name__ == '__main__':
    main()