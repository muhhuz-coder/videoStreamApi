from datetime import datetime,UTC
import os
from venv import create
from dotenv import load_dotenv
from fastapi import FastAPI,Request,Form,UploadFile,File
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from storage3 import create_client
from supabase import Client, create_client
import httpx

load_dotenv()

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates= Jinja2Templates(directory="templates")

templates.env.globals.update(now=lambda:datetime.now(UTC))

SUPABASE_URL=os.getenv("SUPABASE_URL", "")
SUPABASE_ANON_KEY=os.getenv("SUPABASE_ANON_KEY", "")
SUPABASE_BUCKET=os.getenv("SUPABASE_BUCKET", "")

supabse: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)    

@app.get("/",response_class=HTMLResponse)
async def home(request:Request):
    videos=supabse.storage.from_(SUPABASE_BUCKET).list()
    return templates.TemplateResponse("home.html", {"request": request,"videos": videos})

@app.get("/videos/{video_name}",response_class=HTMLResponse)
async def get_video(video_name:str):
    video_url= supabse.storage.from_(SUPABASE_BUCKET).get_public_url(video_name)
    if not video_url:
        return {"error": "Video not found"}
    async def video_stream():
        async with httpx.AsyncClient() as client:
            async with client.stream('GET',video_url,headers={'Range':'bytes=0-'},timeout=None) as response:
                async for chunk in response.aiter_bytes():
                    yield chunk
    return StreamingResponse(video_stream(),media_type='video/mp4')

@app.get('/watch/{video_name}',response_class=HTMLResponse)
async def watch_video(request:Request,video_name:str):
    title= video_name.rsplit('.',1)[0].replace('_',' ')
    return templates.TemplateResponse("watch.html",{'request':request,"video_name":video_name,'title':title})    


@app.get("/upload",response_class=HTMLResponse)
async def upload_form(request: Request):
     return templates.TemplateResponse("upload.html",{"request":request})    
    
@app.post('/upload')
async def upload_video(request:Request,title:str=File(...),video_file: UploadFile= File(...)):
    contents = await video_file.read()
    file_extension = video_file.filename.split('.')[-1]
    file_name = f"{title.replace(' ','_')}.{file_extension}"

    existing_files = supabse.storage.from_(SUPABASE_BUCKET).list()
    existing_names = [f["name"] for f in existing_files]

    if file_name in existing_names:
        message="File already exists. Please rename or delete it first."
    else:
      try:
        res = supabse.storage.from_(SUPABASE_BUCKET).upload(file_name, contents)
        message="File uploaded successfully"
    
      except Exception as e:
        message="File uploaded failed"
        
    return templates.TemplateResponse("upload.html",{'request':request,'message': message})         