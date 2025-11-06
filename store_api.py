from flask import Flask, request
import threading
import sys


sys.path.append('api/associationWP')
sys.path.append('api/classificationWP')
sys.path.append('api/time_seriesWP')

gen_custom_products_run = False
time_series_products_run = False


app = Flask(__name__)


@app.route("/", methods=["get","post"])
def getHome():
    result = {}
    return result


@app.route("/genCustomProducts", methods=["post"])
def genCustomProducts():

    result = {}
    
    if (gen_custom_products_run == True):
        result = {"ok":False, "msg":"task already started"}
    else:
        result = {"ok":True, "msg":"task started, please wait 5 minutes and reload the page"}
        
        task_thread = threading.Thread(target=gen_custom_products_task)
        task_thread.start()
    return result

def gen_custom_products_task():

    print("=============== gen_custom_products_task started ==================")
    global gen_custom_products_run
    gen_custom_products_run = True
    
    try:
        from associationWP import start_generate_association_rules
        
        start_generate_association_rules()
        
        gen_custom_products_run = False

    except Exception as e:
        gen_custom_products_run = False
        print("an error occurred:", e)

    print("=============== gen_custom_products_task end ===================")


@app.route("/classificationWP", methods=["post"])
def classification():
    print('================  start classificationWP ==========================')
    
    result = {}
    
    try:
        from classificationWP import classificationWP

        classificationWP()

        result = {"ok":True}
        return result
    
    except Exception as e:
        print("an error occurred:", e)
        
        result = {"ok":False, "msg": e}
        return result
    


@app.route("/get_products_for_user", methods=["get"])
def get_products_for_user():
    user_id = request.args.get("user_id")
    limit = request.args.get("limit", type=int)

    print('======= get product for user =========')
    try:
        from find_products_for_customer import get_customer_products
        
        products_list = get_customer_products(user_id, limit)
        
        result = {"products_list": products_list, "ok":True}
    except Exception as e:
        print('an error occurred: ', e)
        result = {"ok":False}
    
    print('======= End get product for user =========')

    return result
    
@app.route("/time_seriesWP", methods=["post"])
def time_series():
    
    result = {}
    
    if (time_series_products_run == True):
        result = {"ok":False, "msg":"task already started"}
    
    else:    
        task_thread = threading.Thread(target=time_series_task)
        task_thread.start()
        result = {"ok":True, "msg":"task started"}
    return result


def time_series_task():
    global time_series_products_run
    time_series_products_run = True

    try:
        from time_seriesWP import time_seriesWP
        
        time_seriesWP()
        
        time_series_products_run = False
    
    except Exception as e:
        time_series_products_run = False
        print("حدث خطأ:", e)

@app.route("/draw_forecast", methods=["get","post"])
def draw_forecast():
   from draw_forecastWP import create_img
   img_src = create_img()
   return img_src

@app.route("/getState", methods=["get","post"])
def getState():
    
    result = {
        "gen_custom_products_run":gen_custom_products_run,
        "time_series_products_run":time_series_products_run,
        "ok":True
    }
    return result

@app.errorhandler(404)
def page_not_found(error):
    result = {"ok":False, "msg":"page not found"}
    return result
