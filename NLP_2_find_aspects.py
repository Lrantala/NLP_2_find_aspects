import ast

import pandas as pd
pd.options.mode.chained_assignment = None
import logging
import csv
import os
import sys

COMBINATIONS4 = [("JJ", "NN","NN", "NN"),("RB", "JJ","NN", "NN"),("JJ", "JJ","NN", "NN"),("RB","JJ","JJ","NN"),("JJ","CC", "JJ", "NN")]
COMBINATIONS3 = [("NN","NN", "NN"),("JJ","NN", "NN"),("RB","JJ","NN"),("JJ","JJ", "NN"), ("NN", "CC", "NN")]
COMBINATIONS2 = [("NN", "NN"), ("JJ", "NN")]
ADJECTIVES = ["JJ", "JJR", "JJS"]
NOUNS = ["NN", "NNP", "NNPS", "NNS"]
ADVERBS = ["RB", "RBR", "RBS"]
VERBS = ["VB", "VBD", "VBG", "VBN", "VBN", "VBP", "VBZ"]
ADJECTIVE_PHRASES = [("RB"),("JJ"), ("RB", "RB", "JJ")]
SKIPPED_WORDS = ["None", "be"]


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
        print("Saved file: %s%s%s" % (filepath, name, ".csv"))
    except IOError as exception:
        print("Couldn't save the file. Encountered an error: %s" % exception)
    logging.debug("Finished writing: " + name)


def new_find_noun_phrases(raw_list):
    logging.debug("Entering find noun phrases")
    # old code
    # original_phrase_list = []
    # new code
    original_phrase_list = []
    original_lemmas_list = []
    related_opinion_words = []

    list_of_noun_phrases = []
    list_of_single_words = []
    list_of_grouped_words = []
    tagged_sentences = raw_list["formatted"]
    for j, sentence in enumerate(tagged_sentences):
        inclusion_check = False
        previous_word = None
        for i, word in enumerate(sentence):
            if i+1 < len(sentence):
                inclusion_check = False
                word1 = sentence[i]
                if any(word1[1] in wrd for wrd in ADJECTIVES + NOUNS + ADVERBS):
                    word2 = sentence[i+1]
                # This part checks for quadro-grams
                    if any(word2[1] in wrd for wrd in ADJECTIVES + NOUNS + ADVERBS):
                        if i + 3 < len(sentence):
                            word3 = sentence[i + 2]
                            word4 = sentence[i + 3]
                            for x1, x2, x3, x4 in COMBINATIONS4:
                                if x1 == word1[1] and x2 == word2[1] and x3 == word3[1] and x4 == word4[1]:
                                    list_of_grouped_words.append((word1, word2, word3, word4))
                                    inclusion_check = True
                                    list_of_single_words = find_related_opinion_words(i, i + 5, sentence)
                                    list_of_noun_phrases.append(list_of_grouped_words)
                                    original_phrase_list.append(raw_list["text"][j])
                                    original_lemmas_list.append(raw_list["formatted"][j])
                                    related_opinion_words.append(list_of_single_words)
                                list_of_grouped_words = []

                    if i + 3 >= len(sentence):
                        inclusion_check = False
                    # This part checks for tri-grams
                    if (i+2 < len(sentence)) and inclusion_check == False:
                        word3 = sentence[i + 2]
                        for x1, x2, x3 in COMBINATIONS3:
                            if x1 == word1[1] and x2 == word2[1] and x3 == word3[1]:
                                list_of_grouped_words.append((word1, word2, word3))
                                previous_word = word1
                                inclusion_check = True
                                # This part starts checking if the noun phrase is followed by
                                # a verb and then adjective.
                                list_of_single_words = find_related_opinion_words(i, i + 4, sentence)
                                list_of_noun_phrases.append(list_of_grouped_words)
                                original_phrase_list.append(raw_list["text"][j])
                                original_lemmas_list.append(raw_list["formatted"][j])
                                related_opinion_words.append(list_of_single_words)
                            list_of_grouped_words = []

                    if i+2 >= len(sentence):
                        inclusion_check = False
                # This part checks for bigrams
                if inclusion_check == False:
                    if previous_word == None:
                        for x1, x2 in COMBINATIONS2:
                            if x1 == word1[1] and x2 == word2[1]:
                                list_of_grouped_words.append((word1, word2))
                                list_of_single_words = find_related_opinion_words(i, i + 3, sentence)
                                list_of_noun_phrases.append(list_of_grouped_words)
                                original_phrase_list.append(raw_list["text"][j])
                                original_lemmas_list.append(raw_list["formatted"][j])
                                related_opinion_words.append(list_of_single_words)
                            list_of_grouped_words = []

                    elif not any(previous_word[1] in wrd for wrd in ADJECTIVES + NOUNS + ADVERBS):
                        for x1, x2 in COMBINATIONS2:
                            if x1 == word1[1] and x2 == word2[1]:
                                list_of_grouped_words.append((word1, word2))
                                list_of_single_words = find_related_opinion_words(i, i + 3, sentence)
                                list_of_noun_phrases.append(list_of_grouped_words)
                                original_phrase_list.append(raw_list["text"][j])
                                original_lemmas_list.append(raw_list["formatted"][j])
                                related_opinion_words.append(list_of_single_words)
                            list_of_grouped_words = []
                    else:
                        previous_word = None
        # This creates every sentence as its own list of lists
        # if len(list_of_grouped_words) != 0:
        #     list_of_noun_phrases.append(list_of_grouped_words)
        #     original_phrase_list.append(raw_list["text"][j])
        #     original_lemmas_list.append(raw_list["formatted"][j])
        #     related_opinion_words.append(list_of_single_words)
        # list_of_grouped_words = []
    # This returns a list, where every noun is its own list
    phrases_and_lemmas = pd.DataFrame()
    phrases_and_lemmas["related_opinion_words"] = pd.Series(related_opinion_words)
    phrases_and_lemmas["noun_phrases_tags"] = pd.Series(list_of_noun_phrases)
    phrases_and_lemmas["original_text"] = pd.Series(original_phrase_list)
    phrases_and_lemmas["original_lemmas"] = pd.Series(original_lemmas_list)
    return phrases_and_lemmas


