from fastapi import FastAPI, HTTPException, UploadFile, Request, Form, File, Body, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, StreamingResponse, Response
from typing import Annotated, List
import uvicorn

from pymongo import MongoClient
import motor.motor_asyncio
from database import *
from models.model_train import *
from models.model_login import *
from bson.objectid import ObjectId

from fastapi.encoders import jsonable_encoder
from datetime import datetime, time, timedelta, date
from dotenv import dotenv_values
import os
import json

config = dotenv_values(".env")
DATABASE_URI = config.get("DATABASE_URI")
if os.getenv("DATABASE_URI"): 
    DATABASE_URI = os.getenv("DATABASE_URI") #ensures that if we have a system environment variable, it uses that instead

client = motor.motor_asyncio.AsyncIOMotorClient(DATABASE_URI)

database = client.todoapp
train_collection = database.trains
user_collection = database.logins

origins = ["*"] 
# This will eventually be changed to only the origins you will use once it's deployed, to secure the app a bit more.

app = FastAPI()  # activate  FastAPI app

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# convert list into tuple
def convert_list_tuple(list):
    return tuple(list)

# convert json to list
def convert_json_list(file_name):
    result_list =[]
    with open(file_name, mode='r') as f:
        json_data = json.load(f)
        for i in json_data:
            result_list.append(json_data[i])
        f.close()
    return (result_list)

# Daily Train Table setting
headings = ("User", "Date", "푸쉬업", "배운동","벽스퀏", "팔운동","상체들기","뒤꿈치들기","의자발차기","무릎벌리기","id","Actions")
data = () 


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/")
def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request} )

@app.get('/train')
async def get_train_data(request: Request):
    #results = await fetch_all_trains()
    trains = []   
    cursor = train_collection.find({})
    async for doc in cursor:
        id = str(doc['_id'])   #abstract _id from ObjectID and add id into doc
        doc.update({'id':id})
        train = TrainOut(**doc)
        trains.append(train)
    if not trains: return{"msg":"no records found"}
    return templates.TemplateResponse("traintable.html", {"request": request, "headings": headings, "data": trains}) 

@app.get('/train/{id}',response_model=Train)
async def get_train_data_byid(id: str):
    print(id)
    train = await train_collection.find_one({"_id": ObjectId(id)})
    if not train: raise HTTPException(400)
    return train

@app.post('/train')
async def add_train_data(
    date: str = Form(...),
    user: str = Form(...),
    pushup: int = Form(...),
    stomach: int = Form(...),
    squat: int = Form(...),
    arm: int = Form(...),
    uplift: int = Form(...),
    upheel: int = Form(...),
    kick_on_chair: int = Form(...),
    spreading_thigh: int = Form(...)
   ):
    date1 = datetime.now().date()
    print(date)
    data = {
        "date": date1,
        "user": user,
        "pushup": pushup,
        "stomach": stomach,
        "squat": squat,
        "arm": arm,
        "uplift": uplift,
        "upheel": upheel,
        "kick_on_chair":kick_on_chair,
        "spreading_thigh": spreading_thigh
    }  

    doc = dict(data)
    result = await train_collection.insert_one(doc)
    if not result: return("insetion error")
    
    return {"msg": 'data inserted'}

@app.delete("/deletetrain/{id}")
async def delete_train_byid(id: str):
    #result = await delete_train(id)
    print(id)
    result = await train_collection.delete_one({"_id": ObjectId(id)})
    print(result)
    if not result: raise HTTPException(400)
    return {"msg": 'data deleted'}

@app.get("/upload")
def root(request: Request):
    print("request received")
    return templates.TemplateResponse("upload.html", {"request": request} )

@app.get('/login')
def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request} )
  
@app.post('/login', response_model=Login)
async def login_process(id: Annotated[str, Form()], pw: Annotated[str, Form()]):
    print(id, pw)
    #result = await find_user(id)
    user = await user_collection.find_one({"id": id})
   
    if not user: raise HTTPException(400)
    if not user['pw'] == pw: raise HTTPException(400)
    return (user)

@app.post('/register')
async def user_register(id: Annotated[str, Form()], pw: Annotated[str, Form()]):
    user = {"id": id, "pw": pw}
    print(user)
    #result = await create_user(user)
    user = await user_collection.insert_one(user)
    if not user: raise HTTPException(400)
    return {"msg": "user is redistered"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True) 