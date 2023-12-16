"""This has pre-processing step to clean the text data.

AUTHOR: Matteo Paltenghi
"""

import os
import pandas as pd
from verbify_tts.utils import get_root_directory


def replace_acronyms(text):
    """Replace acronyms TPL with their hyphened version T-P-L."""
    # get all upper case words
    words = text.split()
    mapping_dict = dict()
    for i, word in enumerate(words):
        if len(word) > 2 and word.isupper():
            replacement_word = '-'.join(word.lower())
            mapping_dict[word] = replacement_word
    # replace all words in the mapping dict
    for key, value in mapping_dict.items():
        text = text.replace(key, value)
    return text


def replace_idioms(text):
    """Replace idioms such as "e.g." with "for example"."""
    df = pd.read_csv(
        os.path.join(get_root_directory(), "configuration/idioms.csv"),
        header=0, delimiter=",")
    for i, row in df.iterrows():
        text = text.replace(str(row["idiom"]), str(row["replacement"]))
    return text