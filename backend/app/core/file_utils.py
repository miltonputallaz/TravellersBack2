import time
import os.path
from fastapi import UploadFile

file_path = "static/"

async def saveFileAndGetId(incomingFile: UploadFile, userId):
    timestamp = int(time.time())
    current_dir = os.path.dirname(__file__)  # Obtiene la ruta del archivo actual
    parent_dir = os.path.dirname(current_dir)  # Sube al directorio padre

    # Ruta de la carpeta statics
    statics_dir = os.path.join(parent_dir, 'statics')

    # Asegúrate de que la carpeta statics existe
    os.makedirs(statics_dir, exist_ok=True)

    filename, file_extension = os.path.splitext(incomingFile.filename)

    newFileName = f'{userId}_{timestamp}'

    # Ruta del archivo que quieres crear
    file_path = os.path.join(statics_dir, f'{newFileName}{file_extension}')

    # Crear y escribir en el archivo
    with open(file_path, 'wb+') as file:
        file.write(await incomingFile.read())
        file.flush()

    return f'{newFileName}{file_extension}'