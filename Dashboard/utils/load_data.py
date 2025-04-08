import pandas as pd
import sqlite3

def carregar_dados(caminho_db='C:/Users/louis/datatech/Database/walmart_fraudes.db'):
    conn = sqlite3.connect(caminho_db)

    # Carrega pedidos e itens faltantes
    orders = pd.read_sql_query("SELECT * FROM orders", conn)
    missing = pd.read_sql_query("SELECT * FROM missing_items", conn)

    # Processamento
    orders['order_amount'] = orders['order_amount'].astype(float)
    orders['date'] = pd.to_datetime(orders['date'])
    orders['delivery_hour_only'] = orders['delivery_hour'].apply(lambda x: int(x.split(':')[0]))
    orders['delivery_minute'] = orders['delivery_hour'].apply(lambda x: int(x.split(':')[1]))
    orders['delivery_second'] = orders['delivery_hour'].apply(lambda x: int(x.split(':')[2]))

    def categorize_time(hour):
        if 5 <= hour < 12:
            return 'Manhã'
        elif 12 <= hour < 18:
            return 'Tarde'
        else:
            return 'Noite'

    orders['periodo'] = orders['delivery_hour_only'].apply(categorize_time)
    orders['total_items'] = orders['items_delivered'] + orders['items_missing']
    orders['missing_ratio'] = orders['items_missing'] / orders['total_items']

    # Itens faltantes detalhados
    missing['itens_faltantes'] = missing[['product_id_1', 'product_id_2', 'product_id_3']].notnull().sum(axis=1)
    orders = orders.merge(missing[['order_id', 'itens_faltantes']], on="order_id", how="left")
    orders['itens_faltantes'] = orders['itens_faltantes'].fillna(0).astype(int)

    # Renomeia para compatibilidade
    df = orders.rename(columns={
        "order_id": "pedido_id",
        "driver_id": "driver_id",
        "region": "regiao",
        "items_delivered": "itens_entregues"
    })

    conn.close()
    return df
