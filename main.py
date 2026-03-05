import json
import re
from datetime import datetime

from indico import IndicoClient, IndicoConfig
from indico.client.request import GraphQLRequest
from indico.errors import IndicoDecodingError
from indico.queries import RetrieveStorageObject

from submission.csv_submission_result_serializer import build_submission_rows, collect_global_labels, \
    write_submission_csv
from submission.submission_result_query import build_submissions_results_query
from workflow.csv_workflow_serializer import serialize_workflow_to_csv
from workflow.workflow_query import WORKFLOW_QUERY

ALLIANZ_API_TOKEN = ""
ALLIANZ_URL = ""

AVIVA_API_TOKEN = ""
AVIVA_URL = ""

BATCH_SIZE = 10  # tweak between 3–20 safely
WORKFLOW_ID = 2
SUBMISSIONS_ID = [139, 140, 141, 145, 148, 150, 151, 152]


def serialize_workflow_response_to_csv(workflow_id: int):
    config = IndicoConfig(host=AVIVA_URL, api_token=AVIVA_API_TOKEN)
    client = IndicoClient(config)

    response = client.call(
        GraphQLRequest(query=WORKFLOW_QUERY, variables={"id": workflow_id})
    )

    serialize_workflow_to_csv(response, workflow_id)


def export_multiple_submissions(submission_ids: list[int]):
    config = IndicoConfig(host=ALLIANZ_URL, api_token=ALLIANZ_API_TOKEN)
    client = IndicoClient(config)

    all_rows = []
    all_submission_jsons = []

    for batch in _chunked(submission_ids, BATCH_SIZE):
        print(f"\n🔹 Processing batch: {batch}")

        query = build_submissions_results_query(batch)

        try:
            gql = client.call(GraphQLRequest(query=query))
        except Exception as e:
            print(f"⚠ Batch GraphQL failed: {e}")
            continue

        for alias, submission_property in gql.items():
            submission_id = int(alias[1:])  # remove "s"

            print(f"Processing submission {submission_id}...")

            if not submission_property:
                print(f"⚠ Submission {submission_id}: missing data")
                continue

            created_at = submission_property.get("createdAt")
            filename = submission_property.get("inputFilename")

            output_files = submission_property.get("outputFiles") or []
            if not output_files:
                print(f"⚠ Submission {submission_id}: no output files")
                continue

            storage_url = _get_submission_result_filepath(output_files, submission_id)
            if not storage_url:
                print(f"⚠ Submission {submission_id}: no matching JSON result")
                continue

            try:
                result = client.call(RetrieveStorageObject(storage_url))
            except IndicoDecodingError:
                print(f"⚠ Submission {submission_id}: storage missing")
                continue
            except Exception as e:
                print(f"⚠ Submission {submission_id}: storage error: {e}")
                continue

            try:
                if isinstance(result, bytes):
                    submission_json = json.loads(result.decode("utf-8"))
                elif isinstance(result, dict):
                    submission_json = result
                else:
                    raise TypeError(type(result))
            except Exception as e:
                print(f"⚠ Submission {submission_id}: JSON decode failed: {e}")
                continue

            all_submission_jsons.append(submission_json)

            create_datetime = None
            if created_at:
                try:
                    create_datetime = (
                        datetime.fromisoformat(created_at)
                        .replace(microsecond=0)
                        .isoformat()
                    )
                except Exception:
                    create_datetime = created_at

            try:
                rows = build_submission_rows(
                    submission_json=submission_json,
                    submission_id=submission_id,
                    filename=filename,
                    create_datetime=create_datetime,
                )
                all_rows.extend(rows)
            except Exception as e:
                print(f"⚠ Submission {submission_id}: row build failed: {e}")

    if not all_rows:
        print("❌ No data exported.")
        return

    all_labels = collect_global_labels(all_submission_jsons)

    csv_filename = datetime.now().strftime("%Y-%m-%dT%Hh%Mm%Ss.csv")
    write_submission_csv(all_rows, csv_filename, all_labels)

    print(f"\n✅ Export complete: {csv_filename}")


def _chunked(lst, size):
    for i in range(0, len(lst), size):
        yield lst[i:i + size]


def _get_submission_result_filepath(output_files, submission_id):
    canonical_pattern = rf"submission_{submission_id}_result\.json$"
    fallback_pattern = r"_result\.json$"

    fallback = None

    for f in output_files:
        filepath = f.get("filepath", "")

        if re.search(canonical_pattern, filepath):
            return filepath

        if re.search(fallback_pattern, filepath):
            fallback = filepath

    return fallback


if __name__ == "__main__":
    export_multiple_submissions(SUBMISSIONS_ID)
    serialize_workflow_response_to_csv(WORKFLOW_ID)
