# Auto-generated pipeline by AcidEngine
import pandas as pd
from acid_engine.core import Contract, Field

# Загрузка orders
orders = pd.read_csv('orders.csv')

# Загрузка customers
customers = pd.read_csv('customers.csv')

# Стадия: validate
def validate(df):
    # Join: customers
    customers = pd.read_csv('customers.csv')
    df = df.merge(customers, on='customer_email', how='left')
    # Cast: order_id to integer
    df['order_id'] = df['order_id'].astype(int)
    # Cast: price to float
    df['price'] = df['price'].astype(float)
    # Normalize: price
    df['price'] = (df['price'] - df['price'].mean()) / df['price'].std()
    # Enrich: phone
    df['phone'] = df['phone']
    # Enrich: segment
    df['segment'] = df['segment']
    # Filter: price > 0.0
    df = df[df['price'] > 0.0]
    # Deduplicate: order_id
    df = df.drop_duplicates(subset=['order_id'])
    return df

# Оркестратор
def main():
    df = orders.copy()
    df = validate(df)
    df.to_csv('validated_orders.csv', index=False)

if __name__ == '__main__':
    main()