def build_submissions_results_query(ids: list[int]) -> str:
    blocks = []
    for sid in ids:
        blocks.append(f"""
        s{sid}: submission(id: {sid}) {{
            createdAt
            inputFilename
            outputFiles {{
                filepath
            }}
        }}
        """)

    return f"""
    query GetMultipleSubmissionsResults {{
        {''.join(blocks)}
    }}
    """
