import json
import re
from csv import DictWriter
from datetime import datetime, timezone, timedelta

CET = timezone(timedelta(hours=1))
CSV_DELIMITER = ","
NEWLINE_SYMBOL_SAFE_FOR_EXCEL = "    "


def serialize_workflow_to_csv(workflow_body, workflow_id: int):
    components = _extract_components(workflow_body)
    all_rows = []

    for component in components:
        all_rows.extend(_extract_rows_from_component(component))

    all_rows.sort(
        key=lambda r: (
            r["field_name"] == "" or r["field_name"] is None,  # nulls last
            r["field_name"] or "",
            -_agent_version_to_timestamp(r["agent_version"])
        )
    )

    collapsed_rows = _collapse_adjacent_keep_last(
        all_rows,
        key_fn=lambda r: ((r.get("field_name") or ""), r["prompt"])
    )

    timestamp = datetime.now().replace(microsecond=0).strftime("%Y-%m-%dT%Hh%Mm%Ss")
    csv_filename = f"Workflow_id_{workflow_id}_{timestamp}.csv"

    _write_csv(collapsed_rows, csv_filename)
    print(f"CSV created: {csv_filename} ({len(collapsed_rows)} rows)")


def _agent_version_to_timestamp(agent_version_iso):
    dt = datetime.fromisoformat(agent_version_iso)
    return dt.timestamp()


def _build_row(field_config, component_name, agent_version, fields_mapping):
    description = field_config.get("description", "")
    if not description:
        return None

    target_id = field_config.get("target_id")
    field_name = fields_mapping.get(target_id, "")

    return {
        "agent_name": component_name,
        "agent_version": agent_version,
        "prompt": _normalize_text(description),
        "field_name": field_name
    }


def _collapse_adjacent_keep_last(rows, key_fn):
    if not rows:
        return []

    result = []
    last = rows[0]
    last_key = key_fn(last)

    for current in rows[1:]:
        key = key_fn(current)
        if key != last_key:
            result.append(last)
        last = current
        last_key = key

    result.append(last)
    return result


def _convert_timestamp_to_iso(ts_str):
    ts_float = float(ts_str)

    dt = datetime.fromtimestamp(ts_float, tz=CET).replace(microsecond=0)
    dt_naive = dt.replace(tzinfo=None)

    return dt_naive.isoformat()


def _extract_components(workflow_body):
    components = workflow_body.get("data", {}).get("workflow", {}).get("components", [])
    if not components:
        components = workflow_body.get("components", [])
    if not components:
        components = workflow_body.get("workflow", {}).get("components", [])

    return components or []


def _extract_rows_from_component(component):
    rows = []

    component_name = component.get("name", "")
    model_group = component.get("modelGroup")
    if not model_group:
        return rows

    fields_mapping = {
        f["targetId"]: f["targetName"]
        for f in model_group.get("fieldLinks", [])
    }

    for model in model_group.get("models", []):
        rows.extend(
            _extract_rows_from_model(
                model,
                component_name,
                fields_mapping
            )
        )

    return rows


def _extract_rows_from_model(model, component_name, fields_mapping):
    rows = []

    updated_at = model.get("updatedAt")
    if not updated_at:
        return rows

    agent_version = _convert_timestamp_to_iso(updated_at)

    model_options = _parse_model_options(model.get("modelOptions", "{}"))
    mt_options = model_options.get("model_training_options")
    if not mt_options:
        return rows

    for fc in mt_options.get("field_configs", []):
        row = _build_row(
            fc,
            component_name,
            agent_version,
            fields_mapping
        )
        if row:
            rows.append(row)

    return rows


def _normalize_text(text: str) -> str:
    if not text:
        return ""

    text = text.replace("\r\n", NEWLINE_SYMBOL_SAFE_FOR_EXCEL)
    text = text.replace("\r", NEWLINE_SYMBOL_SAFE_FOR_EXCEL)
    text = text.replace("\n", NEWLINE_SYMBOL_SAFE_FOR_EXCEL)

    text = re.sub(r"[ \t]+", " ", text)

    return text.strip()


def _parse_model_options(model_options_str):
    try:
        return json.loads(model_options_str)
    except json.JSONDecodeError:
        return {}


def _write_csv(rows, csv_filename):
    with open(csv_filename, mode="w", newline="", encoding="utf-8") as f:
        writer = DictWriter(
            f,
            fieldnames=[
                "agent_name",
                "agent_version",
                "prompt",
                "field_name"
            ],
            delimiter=CSV_DELIMITER
        )
        writer.writeheader()
        writer.writerows(rows)
