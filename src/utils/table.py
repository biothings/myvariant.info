from dataclasses import dataclass
from itertools import groupby
from typing import Callable


@dataclass
class TableColumn:
    """
    Configuration marker for each column in a tabular file.

    A TableColumn object indicates that a value from the named column must be transformed before its assignment to a destination field inside a JSON doc.

    E.g. TableColumn(name="AF", dest="allele_freq", transform=float) means that a value from the "AF" column must be cast to float and then be assigned to the
    "allele_freq" field inside its associated JSON doc.
    """
    name: str  # column name
    dest: str = None  # destination field name
    transform: Callable = None  # transforming function applied to the column values
    tag: str = None  # tagging columns that need special prior sanity check or post-processing

    @classmethod
    def identity_function(cls, value):
        return value

    def __post_init__(self):
        if self.dest is None:
            # This is very common practice of determining field name.
            # E.g. a value in column "SIFT_score" is often wrapped to field "sift.score" (dotfield)
            self.dest = self.name.lower().replace("_", ".")

        # Default transformation is identity function; therefore we don't have to check if self.transform is None.
        # The choice is made because most columns have transforming function in our application.
        if self.transform is None:
            self.transform = self.identity_function


def create_tag_column_map(columns: list[TableColumn]):
    """
    Map each tag to its associated column or columns.

    Args:
        columns: a list of TableColumn objects

    Returns:
        a dictionary of { <tag> : <list-of-columns> }
    """
    tagged_columns = sorted([c for c in columns if c.tag is not None], key=lambda c: c.tag)
    result = {tag: list(columns) for tag, columns in groupby(tagged_columns, lambda c: c.tag)}
    return result
