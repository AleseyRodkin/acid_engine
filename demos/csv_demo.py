# Copyright (c) 2025 Alexey Rodkin. All rights reserved.
# Licensed under the Apache License, Version 2.0.

import csv
from acid_engine.core import Contract, QualityGate, QualityGateExceeded

UserContract = Contract(
    unique=True,
    ordered=True,
    validators=[
        lambda row: isinstance(row.get("age"), int) and 0 <= row["age"] <= 120,
        lambda row: "@" in row.get("email", "")
    ]
)

users = UserContract.create_container()
error_log = []
gate = QualityGate(users, max_error_rate=0.5,
                   mode="quarantine",
                   error_container=error_log,
                   collect_errors=True)

with open("sample.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        try:
            row["age"] = int(row["age"]) if row["age"].isdigit() else row["age"]
        except (ValueError, AttributeError):
            pass
        gate.add(row)

print("=== Принятые записи ===")
for item in users:
    print(item)

print("\n=== ErrorRecords ===")
for rec in gate.error_records:
    print(rec)