# src/main.py

import uvicorn
from .api.server import app  # El punto indica una importación relativa  # Importa la 'app' desde nuestro módulo de servidor
from dotenv import load_dotenv


# Llama a load_dotenv() ANTES de importar cualquier otro módulo de nuestro proyecto.
# Esto asegura que las variables de entorno estén disponibles para todos los servicios.
load_dotenv()
if __name__ == "__main__":
    print("Iniciando el servidor de Jarv1s...")
    # Ejecuta el servidor Uvicorn
    # --reload=True hace que el servidor se reinicie automáticamente cuando guardas cambios.
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)