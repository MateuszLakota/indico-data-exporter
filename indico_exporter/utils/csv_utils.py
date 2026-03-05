from csv import DictWriter


def write_csv(rows, filename, fieldnames, delimiter=","):
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = DictWriter(
            f,
            fieldnames=fieldnames,
            delimiter=delimiter
        )

        writer.writeheader()
        writer.writerows(rows)
