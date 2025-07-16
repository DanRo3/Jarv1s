import subprocess
import os
import time
import sys
import signal

# --- Configuración ---
# Rutas relativas al script. Asumimos que este script está en la raíz de 'local-agent-suite'.
BACKEND_DIR = "."  # El directorio actual
FRONTEND_DIR = "./frontend" # Sube un nivel y entra en la carpeta del frontend

# Comandos a ejecutar
# Usamos sys.executable para asegurarnos de que se use el Python del venv actual
BACKEND_COMMAND = [sys.executable, "-m", "uvicorn", "src.main:app", "--reload", "--port", "8000"]
FRONTEND_COMMAND = ["bun", "run", "dev"]

# --- Función para imprimir con estilo ---
def print_status(service, message, color_code):
    """Imprime un mensaje con un prefijo de color."""
    # Códigos de color ANSI
    RESET = "\033[0m"
    COLOR = f"\033[{color_code}m"
    print(f"{COLOR}[{service.upper()}]{RESET} {message}")


# --- Script Principal ---
if __name__ == "__main__":
    # Verificamos si la carpeta del frontend existe
    if not os.path.isdir(FRONTEND_DIR):
        print_status("ERROR", f"No se encontró el directorio del frontend en '{FRONTEND_DIR}'. Asegúrate de que la ruta es correcta.", "91")
        sys.exit(1)

    backend_process = None
    frontend_process = None
    
    # Usamos un bloque try...finally para asegurarnos de que los procesos se limpian
    try:
        # --- Iniciar Backend ---
        print_status("LAUNCHER", f"Iniciando el backend en '{os.path.abspath(BACKEND_DIR)}'...", "96")
        # Popen inicia el comando en un nuevo proceso sin bloquear el script actual
        backend_process = subprocess.Popen(BACKEND_COMMAND, cwd=BACKEND_DIR)
        print_status("LAUNCHER", f"Backend iniciado con PID: {backend_process.pid}", "92")
        time.sleep(5) # Damos un momento para que el backend arranque antes de iniciar el frontend

        # --- Iniciar Frontend ---
        print_status("LAUNCHER", f"Iniciando el frontend en '{os.path.abspath(FRONTEND_DIR)}'...", "96")
        frontend_process = subprocess.Popen(FRONTEND_COMMAND, cwd=FRONTEND_DIR)
        print_status("LAUNCHER", f"Frontend iniciado con PID: {frontend_process.pid}", "92")

        print("\n" + "="*50)
        print_status("SYSTEM", "¡Jarv1s está completamente en línea!", "95")
        print_status("SYSTEM", "Backend API: http://localhost:8000", "94")
        print_status("SYSTEM", "Frontend UI: http://localhost:5173 (o la URL que muestre Vite)", "94")
        print_status("SYSTEM", "Presiona Ctrl+C en esta terminal para detener ambos servidores.", "93")
        print("="*50 + "\n")

        # Mantenemos el script principal vivo, esperando a ser interrumpido
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print_status("LAUNCHER", "\nDetectada interrupción (Ctrl+C). Apagando los servicios...", "93")
    
    finally:
        # --- Limpieza de Procesos ---
        # Esta sección se ejecuta siempre, tanto si el script termina bien o por un error.
        if frontend_process:
            print_status("LAUNCHER", f"Deteniendo el proceso del frontend (PID: {frontend_process.pid})...", "93")
            frontend_process.terminate()
            frontend_process.wait() # Espera a que el proceso termine realmente
            print_status("LAUNCHER", "Frontend detenido.", "92")

        if backend_process:
            print_status("LAUNCHER", f"Deteniendo el proceso del backend (PID: {backend_process.pid})...", "93")
            backend_process.terminate()
            backend_process.wait()
            print_status("LAUNCHER", "Backend detenido.", "92")
            
        print_status("SYSTEM", "Todos los servicios de Jarv1s se han detenido. ¡Hasta la próxima!", "95")