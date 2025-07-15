from datetime import datetime,UTC
import os
from venv import create
from dotenv import load_dotenv
from fastapi import FastAPI,Request,Form,UploadFile,File
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