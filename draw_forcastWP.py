import mysql.connector
import pandas as pd
import os

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

def create_img():
    mysql_connect()
    import matplotlib.pyplot as plt
    plt.figure(figsize=(12,10))
    sql = 'SELECT * from custom_forecast'
    cursor.execute(sql)
    results = cursor.fetchall()
    df = pd.DataFrame(columns=['date', 'total'])
    for row in results:
        obj = {"date": row['date'], "total": row['total']}
        df = pd.concat([df, pd.DataFrame([obj])], ignore_index=True)
    plt.plot(df['date'], df['total'])
    plt.xlabel("Date")
    plt.ylabel("Expected Total")
    plt.title("Sales Forecast")
    connection_mydb.close()
    path = "output_img.png"
    plt.savefig(path, format='png')
    import base64
    with open(path, 'rb') as image_file:
        image_data = image_file.read()
        base64_image = base64.b64encode(image_data).decode('utf-8')
    return f"data:image/jpeg;base64,{base64_image}"
