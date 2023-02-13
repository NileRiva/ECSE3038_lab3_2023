from fastapi import FastAPI,HTTPException,Request
from bson import ObjectId
import motor.motor_asyncio
from fastapi.middleware.cors import CORSMiddleware
import pydantic
import os
from dotenv import load_dotenv
from datetime import datetime


app = FastAPI()

load_dotenv() #Nile Code, loads things from the coding environment
client = motor.motor_asyncio.AsyncIOMotorClient(os.getenv("MONG0_CONNECTION_STRING"))#Attempt at hiding URL - Nile
db = client.tanks
db2 = client.profile

def currdatetime():
    dt=datetime.now()
    currdatetimestr= dt.strftime("%#d/%#m/%Y, %#I:%M:%S %p")#date fomatted exactly how you have it in the request
    return currdatetimestr

pydantic.json.ENCODERS_BY_TYPE[ObjectId]=str

origins = ["https://ecse3038-lab3-tester.netlify.app"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.post("/profile",status_code=201)
async def addprofile(request:Request):
    profiletemp = await request.json()
    profiletemp["last_updated"]= currdatetime()
    
    
    newprofile = await db2["profile"].insert_one(profiletemp)#Does insert_one have a return
    createdprofile = await db2["profile"].find_one({"_id": newprofile.inserted_id })
    return createdprofile

@app.get("/profile",status_code=200)#200 is Default though
async def getprofile(request:Request):
    userprofile = await db2["profile"].find().to_list(1)#parameter limits amount of objects
    if len(userprofile)==0:
        return None
    return userprofile[len(userprofile)-1]

@app.post("/data",status_code=201)
async def create_new_tank(request:Request):
    tank_object = await request.json()

    new_tank = await db["tanks"].insert_one(tank_object)#Does insert_one have a return
    created_tank = await db["tanks"].find_one({"_id": new_tank.inserted_id })
    return created_tank

@app.get("/data")
async def get_all_tanks():
    tanks = await db["tanks"].find().to_list(999)#parameter limits amount of objects
    return tanks

@app.get("/data/{id}")
async def get_one_tank_by_id(id: str):
    tank = await db["tanks"].find_one({"_id": ObjectId(id)})
    return tank

@app.patch("/data/{id}")
async def update_tank(id: str,request:Request):
    tank_object = await request.json()

    updated_tank= await db["tanks"].update_one({"_id": ObjectId(id)},{"$set": tank_object})
    patched_tank = await db["tanks"].find_one({"_id": ObjectId(id) }) #updated_tank.upserted_id
    if updated_tank.modified_count>=1: 
        return patched_tank
    raise HTTPException(status_code=304,detail="No Entity was Modified by this Request")

@app.delete("/data/{id}",status_code=204)
async def delete_tank(id: str):
    deleted_tank = await db["tanks"].delete_one({"_id": ObjectId(id)})

    if deleted_tank.deleted_count == 1:
        return {"Success":"Object Deleted"}
    else:
        raise HTTPException(status_code=400,detail="Entry does not exist")



