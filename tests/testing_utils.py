def partial_dict_match(compare_dict: dict, target_dict: dict) -> bool:
    """Determine whether the given dictionary partially matches the
    target dictionary by verifying that all the keys in compare_dict
    are in target_dict and they have the same values.

    This can somewhat be thought of as a subset comparison for dicts, or
    if target_dict "contains" compare_dict.

    Paramters
    ---------
        compare_dict (dict) : The dictionary that we want to verify is
            completely contained in target_dict.
        target_dict (dict): The dictionary that we would expect
            compare_dict to be "inside" of.

    Returns
    -------
        (bool) : True if all of compare_dict's keys and their values are
            present in target_dict, otherwise False.

    Example
    -------
        >> dict_a = {'1': 1, '2': 2}
        >> dict_b = {'1': 1, '2': 2, '3': 3}
        >> dict_c = {'1': 2}
        >> dict_d = {'4': 4}
        >>
        >> partial_dict_match(dict_a, dict_b) # True
        >> partial_dict_match(dict_c, dict_b) # False
        >> partial_dict_match(dict_d, dict_b) # False
        >> partial_dict_match(dict_b, dict_a) # False
    """
    for key, value in compare_dict.items():
        if key not in target_dict:
            return False

        if value != target_dict[key]:
            return False

    return True


def partial_dict_list_match(
    compare_dict_list: list[dict], target_dict_list: list[dict]
) -> bool:
    """Determine whether each dictionary in the given list partially
    matches a target dictionary in the target list by verifying that all
    the keys in the first dict are in target_dict and they have the same
    values.

    This can somewhat be thought of as a subset comparison for dicts, or
    if target_dict_list "contains" a partial copy of each dict in
    compare_dict_list.

    Paramters
    ---------
        compare_dict (dict) : The dictionary that we want to verify is
            completely contained in target_dict.
        target_dict (dict): The dictionary that we would expect
            compare_dict to be "inside" of.

    Returns
    -------
        (bool) : True if all of compare_dict's keys and their values are
            present in target_dict, otherwise False.
    """
    for compare_dict in compare_dict_list:
        if not any(
            [
                partial_dict_match(compare_dict, target_dict)
                for target_dict in target_dict_list
            ]
        ):
            return False

    return True
