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
    for row in sentences:
        row_of_nouns = []
        for i, pair in enumerate(row):
            if pair[1] == "NOUN":
                row_of_nouns.extend((str(i),pair[0], pair[1]))
                if i+1 < len(row):
                    next_pair = row[i+1]
                    row_of_nouns.extend((str(i+1), next_pair[0], next_pair[1]))
                if i >= 1:
                    previous_pair = row[i-1]
                    row_of_nouns.extend((str(i-1), previous_pair[0], previous_pair[1]))
            elif pair[1] == "PUNCT":
                list_of_nouns.extend([row_of_nouns])
                row_of_nouns  = []
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