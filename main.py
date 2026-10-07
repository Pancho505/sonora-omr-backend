import os
import shutil
import tempfile
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from pdf2image import convert_from_path
from PIL import Image

app = FastAPI(title="Free OMR API Server")

@app.api_route("/", methods=["GET", "HEAD"])
def read_root():
    return {"status": "ok", "message": "Sonora OMR Backend is running"}

@app.get("/")
def home():
    return {"status": "Servidor OMR activo y listo"}

@app.post("/process-sheet")
async def process_sheet(file: UploadFile = File(...)):
    # 1. Crear directorio temporal para procesar los archivos
    with tempfile.TemporaryDirectory() as temp_dir:
        input_path = os.path.join(temp_dir, file.filename)
        
        # Guardar el archivo recibido
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        image_path = input_path
        
        # 2. Si el archivo es un PDF, convertir la primera página a imagen PNG
        if file.filename.lower().endswith(".pdf"):
            images = convert_from_path(input_path, first_page=1, last_page=1)
            if not images:
                raise HTTPException(status_code=400, detail="No se pudo leer el archivo PDF")
            image_path = os.path.join(temp_dir, "converted_sheet.png")
            images[0].save(image_path, "PNG")

        # 3. Ejecutar la extracción OMR usando oemer (genera un archivo .mid)
        # Comando de consola: oemer /ruta/imagen.png -o /ruta/salida
        output_dir = os.path.join(temp_dir, "output")
        os.makedirs(output_dir, exist_ok=True)
        
        os.system(f"oemer '{image_path}' -o '{output_dir}'")
        
        # 4. Buscar el archivo .mid generado en la carpeta de salida
        generated_mid = None
        for f in os.listdir(output_dir):
            if f.endswith(".mid") or f.endswith(".midi"):
                generated_mid = os.path.join(output_dir, f)
                break

        if not generated_mid or not os.path.exists(generated_mid):
            raise HTTPException(
                status_code=500, 
                detail="El motor OMR no pudo extraer notas claras de esta partitura."
            )

        # 5. Mover el archivo MIDI a una ubicación persistente para enviarlo
        final_midi_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mid").name
        shutil.copy(generated_mid, final_midi_path)

        return FileResponse(
            path=final_midi_path,
            filename="sheet_music.mid",
            media_type="audio/midi"
        )