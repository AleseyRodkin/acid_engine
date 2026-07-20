def execute(df):
    df["order_id"] = df["order_id"].astype(int)
    df["price"] = df["price"].astype(float)
    return df