import os
import shutil
import tempfile
import cv2
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse

app = FastAPI()

@app.api_route("/", methods=["GET", "HEAD"])
def read_root():
    return {"status": "ok", "message": "Sonora OMR Backend running"}

@app.post("/process-sheet")
async def process_sheet(file: UploadFile = File(...)):
    with tempfile.TemporaryDirectory() as temp_dir:
        input_path = os.path.join(temp_dir, file.filename)
        resized_path = os.path.join(temp_dir, "input_resized.png")
        
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        try:
            # Optimización de imagen para Render Free
            img = cv2.imread(input_path)
            if img is None:
                raise HTTPException(status_code=400, detail="Imagen inválida")
            
            height, width = img.shape[:2]
            if width > 1000:
                new_width = 1000
                new_height = int(height * (1000 / width))
                img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_AREA)
            
            cv2.imwrite(resized_path, img)

            # Ejecutar oemer
            os.system(f"oemer '{resized_path}' -o '{temp_dir}'")

            midi_files = [f for f in os.listdir(temp_dir) if f.endswith(('.mid', '.midi'))]
            
            if not midi_files:
                raise HTTPException(status_code=500, detail="No se generó el archivo MIDI")

            midi_path = os.path.join(temp_dir, midi_files[0])
            
            return FileResponse(
                path=midi_path, 
                filename="output.mid", 
                media_type="audio/midi"
            )

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        )