def find_related_opinion_words(before_phrase, after_phrase, sentence):
    list_of_opinion_words = []
    counter = 0
    while after_phrase < len(sentence):
        if sentence[after_phrase][1] in ADJECTIVES + VERBS + ADVERBS:
            list_of_opinion_words.append(sentence[after_phrase])
        after_phrase += 1
    while counter < before_phrase:
        if sentence[counter][1] in ADJECTIVES + VERBS + ADVERBS:
            list_of_opinion_words.append(sentence[counter])
        counter += 1
    if len(list_of_opinion_words) != 0:
        return list_of_opinion_words
    else:
        return [("None", "None")]


def separate_individual_words(df):
    individual_words = df["noun_phrases_tags"]
    individual_scores = df["vad_scores_phrases"]
    single_aspect_words = []
    single_opinion_words = []
    list_of_aspects = []
    list_of_opinion = []
    for i, phrase in enumerate(individual_words):
        for j, word in enumerate(*phrase):
            if word[1] in ADJECTIVES + ADVERBS:
                single_opinion_words.append(individual_scores[i][j])
            elif word[1] in NOUNS:
                single_aspect_words.append(individual_scores[i][j])
        list_of_aspects.append(single_aspect_words)
        list_of_opinion.append(single_opinion_words)
        single_aspect_words = []
        single_opinion_words = []
    df["aspect_words"] = pd.Series(list_of_aspects)
    df["opinion_words"] = pd.Series(list_of_opinion)
    return df


def find_sentence_structures(raw_list):
    logging.debug("Entering find sentence structures.")
    list_of_sentences = []
    tagged_sentences = raw_list["formatted"]
    for j, sentence in enumerate(tagged_sentences):
        temp_sentence_list = []
        for i, word in enumerate(sentence):
            if word[2] != "punct":
                temp_sentence_list.append(word[1])
            else:
                list_of_sentences.append(temp_sentence_list)
    return list_of_sentences


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


def assign_vad_scores_for_adjectives(adjectives, score_list):
    logging.debug("Entering assign vad scores for adjectives.")
    adjective_scores = []
    all_scores = []
    for phrase in adjectives:
        i = 0
        while i < len(phrase):
            # The way to access the word in the list is through phrase[i][0]
            score = [item for item in score_list if phrase[i][0] in item]
            if len(score) != 0:
                # The * ensures that only the list contents from score are returned
                adjective_scores.append(*score)
            else:
                adjective_scores.append((phrase[i][0], 5.00, 5.00, 5.00))
            i += 1
        if len(adjective_scores) != 0:
            all_scores.append(adjective_scores)
        adjective_scores = []
    return all_scores
    # The first number in the score list is the number of the word, the second one is [0]
    # for name, [1] for valence, [2] for arousal, [3] for dominance

