def execute(df):
    return df.drop_duplicates(subset=["order_id"])