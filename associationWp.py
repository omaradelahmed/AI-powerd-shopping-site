import mysql.connector

connection_mydb=None
cursor=None
def mysql_connect():
    global cursor,connection_mydb
    connection_mydb=mysql.connector.connect(host='localhost',user='root',password="",database='wp-ecommerce')
    cursor=connection_mydb.cursor(dictionary=True)


def get_product_name_from_id(connection_mydb,product_id):
    cursor=connection_mydb.cursor(dictionary=True)
    sql = "SELECT * FROM wp_posts WHERE ID=(%s)"
    id=(product_id,)
    cursor.execute(sql,id)
    results=cursor.fetchall()
    if len(results)>0:
        return results[0]['post_title']
    return "Unknown product"

import pandas as pd

def build_dataframe_associated_products(connection_mydb):
    df=pd.DataFrame(columns=[0,1,2,3,4,5,6,7,8,9])
    cursor=connection_mydb.cursor(dictionary=True)
    sql="SELECT * FROM wp_wc_order_stats order by order_id "
    cursor.execute(sql)
    results_orders=cursor.fetchall()
    for order in results_orders:
        order_id=order['order_id']
        sql="SELECT * FROM wp_wc_order_product_lookup where order_id=(%s)"
        id=(order_id,)
        cursor.execute(sql,id)
        results_products=cursor.fetchall()
        products_ids=[]
        for product in results_products:
            product_id=product['product_id']
            if product_id>0:
                df=pd.concat([df.pd.DataFrame([products_ids])],ignore_index=True)
            if len(products_ids)>1:
                    df=df.append([products_ids], ignore_index=True)
        return df
    
def prepare_transactions(df):
     df=df.T
     transactions=df.apply(lambda x:x.dropna().tolist())
     transactions_list=transactions.tolist()
     from mlxtend.preprocessing import TransactionEncoder
     te=TransactionEncoder()
     te_model=te.fit(transactions_list)
     rows=te_model.transform(transactions_list)
     df_transactions=pd.DataFrame(rows, columns=te_model.columns_)
     return df_transactions

def generate_association_rules(df_transactions,min_support,min_confidence):
     from mlxtend.frequent_patterns import apriori
     frequent_itemsets=apriori(df_transactions,min_support=min_support,use_columns=True)
     from mlxtend.frequent_patterns import association_rules
     rules = association_rules(frequent_itemsets,metric="confidence",min_threshold=min_confidence)
     rules=rules.sort_values(['confidence'],ascending=[False])
     return rules

def export_to_db(connection_mydb,rules):
     cursor=connection_mydb.cursor()
     sql='''
    DROP TABLE IF EXISTS  custom_products_association
    '''
     cursor.execute(sql)
     sql='''
    CREATE TABLE custom_products_association ( ID int(11) NOT NULL AUTO_INCREMENT,
      product_id_in int(11) NOT NULL,
      post_title_in text NOT NULL,
      product_id_out int(11) NOT NULL,
      post_title_out text NOT NULL,
      confidence double NOT NULL , PRIMARY KEY (ID))ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    '''
     cursor.execute(sql)
     connection_mydb.commit()
     for row in rules.itertuples():
          antecedents=row.antecedents
          consequents=row.consequents
          confidence=row.confidence*100
          for product1 in antecedents:
               post_title_in=get_product_name_from_id(connection_mydb,product=1)
               for product2 in consequents:
                    post_title_out=get_product_name_from_id(connection_mydb,product2)
                    sql='''SELECT * FROM custom_products_association where product_id_in=(%s) and
                    product_id_out=(%s) and confidence >= (%s) '''
                    params=(product1,product2,confidence)
                    cursor.execute(sql,params)
                    results=cursor.fetchall()
                    must_add=True
                    if results!=None and len(results)>0:
                         must_add=False
                    if must_add:
                         sql="INSERT INTO custom_products_association (product_id_in, post_title_in,product_id_out,post_title_out,confidence) VALUES (%s, %s,%s,%s,%s)"
                         val=(product1,post_title_in,product2,post_title_out,confidence)
                         cursor.execute(sql,val)
                         connection_mydb.commit()

def start_generate_association_rules():
     mysql_connect()
     df=build_dataframe_associated_products(connection_mydb)
     transactions_df=prepare_transactions(df)
     min_support=0.001
     min_confidence=0.001
     rules=generate_association_rules(transactions_df,min_support,min_confidence)
     export_to_db(connection_mydb,rules)
     connection_mydb.close()

                         








