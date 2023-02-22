"""
Utility functions to be used to help with backend operations.
"""
import json
from typing import Callable, Tuple


def dict_to_json(dictionary: dict, id_range: range) -> list[dict]:
    """Convert a given dictionary (from a pandas dataframe) to one that
    is in more standard JSON format.
    i.e - An array of objects (dicts) instead of mapping
    dictionary[key][id] = key_value for each object.

    Parameters
    ----------
        dictionary (dict) : A dictionary of the form:
            {col1_name: [row1,row2, ...], ...,
             coln_name:[row1, row2, ...]}
        id_range (range) : The range of values to iterate over; for a
            Pandas DataFrame, this would be the index.

    Returns
    -------
        jsonList (list[dict]) : A list of dictionaries corresponding to
            the standard JSON format. This can be thought of as a list
            of JSON objects, represented by dictionaries in Python.
    """
    json_list = []
    for i in id_range:
        object_dict = dict()
        for key in dictionary:
            object_dict[key] = dictionary[key][i]
        json_list.append(object_dict)

    return json_list


def endpoint_error_wrapper(endpoint_func: Callable) -> Callable:
    """Wrap the given endpoint in a try... except block to return a bad
    status number and JSON response containing the error message.

    Parameters
    ----------
        endpoint_func (Callable) : The endpoint to wrap in the block.

    Returns
    ----------
        (tuple[str, int]) : JSON of successful request OR JSON with the
        error message and status code.
    """

    def wrap_try(*args, **kwargs) -> Tuple[str, int]:
        try:
            return endpoint_func(*args, **kwargs)
        except Exception as e:
            return json.dumps(dict(message=str(e))), 500

    return wrap_try
