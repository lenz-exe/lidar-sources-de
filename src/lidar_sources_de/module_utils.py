import csv
import html
import json
from dataclasses import fields, is_dataclass
from typing import Type, TypeVar

import requests


def check_if_url_exists(url: str, timeout: int = 10) -> bool:
    """
    Check if a URL is reachable.

    :param url: A string URL.
    :param timeout: How long to wait for a response.
    :return: A boolean indicating if the URL is reachable.
    """
    try:
        response = requests.get(url, allow_redirects=True, timeout=timeout)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException:
        return False


def unescape_html(text: str) -> str:
    return html.unescape(text)


T = TypeVar("T")


def write_data_to_file(data_class: Type[T], data: list[T], output_path: str, file_format: str = "csv") -> None:
    """
    Write a list of dataclass instances into a CSV or JSON file.

    :param data_class: Dataclass type (used to generate headers for CSV)
    :param data: List of dataclass instances
    :param output_path: Output file path
    :param file_format: "csv" or "json"
    """
    if not is_dataclass(data_class):
        raise TypeError("data_class must be a dataclass type")

    if not data:
        raise ValueError("data list is empty")

    if file_format not in ("csv", "json"):
        raise ValueError('format must be "csv" or "json"')

    # check if all items have the correct type
    for item in data:
        if type(item) is not data_class:
            raise TypeError(f"Item {item} is not of type {data_class.__name__}")

    # prepare data as dict
    dict_list = []
    for item in data:
        row = {}
        for field_name in [f.name for f in fields(data_class)]:
            value = getattr(item, field_name)
            # Serializing lists and dictionaries
            if isinstance(value, (list, dict)):
                row[field_name] = value
            else:
                row[field_name] = value
        dict_list.append(row)

    if file_format == "csv":
        with open(output_path, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=dict_list[0].keys())
            writer.writeheader()
            for row in dict_list:
                # convert lists and dicts into json strings
                writer.writerow(
                    {k: json.dumps(v, ensure_ascii=False) if isinstance(v, (list, dict)) else v for k, v in row.items()}
                )
    else:  # JSON
        with open(output_path, "w", encoding="utf-8") as jsonfile:
            json.dump(dict_list, jsonfile, ensure_ascii=False, indent=4)
