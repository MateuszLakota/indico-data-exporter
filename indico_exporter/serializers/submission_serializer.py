import re
from typing import Dict, Any, List

from indico_exporter.utils.csv_utils import write_csv
from indico_exporter.utils.text_utils import normalize_text

CSV_DELIMITER = ","
NEWLINE_SYMBOL_SAFE_FOR_EXCEL = "    "


def build_submission_rows(
        submission_json: Dict[str, Any],
        submission_id: int,
        filename: str,
        create_datetime: str,
        all_labels: List[str] | None = None,
) -> List[Dict[str, str]]:
    submission_results = submission_json.get("submission_results", [])
    if not submission_results:
        return []

    if all_labels is None:
        all_labels = _collect_original_labels(submission_results)

    column_map = {label: _to_snake_case(label) for label in all_labels}

    rows: List[Dict[str, str]] = []

    for submission in submission_results:

        row = {
            "submission_id": submission_id,
            "filename": filename,
            "create_datetime": create_datetime,
        }

        model_results = submission.get("model_results", {})
        original = model_results.get("ORIGINAL", {})
        final = model_results.get("FINAL", {})

        final_lookup = _build_lookup(final)
        original_lookup = _build_lookup(original)

        for label in all_labels:
            col = column_map[label]

            value = (
                    final_lookup.get(label)
                    or original_lookup.get(label)
                    or ""
            )

            row[col] = normalize_text(value, NEWLINE_SYMBOL_SAFE_FOR_EXCEL)

        rows.append(row)

    return _squash_rows_if_possible(rows)


def write_submission_csv(
        rows: List[Dict[str, str]],
        csv_filename: str,
        all_labels: List[str],
):
    column_map = {label: _to_snake_case(label) for label in all_labels}

    fieldnames = (
            ["submission_id", "filename", "create_datetime"]
            + [column_map[label] for label in all_labels]
    )

    write_csv(rows, csv_filename, fieldnames, CSV_DELIMITER)


def collect_global_labels(submissions_json: List[Dict[str, Any]]) -> List[str]:
    labels = set()

    for submission_json in submissions_json:
        submission_results = submission_json.get("submission_results", [])
        labels.update(_collect_original_labels(submission_results))

    return sorted(labels)


def _squash_rows_if_possible(rows: List[Dict[str, str]]) -> List[Dict[str, str]]:
    if len(rows) <= 1:
        return rows

    merged = rows[0].copy()

    for row in rows[1:]:

        for key, value in row.items():

            if key in ("submission_id", "filename", "create_datetime"):
                continue

            existing = merged.get(key, "")

            if not existing and value:
                merged[key] = value
                continue

            if existing == value:
                continue

            if existing and value and existing != value:
                return rows

    return [merged]


def _collect_original_labels(submissions: List[Dict[str, Any]]) -> List[str]:
    labels = set()

    for submission in submissions:

        original = submission.get("model_results", {}).get("ORIGINAL", {})

        for items in original.values():
            for item in items:

                label = item.get("label")
                if label:
                    labels.add(label)

    return sorted(labels)


def _build_lookup(section: Dict[str, Any]) -> Dict[str, str]:
    lookup = {}

    for items in section.values():
        for item in items:

            label = item.get("label")

            if label:
                lookup[label] = item.get("text") or ""

    return lookup


def _normalize_text(text: str) -> str:
    if not text:
        return ""

    text = text.replace("\r\n", NEWLINE_SYMBOL_SAFE_FOR_EXCEL)
    text = text.replace("\r", NEWLINE_SYMBOL_SAFE_FOR_EXCEL)
    text = text.replace("\n", NEWLINE_SYMBOL_SAFE_FOR_EXCEL)

    text = re.sub(r"[ \t]+", " ", text)

    return text.strip()


def _to_snake_case(label: str) -> str:
    label = label.lower()
    label = re.sub(r"[^\w\s]", "", label)
    label = re.sub(r"\s+", "_", label)
    label = re.sub(r"_+", "_", label)

    return label.strip("_")
