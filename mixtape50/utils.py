import re


def clean_title(title):
    """
    Cleans title by performing the following transformations in order:
     - Remove substrings enclosed in (...) or [...] and preceding whitespace (using regex greedy matching)
     - Remove " - " and substring after
     - Remove " feat.", " ft(.)", or " featuring" and substring after

    https://stackoverflow.com/questions/14596884/remove-text-between-and
    """
    # (Greedy) replace substrings between (...) and []
    title = re.sub(r"\s+\(.+\)", "", title)
    title = re.sub(r"\s+\[.+\]", "", title)

    # Remove " - " and subsequent substring
    title = re.sub(r" - .*", "", title)

    # Remove " feat(.) ", " ft(.) ", or " featuring " (but not "feature") and
    # substring after
    title = re.sub(r"\W+(ft[:.]?|feat[:.]|featuring)\s.*", "", title)

    return title


def remove_punctuation(title):
    """
    Removes punctuation by performing the following transformations:
     - Delete XML escape sequences: &amp; &quot; &lt; &gt; &apos;
     - Replace "/", "//", etc. and surrounding whitespace with " " (in medley titles)
     - Replace "&" and surrounding whitespace with " and "
     - Remove the following characters from the string: !"#$%'‘’“”()*+,-.:;<=>?@[\\]^_—`{|}~
     - Strips surrounding whitespace
    """
    title = re.sub(r"&[amp|quot|lt|gt|apos];", "", title)
    title = re.sub(r"\s*\/+\s*", " ", title)
    title = re.sub(r"\s*&\s*", " and ", title)
    title = re.sub(r"[!\"#$%'‘’“”()*+,-.:;<=>?@[\\\]^_—`{|}~]", "", title)
    title = re.sub(r"\s{2,}", " ", title)
    return title.strip()
