import re
from flask import Flask,request,jsonify # For flask implementation
from bson import ObjectId # For ObjectId to work
from pymongo import MongoClient
from collections import defaultdict
import os
import json
from bson import json_util

app = Flask(__name__)

title = "Simple tag counter app"
heading = "Application write with flask and MongoDB"

client = MongoClient("mongodb://localhost/FlaskPythonTest")#host uri
db = client['toastapp'] #Select the database

def discountapply(price=None,no_item=None):
    price_dict ={
        "100":'3',
        "500":'5',
        "1000":'10'
    }
    item_dict ={
        "3":'3',
        "5":'10'
    }
    if price != None:
        price_discount = 0
        for pr,dis in price_dict.items():
            if pr>price:
                break
            else:
                price_discount = dis
    if no_item != None:
        item_discount = 0
        for it,dis in item_dict.items():
            if it>price:
                break
            else:
                item_discount = dis
    if price_discount > item_discount :
        final_discount = price_discount
    else:
        final_discount = item_discount  
    return final_discount
@app.route('/tablemanagement/<id>', methods = ['DELETE'])
def TableManagement(id):            #table deletion
    collection = db['Table'] #Select the collection name
    if request.method == 'GET':
        pass
    elif request.method == 'DELETE':
        key=id
        collection.delete_one(
            {"_id":ObjectId(key)}
            ) #delete specific table
        return {"Message":"Deleted successfully"}
    return {"Message":"Failed"}
@app.route('/table/add', methods = ['POST'])
def Table_add():
    collection = db['Table'] #Select the collection name
    if request.method == 'POST':
        record = json.loads(request.data)       #requesting data
        collection.insert_one(
            {"tablename":record['tablename']} 
            ) #adding table name in table document
        return {"Message":"Add Success"}        #success
    return {"Message":"Failed"}        #failed
@app.route('/Menu', methods=['POST','GET']) 
def Menu_add():         #adding menu
    collection = db['menu'] #Select the collection name
    if request.method == 'GET':
        DataDisplay=collection.find()       #find menu details
        json_docs = [json.dumps(doc, default=json_util.default) for doc in DataDisplay] #json conversion of data
        if json_docs:
            return jsonify(data=json_docs)  #return data if having more than one
        else:
            return {"Message":"No data"}    #not having more than one then it display no data message
    elif request.method == 'POST':
        record = json.loads(request.data)   #requesting data 
        collection.insert_one(
                {"menu_name":record['menu_name'],"menudata":record['menudata']}
             ) #adding menu details to menu table
        return {"Message":"Add Success"} #Return success 
    return {"Message":"Failed"} #retun failed if no method found

@app.route('/Menu/<menu_id>', methods=['GET','PUT','DELETE'])
def Menu_update(menu_id):   #menu get update and delete function
    collection = db['menu'] #Select the collection name
    if request.method == 'GET':
        DataDisplay = list(collection.find({"_id":ObjectId(menu_id)})) #data find specific based on id
        return {'Menu' : json.dumps({'data':DataDisplay}, default=json_util.default)} #return data specified
    elif request.method == 'PUT':
        record = json.loads(request.data)   #request data
        list(collection.update(
            {"_id":ObjectId(menu_id)}, {"$set":{"menu_name":record['menu_name'],"menudata":record['menudata']}})
            ) #update in database
        return {"Message":"Update Success"}    #return success after updating
    elif request.method == 'DELETE':
        key = menu_id
        collection.delete_one(
            {"_id":ObjectId(key)}
            ) #delete specific menu
        return {"Message":"Deleted successfully"}
    return {"Message":"Failed"}

@app.route('/Order/', methods=['POST'])
def order():
    collection = db['order']
    if request.method == 'POST':
        order_record = json.loads(request.data) #request data related order 
        discount = discountapply(order_record['price'],order_record['item_number'])
        collection.insert_one(
                {"ordername":order_record['ordername'],"tablename":order_record['tablename'],"price":order_record['price'],"item_number":order_record['item_number'],"discount":discount,"status":"placed"} 
                ) #updated in database
        return {"Message":"Add Success"}

    return {"Message":"Failed"}
@app.route('/Orderdisplay/<status>', methods=['GET'])
def order_status(status):
    collection = db['order']
    if request.method == 'GET':
        DataDisplay=list(collection.find({"status":status}))    #display data in related to order
        return {"Menu" : json.dumps({'data':DataDisplay}, default=json_util.default)} #display data after suceess
    return {"Message":"Failed"}
@app.route('/tableorder/change/<tb_order>', methods=['PATCH'])
def tableorder_change(tb_order):
    collection = db['order']
    if request.method == 'PATCH':
        record = json.loads(request.data) # requesting the data 
        list(collection.update(
            {"_id":ObjectId(tb_order)}, {"$set":{"tablename":record['tablename']}})
            ) #only updating in table name
        return {"Message":"Update Success"}
    return {"Message":"Failed"}
if __name__ == "__main__":
    app.run()