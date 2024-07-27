import math


def has_looped_item(input_list: list, loop_min_size: int, min_occurrences: int, margin_error: int) -> bool:
    for tested_item in input_list:
        item_indices = [index for index, item in enumerate(input_list) if item == tested_item]

        if len(item_indices) < min_occurrences:
            continue

        differences = [item_indices[i + 1] - item_indices[i] for i in range(len(item_indices) - 1)]
        if not all(difference > loop_min_size for difference in differences):
            continue

        if all(math.fabs(differences[0] - difference) < margin_error for difference in differences):
            return True

    return False
