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

def get_daily_sales_between_2_dates(startdate, enddate):
    df=pd.DataFrame(columns=['date','total'])
    sql='''SELECT left(date_created,10) as date , sum(product_net_revenue) as total
    FROM wp_wc_order_product_lookup 
    where date_created between (%s) and (%s)
    group by    date
    order by date'''
    param = (startdate, enddate)
    cursor.execute(sql, param)
    orders_results = cursor.fetchall()
    for order in orders_results:
        x={ "date":[order['date']], "total":[order['total']]}
        dfx=pd.DataFrame(x)
        df=pd.concat([df, dfx], ignore_index=True)
    return df

def get_last_date():
    from datetime import datetime
    sql='''SELECT left(max(date_created),10) as max_date FROM wp_wc_order_product_lookup'''
    cursor.execute(sql)
    results = cursor.fetchall()
    max=results[0]['max_date']
    max_datetime=datetime.strptime(max, '%Y-%m-%d')
    return max_datetime

from datetime import datetime
from datetime import timedelta

def time_seriesWP():
    mysql_connect()
    enddate=get_last_date()
    startdate=enddate-timedelta(days=60)
    enddate=enddate.strftime('%Y-%m-%d')
    startdate=startdate.strftime('%Y-%m-%d')
    df=get_daily_sales_between_2_dates(startdate, enddate)
    df['date'] = pd.to_datetime(df['date'])
    df=df.set_index("date")
    df = df.resample('D').mean()
    df['total']=df['total'].fillna(df['total'].mean())
    df=df.reset_index()
    from autots import AutoTS
    import warnings
    warnings.filterwarnings('ignore')
    forecast_length=10
    model = AutoTS(forecast_length=forecast_length, frequency='infer')
    model = model.fit(df, date_col='date', value_col='total')
    prediction = model.predict()
    forecast = prediction.forecast
    sql = '''
    DROP TABLE IF EXISTS custom_forecast
    '''
    cursor.execute(sql)
    sql='''
    CREATE TABLE custom_forecast
    ( ID INT NOT NULL AUTO_INCREMENT , 
    date datetime NOT NULL , 
    total float NOT NULL , 
    PRIMARY KEY (id)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    '''
    cursor.execute(sql)
    connection_mydb.commit()
    for index,row in forecast.iterrows():
        date=index.strftime('%Y-%m-%d %H:%M:%S')
        total=float(row['total'])
        sql = "INSERT INTO custom_forecast (date, total) VALUES (%s, %s)"
        params = (date, total)
        cursor.execute(sql, params)
        connection_mydb.commit()
    connection_mydb.close()