def calculate_new_vad_scores_for_phrases(noun_phrases, adjectives):
    logging.debug("Entering calculate new vad scores")
    phrase_scores = []
    original_scores = []
    new_adjectives = pd.Series.tolist(adjectives)
    for i, phrase in enumerate(noun_phrases):
        new_word = []
        valence = []
        arousal = []
        dominance = []
        adjectives = []
        for word, v, a, d in phrase:
            new_word.append(word)
            valence.append(v)
            arousal.append(a)
            dominance.append(d)
        for word, v, a, d in (new_adjectives[i]):
            if word not in SKIPPED_WORDS:
                if v < 4 or v > 6:
                    valence.append(v)
                    arousal.append(a)
                    dominance.append(d)
                elif a < 4 or a > 6:
                    valence.append(v)
                    arousal.append(a)
                    dominance.append(d)
                elif d < 4 or d > 6:
                    valence.append(v)
                    arousal.append(a)
                    dominance.append(d)
        new_string = ' '.join(new_word).lower()
        new_valence = float(format(sum(valence)/len(valence), '.2f'))
        new_arousal = float(format(sum(arousal)/len(arousal), '.2f'))
        new_dominance = float(format(sum(dominance)/len(dominance), '.2f'))
        original_scores.append(phrase)
        phrase_scores.append((new_string, str(new_valence), str(new_arousal), str(new_dominance)))
    df_scores = pd.DataFrame.from_records(phrase_scores, columns=("clean_phrase", "valence", "arousal", "dominance"))
    old_scores = pd.Series(original_scores)
    df_scores["single_words"] = old_scores.values
    return df_scores


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
            # This deletes determiners (the, a, an)
            if (word[1] == "DT"):
                pass
            else:
                if word2 == None:
                    formatted_list.append(word)
        # This creates every sentence as its own list of tuples
        formatted_list_by_sentence.append(formatted_list)
        formatted_list = []
    return formatted_list_by_sentence


def read_folder_contents(path_to_files):
    filelist = os.listdir(path_to_files)
    return filelist

def main(df_part, name, zipped_scores):
    logging.debug("Entering main")
    df = df_part

    # New version
    # This creates a new column, where the tags are shortened to basic forms.
    tagged_texts = df["lemma_tag_dep"]
    df["formatted"] = new_format_tags(tagged_texts)
    new_df = new_find_noun_phrases(df)
    # combined = (list(zip(original_phrases, noun_phrases)))
    new_df["related_opinion_words"] = assign_vad_scores_for_adjectives(new_df["related_opinion_words"], zipped_scores)
    new_df["vad_scores_phrases"] = assign_vad_scores(new_df["noun_phrases_tags"], zipped_scores)
    df_vad_scores = calculate_new_vad_scores_for_phrases(new_df["vad_scores_phrases"], new_df["related_opinion_words"])
    result = pd.concat([df_vad_scores, new_df], axis=1, sort=False)
    result = separate_individual_words(result)
    result = result[['clean_phrase', 'valence', 'arousal', 'dominance', 'aspect_words', 'opinion_words', 'related_opinion_words', 'original_text', 'original_lemmas']]
    vad_score_name = name + "_vad_scores"
    save_file(result, vad_score_name)

    # Extra step to find sentence structures
    # most_common_sentences = pd.DataFrame()
    # most_common_sentences["sentences"] = find_sentence_structures(df)
    # save_file(most_common_sentences, name + "_common_senteces")


def return_sys_arguments(args):
    if len(args) == 2:
        return args[1]
    else:
        return None


if __name__ == '__main__':
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
    warriner_scores = open_file("Short_Warriner.csv", "warriner")
    zip_scores = list(zip(warriner_scores["word"], warriner_scores["valence"], warriner_scores["arousal"],
                          warriner_scores["dominance"]))

    argument = return_sys_arguments(sys.argv)
    if argument is None:
        print("You didn't give an argument")
    elif os.path.isdir(argument):
        files = read_folder_contents(argument)
        print("Gave a folder: %s, that has %s files." % (argument, str(len(files))))
        x = 0
        for f in files:
            x += 1
            df = open_file(argument + "/" + f, "pandas")
            name = os.path.splitext(f)[0]
            print("Opened file: %s" % name)
            main(df, name, zip_scores)

    elif os.path.isfile(argument):
        df = open_file(argument, "pandas")
        name = os.path.splitext(argument)[0]
        main(df, name, zip_scores)

    else:
        print("You didn't give a file or folder as your argument.")



