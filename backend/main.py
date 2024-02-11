
import json
import logging
import os
import tempfile
import threading
import time
import uuid
from fastapi.responses import StreamingResponse
import uvicorn
from asyncio import get_running_loop, Queue
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette import EventSourceResponse
from uuid import UUID
from squat import getStatsSquat, calcFormSquat, visualizeSquat
from lunge import getStatsLunge, calcFormLunge, visualizeLunge
from pushup import getStatsPushUp, calcFormPushUp, visualizePushUp
from utility import extractSkeleton


OUT_EXT = ".mp4"
OUT_MIME_TYPE = "video/mp4"

queues_lock: threading.Lock = threading.Lock()
queues: dict[UUID, Queue] = {}

videos: dict[UUID, tempfile._TemporaryFileWrapper] = {}

logger = logging.getLogger()
logging.basicConfig(level=logging.DEBUG)


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def analyze(id: UUID, exercise: int, extension: str, video: bytes):
    user_video_file = tempfile.NamedTemporaryFile(suffix=extension)
    result_video_file = tempfile.NamedTemporaryFile(suffix=OUT_EXT)
    with queues_lock:
        queues[id] = Queue(1)
    try:
        # Analyze video here
        print("writing vid")
        user_video_file.write(video)
        user_video_file.flush()
        
        file_path = user_video_file.name
       
        if (exercise == 0): #squat
            print(file_path)
            print("extracting")
            extractSkeleton(file_path, True)
            print("get stats")
            AI_PATH = "./Exemplar Squat 1.npy"
            values = getStatsSquat(file_path, file_path + ".npy", AI_PATH)
            feedback = calcFormSquat(values[0], values[1], values[2], values[3], values[4], values[5])
            minFrameNum = values[6]
            visualizeSquat(file_path, file_path + ".npy", AI_PATH, minFrameNum, result_video_file.name)

        elif (exercise == 1): #lunge
            print(file_path)
            print("extracting")
            extractSkeleton(file_path, False)
            print("get stats")
            AI_PATH = "./Exemplar Lunge 1.npy"
            values = getStatsLunge(file_path, file_path + ".npy", AI_PATH)
            feedback = calcFormLunge(values[0], values[1], values[2], values[3], values[4], values[5])
            minFrameNum = values[6]
            visualizeLunge(file_path, file_path + ".npy", AI_PATH, minFrameNum, result_video_file.name)
        elif (exercise == 2): #push up
            print(file_path)
            print("extracting")
            extractSkeleton(file_path, True)
            print("get stats")
            AI_PATH = "./Exemplar Push Up 1.npy"
            values = getStatsPushUp(file_path, file_path + ".npy", AI_PATH)
            feedback = calcFormPushUp(values[0], values[1], values[2])
            minFrameNum = values[3]
            visualizePushUp(file_path, file_path + ".npy", AI_PATH, minFrameNum, result_video_file.name)
        
        result_video_file.flush()
        # Done analyzing
        print('analyzed!')
        with queues_lock:
            # Replace the object with real results
            queues[id].put_nowait({ "result": "success", "feedback": feedback, "video_file": result_video_file })
    except Exception as e:
        logger.error(e)
        with queues_lock:
            # Send failure
            queues[id].put_nowait({ "result": "fail", "message": "Failed" })
    finally:
        user_video_file.close()
        with queues_lock:
            del queues[id]
            
def get_queue(id: UUID) -> Queue:
    logger.info(f"Getting queue {id}")
    with queues_lock:
        if id in queues:
            return queues[id]
        else:
            return None

def unique_uuid(start_id: UUID) -> UUID:
    with queues_lock:
        while start_id in queues:
            start_id = uuid.uuid4()

    return start_id

@app.post("/upload")
async def upload(req: Request, exercise: int):
    video_bytes = await req.body()
    
    if len(video_bytes) == 0:
        raise HTTPException(status_code=400, detail="Must upload a video")
    
    start_id = uuid.uuid4()
    id = await get_running_loop().run_in_executor(None, lambda: unique_uuid(start_id))
    
    extension = ".mp4"
    if req.headers.get('content-type') == "video/quicktime":
        extension = ".mov"
    
    get_running_loop().run_in_executor(None, lambda: analyze(id, exercise, extension, video_bytes))
    
    # Return id which client uses to check on the analyzing
    return { "id": id }

@app.get("/wait-for-analyze/{id}")
async def wait_for_analyze(id: UUID, request: Request):
    logger.info("waiting for analyze done")
    queue = await get_running_loop().run_in_executor(None, lambda: get_queue(id))
    
    async def event_generator():
        if queue is None:
            yield { "result": "fail", "message": "Failed" }
            return

        if await request.is_disconnected():
            logger.debug("Request disconnected")
            return

        result = await queue.get()
        
        if result["result"] == "fail":
            print(result)
            yield {
                "event": "message",
                "data": json.dumps(result)
            }
            return
        
        result_video_file = result["video_file"]
        print(result_video_file.name)
        videos[id] = result_video_file
        del result["video_file"]
        
        yield {
            "event": "message",
            "data": json.dumps(result)
        }

    return EventSourceResponse(event_generator())

@app.get("/result/{id}", response_class=StreamingResponse)
async def result(id: UUID):
    if id not in videos:
        raise HTTPException(status_code=404, detail="Video not found")
    
    def iterfile():
        try:
            with videos[id] as file_like:
                yield from file_like
        finally:
            videos[id].close()
            del videos[id]

    return StreamingResponse(iterfile(), media_type=OUT_MIME_TYPE)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
