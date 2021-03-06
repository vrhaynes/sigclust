import numpy as np

from editquality.feature_lists import enwiki
from sigclust.sigclust import sigclust


def read_data(f, features, rids=False):
    """
    Expect f to have tsv format.

    Reads a set of features and a label from a file one row at a time.
    rids says to expect the first column to be id numbers.
    """
    # Implicitly splits rows on \n
    for line in f:
        # Splits columns on \t
        parts = line.strip().split("\t")

        if rids:
            rev_id = parts[0]
            parts = parts[1:]

        # All but the last column are feature values.
        values = parts[:-1]

        # Last column is a label
        label = parts[-1]

        feature_values = []
        for feature, value in zip(features, values):
            # Each feature knows its type and will perform the right conversion

            if feature.returns == bool:
                # Booleans are weird. bool("False") == True.
                # so you need to string match "True"
                feature_values.append(value == "True")
            else:
                feature_values.append(feature.returns(value))

        row = feature_values[:]
        row.append(label == "True")
        if rids:
            row.insert(0, int(rev_id))

        yield row


def get_mat(file_name, rids=True):
    """
    Read data in file_name into a np. array.

    When rids == False, assumes all columns of the file from file_name are
        feature values except for the last column, which is assumed to contain
        labels.  Returns two element tuple (values, labels).
    When rids == True, assumes in addition that the first column is rev_ids
        and returns a three element tuple (ids, values, labels).
    """

    f = open(file_name)

    rows = list(read_data(f, enwiki.damaging, rids))

    mat = np.array(rows).astype(float)

    # Last column is the label
    labels = mat[:, -1]
    result = mat[:, :-1]

    # If rids then expect first column to be rev_ids
    if rids:
        rid_col = result[:, 0]
        return rid_col, result[:, 1:], labels
    else:
        return result, labels
