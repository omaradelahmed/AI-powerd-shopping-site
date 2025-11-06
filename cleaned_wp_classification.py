import mysql.connector
import pandas as pd

connection_mydb = None
cursor = None

def mysql_connect():
    global cursor, connection_mydb
    connection_mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="wp-ecommerce"
    )
    cursor = connection_mydb.cursor(dictionary=True)

def get_product_categories(product_id):
    sql = '''SELECT wp_term_relationships.object_id, wp_term_taxonomy.term_id
FROM wp_term_relationships
INNER JOIN wp_term_taxonomy ON wp_term_relationships.term_taxonomy_id = wp_term_taxonomy.term_taxonomy_id
WHERE wp_term_taxonomy.taxonomy = 'product_cat' AND object_id = (%s)'''
    param = (product_id,)
    cursor.execute(sql, param)
    results = cursor.fetchall()
    ar_ids = [row['term_id'] for row in results]
    return ar_ids

def get_category_name_from_id(term_id):
    sql = '''SELECT wp_terms.* FROM wp_terms
LEFT JOIN wp_term_taxonomy ON wp_terms.term_id = wp_term_taxonomy.term_id
WHERE wp_term_taxonomy.taxonomy = 'product_cat' AND wp_terms.term_id = (%s)'''
    param = (term_id,)
    cursor.execute(sql, param)
    results = cursor.fetchall()
    if results and len(results) > 0:
        return results[0]['name']
    return "Unknown Category"

def construct_customers_data():
    sql = "SELECT DISTINCT(user_id) FROM wp_usermeta ORDER BY user_id"
    cursor.execute(sql)
    users_results = cursor.fetchall()
    df = pd.DataFrame(columns=['user_id', 'customer_id', 'country', 'age', 'gender', 'term_id', 'term_name', 'count_term_id'])
    for user in users_results:
        country = "UNKNOWN"
        age = 0
        gender = "UNKNOWN"
        user_id = user['user_id']
        customer_id = 0
        sql = "SELECT * FROM wp_usermeta WHERE user_id = (%s) AND meta_key = 'country'"
        param = (user_id,)
        cursor.execute(sql, param)
        result = cursor.fetchall()
        if result:
            country = result[0]['meta_value']
        sql = "SELECT * FROM wp_usermeta WHERE user_id = (%s) AND meta_key = 'age'"
        cursor.execute(sql, param)
        result = cursor.fetchall()
        if result:
            age = result[0]['meta_value']
        sql = "SELECT * FROM wp_usermeta WHERE user_id = (%s) AND meta_key = 'gender'"
        cursor.execute(sql, param)
        result = cursor.fetchall()
        if result:
            gender = result[0]['meta_value']
        sql = "SELECT * FROM wp_wc_customer_lookup WHERE user_id = (%s)"
        cursor.execute(sql, param)
        result = cursor.fetchall()
        if result:
            customer_id = result[0]['customer_id']
        sql = "SELECT * FROM wp_wc_order_product_lookup WHERE customer_id = (%s)"
        param = (customer_id,)
        cursor.execute(sql, param)
        results_orders = cursor.fetchall()
        categories_list = []
        for row in results_orders:
            customer_id = row['customer_id']
            product_id = row['product_id']
            term_ids = get_product_categories(product_id)
            for term_id in term_ids:
                add_1_category_customer(categories_list, customer_id, term_id)
        for k in range(len(categories_list)):
            for m in range(k + 1, len(categories_list)):
                if categories_list[k]['count'] < categories_list[m]['count']:
                    z = categories_list[k]
                    categories_list[k] = categories_list[m]
                    categories_list[m] = z
        if len(categories_list) > 0:
            term_id = categories_list[0]['term_id']
            count_term_id = categories_list[0]['count']
            term_name = get_category_name_from_id(term_id)
            x = {
                "user_id": user_id,
                "customer_id": customer_id,
                "country": country,
                "age": age,
                "gender": gender,
                'term_id': term_id,
                'term_name': term_name,
                'count_term_id': count_term_id
            }
            df = pd.concat([df, pd.DataFrame([x])], ignore_index=True)
    return df

def add_1_category_customer(category_customer_list, customer_id, term_id):
    item = find_item(category_customer_list, customer_id, term_id)
    item['count'] += 1

def find_item(category_customer_list, customer_id, term_id):
    for item in category_customer_list:
        if item['customer_id'] == customer_id and item['term_id'] == term_id:
            return item
    item = {"customer_id": customer_id, "term_id": term_id, "count": 0}
    category_customer_list.append(item)
    return item

def classificationWP():
    mysql_connect()
    print("building classifier started ...")
    df = construct_customers_data()
    from sklearn.preprocessing import LabelEncoder
    country_LE = LabelEncoder()
    gender_LE = LabelEncoder()
    df['country'] = country_LE.fit_transform(df['country'])
    df['gender'] = gender_LE.fit_transform(df['gender'])
    X = df[['country', 'age', 'gender']]
    y = df['term_id'].astype(int)
    from imblearn.over_sampling import RandomOverSampler
    oversample = RandomOverSampler()
    X, y = oversample.fit_resample(X, y)
    from sklearn.tree import DecisionTreeClassifier
    model = DecisionTreeClassifier()
    model.fit(X, y)
    import pickle
    filename = 'classification_model'
    pickle.dump(model, open(filename, 'wb'))
    cursor = connection_mydb.cursor(dictionary=True)
    sql = 'DROP TABLE IF EXISTS custom_country_codes'
    cursor.execute(sql)
    sql = '''CREATE TABLE custom_country_codes (
    ID int(11) NOT NULL AUTO_INCREMENT,
    code int(11) NOT NULL,
    country char(2) NOT NULL, PRIMARY KEY (ID)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;'''
    cursor.execute(sql)
    connection_mydb.commit()
    for country in country_LE.classes_:
        code = int(country_LE.transform([country])[0])
        sql = "INSERT INTO custom_country_codes (code, country) VALUES (%s, %s)"
        cursor.execute(sql, (code, country))
        connection_mydb.commit()
    cursor = connection_mydb.cursor(dictionary=True)
    sql = 'DROP TABLE IF EXISTS custom_gender_codes'
    cursor.execute(sql)
    sql = '''CREATE TABLE custom_gender_codes (
    ID int(11) NOT NULL AUTO_INCREMENT,
    code int(11) NOT NULL,
    gender char(10) NOT NULL, PRIMARY KEY (ID)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;'''
    cursor.execute(sql)
    connection_mydb.commit()
    for gender in gender_LE.classes_:
        code = int(gender_LE.transform([gender])[0])
        sql = "INSERT INTO custom_gender_codes (code, gender) VALUES (%s, %s)"
        cursor.execute(sql, (code, gender))
        connection_mydb.commit()
    connection_mydb.close()
    print("End building classifier ...")
