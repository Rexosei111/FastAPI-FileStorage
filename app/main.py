from fastapi import FastAPI, UploadFile, File, HTTPException, status
from deta import Deta
from deta.drive import DriveStreamingBody
from fastapi.responses import ORJSONResponse, StreamingResponse
from starlette.requests import Request
from starlette.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import shortuuid
from typing import Union
import time
import os
from dotenv import load_dotenv


load_dotenv()


app = FastAPI(
    title="File Storage",
    description="A service to handle media files both in development and production level",
    version="0.1.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


Project_key = os.getenv("PROJECT_KEY")

key_name = os.getenv("KEY_NAME")

key_description = os.getenv("KEY_DESCRIPTION")


deta = Deta(Project_key)

Photos = deta.Drive("images")


@app.get("/images/{name_of_file}")
async def Get_File(name_of_file: str) -> StreamingResponse:
    """

    Route to retrieve a specific file. \n

    The url format for this route is /images/{name_of_file_to_retrieve.file_extension}. \n

    This route returns a streaming Response of the file requested for.
    """

    try:

        file: DriveStreamingBody = Photos.get(name_of_file)

    except Exception:

        raise HTTPException(
            status=status.HTTP_404_NOT_FOUND, detail="Unable to Retrieve file"
        )

    return StreamingResponse(file.iter_chunks(1024), media_type="image/*")


@app.post("/upload")
async def File_Upload(
    file: UploadFile = File(...), request: Request = None
) -> ORJSONResponse:

    """This View accepts a file from the frontend, generate a unique name for it and upload it to Deta drive. \n

    A url to the uploaded file is generated and sent back to the frontend.
    """

    file_name: str = file.filename

    file_obj = file.file

    extention: str = file_name.split(".")[-1]

    unique_name: str = shortuuid.uuid()

    name: str = f"{unique_name}.{extention}"

    try:

        res = Photos.put(name, file_obj)

    except Exception:

        raise HTTPException(status_code=500, detail="Unable to Upload image")

    return {"link": request.url_for("Get_File", name_of_file=name)}


@app.get("/images")
async def Get_All_Images() -> ORJSONResponse:

    """This route returns all files found on the drive"""

    files = Photos.list()
    return files


if __name__ == "__main__":

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload="true")
