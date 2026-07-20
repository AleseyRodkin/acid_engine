import polars as pl
from acid_engine.core import Contract, Field
from acid_engine.adapters.polars import validate_polars

contract = Contract(
    schema={
        "id": Field(type=int, min=1),
        "email": Field.Email(),
        "age": Field(type=int, min=0, max=120)
    },
    unique=["id"]
)
contract.add_rule("age >= 18 if email.endswith('@company.com')")

df = pl.DataFrame({
    "id": [1, 2, 3, 4, 1, 5],
    "email": ["alice@company.com", "bob@mail.com", "bad", "eve@company.com", "dup@mail.com", "user@test.com"],
    "age": [25, 17, 30, 16, 40, 200]
})

valid, errors, summary = validate_polars(df, contract, max_error_rate=1.0, collect_errors=True)
print("Valid:", valid)
print("Errors:", errors)
print("Summary:", summary)
