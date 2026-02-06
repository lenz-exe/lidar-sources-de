import json
from dataclasses import asdict


def to_dict_list(items: list) -> list[dict]:
    """
    Convert a list of dataclasses into a list of dictionaries.

    :param items: A list of dataclasses
    :return: A list of dictionaries
    """
    return [asdict(item) for item in items]


def to_json(items: list, path: str) -> None:
    """
    Convert a list of dataclasses into a json file.

    :param items: A list of dataclasses
    :param path: Path where to put the json file
    :return:
    """
    with open(path, "w", encoding="utf-8") as file:
        json.dump(to_dict_list(items), file, ensure_ascii=False, indent=2)
