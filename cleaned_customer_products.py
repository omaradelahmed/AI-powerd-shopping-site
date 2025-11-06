import pickle
import mysql.connector
import pandas as pd

connection_mydb = None
cursor = None

def get_category_code(filename, country, age, gender):
    loaded_model = pickle.load(open(filename, 'rb'))
    example = [country, age, gender]
    result = loaded_model.predict([example])
    return result[0]

def mysql_connect():
    global cursor, connection_mydb
    connection_mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="wp-ecommerce"
    )
    cursor = connection_mydb.cursor(dictionary=True)

def category_best_seller_products(category_id, n=3):
    cursor = connection_mydb.cursor(dictionary=True)
    sql = '''SELECT wp_term_taxonomy.term_id, wp_wc_order_product_lookup.product_id, SUM(wp_wc_order_product_lookup.product_qty) AS sumsales
FROM wp_wc_order_product_lookup
INNER JOIN wp_term_relationships ON wp_term_relationships.object_id = wp_wc_order_product_lookup.product_id
INNER JOIN wp_term_taxonomy ON wp_term_relationships.term_taxonomy_id = wp_term_taxonomy.term_taxonomy_id
WHERE wp_term_taxonomy.taxonomy = 'product_cat' AND wp_term_taxonomy.term_id = (%s)
GROUP BY wp_term_taxonomy.term_id, wp_wc_order_product_lookup.product_id
ORDER BY sumsales DESC'''
    param = (category_id,)
    cursor.execute(sql, param)
    results = cursor.fetchall()
    products_ids = []
    if results:
        i = 0
        while i < n and i < len(results):
            products_ids.append(results[i]['product_id'])
            i += 1
    return products_ids

def get_product_name(product_id):
    cursor = connection_mydb.cursor(dictionary=True)
    sql = "SELECT post_title FROM wp_posts WHERE ID = (%s)"
    cursor.execute(sql, (product_id,))
    results = cursor.fetchall()
    if len(results) > 0:
        return results[0]['post_title']
    return "Unknown Product"

def get_gender_code(gender):
    cursor = connection_mydb.cursor(dictionary=True)
    sql = "SELECT code FROM custom_gender_codes WHERE gender = (%s)"
    cursor.execute(sql, (gender,))
    result = cursor.fetchall()
    if result and len(result) > 0:
        return result[0]['code']
    else:
        return 0

def get_country_code(country):
    cursor = connection_mydb.cursor(dictionary=True)
    sql = "SELECT code FROM custom_country_codes WHERE country = (%s)"
    cursor.execute(sql, (country,))
    result = cursor.fetchall()
    if result and len(result) > 0:
        return result[0]['code']
    else:
        return 0

def get_customer_products(customer_id, n=3):
    mysql_connect()
    user_id = 0
    sql = "SELECT user_id FROM wp_wc_customer_lookup WHERE customer_id = (%s)"
    cursor.execute(sql, (customer_id,))
    result = cursor.fetchall()
    if result and len(result) > 0:
        user_id = result[0]['user_id']
    country = ""
    sql = "SELECT meta_value FROM wp_usermeta WHERE user_id = (%s) AND meta_key = 'country'"
    cursor.execute(sql, (user_id,))
    result = cursor.fetchall()
    if result and len(result) > 0:
        country = result[0]['meta_value']
    country_code = get_country_code(country)
    age = 0
    sql = "SELECT meta_value FROM wp_usermeta WHERE user_id = (%s) AND meta_key = 'age'"
    cursor.execute(sql, (user_id,))
    result = cursor.fetchall()
    if result and len(result) > 0:
        age = int(result[0]['meta_value'])
    gender = ""
    sql = "SELECT meta_value FROM wp_usermeta WHERE user_id = (%s) AND meta_key = 'gender'"
    cursor.execute(sql, (user_id,))
    result = cursor.fetchall()
    if result and len(result) > 0:
        gender = result[0]['meta_value']
    gender_code = get_gender_code(gender)
    category_code = get_category_code('classification_model', country_code, age, gender_code)
    products_ids = category_best_seller_products(int(category_code), n)
    products = []
    for pid in products_ids:
        product = get_product_name(pid)
        products.append(product)
    connection_mydb.close()
    return products_ids
