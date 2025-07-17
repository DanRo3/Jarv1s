#!/usr/bin/env python3
"""
Script de configuración automatizada para Jarv1s
Instala dependencias, descarga modelos y configura el entorno
"""

import os
import sys
import subprocess
import urllib.request
from pathlib import Path
import shutil

def print_header(title):
    """Imprime un header bonito"""
    print("\n" + "=" * 60)
    print(f"🚀 {title}")
    print("=" * 60)

def run_command(cmd, description, check=True):
    """Ejecuta un comando con feedback"""
    print(f"\n📋 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=check)
        print(f"✅ {description} - Completado")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Error: {e}")
        return False

def check_system_dependencies():
    """Verifica dependencias del sistema"""
    print_header("VERIFICANDO DEPENDENCIAS DEL SISTEMA")
    
    dependencies = {
        "python3": "Python 3.11+",
        "pip": "Python Package Manager",
        "ffmpeg": "Audio Processing",
    }
    
    missing = []
    for cmd, desc in dependencies.items():
        if shutil.which(cmd) is None:
            print(f"❌ {desc} ({cmd}) - NO ENCONTRADO")
            missing.append(cmd)
        else:
            print(f"✅ {desc} ({cmd}) - OK")
    
    if missing:
        print(f"\n⚠️  Dependencias faltantes: {', '.join(missing)}")
        print("\nInstala las dependencias faltantes:")
        print("Ubuntu/Debian: sudo apt update && sudo apt install python3 python3-pip ffmpeg")
        print("macOS: brew install python ffmpeg")
        return False
    
    return True

def setup_virtual_environment():
    """Configura el entorno virtual"""
    print_header("CONFIGURANDO ENTORNO VIRTUAL")
    
    venv_path = Path(".venv")
    
    if venv_path.exists():
        print("✅ Entorno virtual ya existe")
        return True
    
    if not run_command("python3 -m venv .venv", "Creando entorno virtual"):
        return False
    
    print("✅ Entorno virtual creado")
    print("\n📝 Para activar el entorno virtual:")
    print("   Linux/macOS: source .venv/bin/activate")
    print("   Windows: .venv\\Scripts\\activate")
    
    return True

def install_python_dependencies():
    """Instala dependencias de Python"""
    print_header("INSTALANDO DEPENDENCIAS DE PYTHON")
    
    # Detectar si estamos en un entorno virtual
    in_venv = sys.prefix != sys.base_prefix
    pip_cmd = "pip" if in_venv else "pip3"
    
    if not in_venv:
        print("⚠️  No estás en un entorno virtual")
        print("   Recomendamos usar: source .venv/bin/activate")
        response = input("¿Continuar con instalación global? (y/N): ")
        if response.lower() != 'y':
            return False
    
    # Actualizar pip
    run_command(f"{pip_cmd} install --upgrade pip", "Actualizando pip")
    
    # Instalar dependencias
    if Path("requirements.txt").exists():
        return run_command(f"{pip_cmd} install -r requirements.txt", "Instalando dependencias desde requirements.txt")
    else:
        return run_command(f"{pip_cmd} install -e .", "Instalando proyecto en modo desarrollo")

def download_tts_models():
    """Descarga modelos TTS"""
    print_header("DESCARGANDO MODELOS TTS")
    
    models_dir = Path("models/tts")
    models_dir.mkdir(parents=True, exist_ok=True)
    
    model_files = [
        ("es_ES-sharvard-medium.onnx", "https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/sharvard/medium/es_ES-sharvard-medium.onnx"),
        ("es_ES-sharvard-medium.onnx.json", "https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/sharvard/medium/es_ES-sharvard-medium.onnx.json")
    ]
    
    for filename, url in model_files:
        file_path = models_dir / filename
        
        if file_path.exists():
            print(f"✅ {filename} - Ya existe")
            continue
        
        print(f"📥 Descargando {filename}...")
        try:
            urllib.request.urlretrieve(url, file_path)
            print(f"✅ {filename} - Descargado")
        except Exception as e:
            print(f"❌ Error descargando {filename}: {e}")
            return False
    
    return True

def setup_environment_file():
    """Configura archivo de entorno"""
    print_header("CONFIGURANDO ARCHIVO DE ENTORNO")
    
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if env_file.exists():
        print("✅ Archivo .env ya existe")
        return True
    
    if env_example.exists():
        shutil.copy(env_example, env_file)
        print("✅ Archivo .env creado desde .env.example")
        print("\n📝 Edita .env para personalizar tu configuración")
        return True
    else:
        print("❌ .env.example no encontrado")
        return False

def setup_frontend():
    """Configura el frontend si existe"""
    print_header("CONFIGURANDO FRONTEND")
    
    frontend_dir = Path("frontend")
    
    if not frontend_dir.exists():
        print("⚠️  Directorio frontend no encontrado - Saltando")
        return True
    
    if not (frontend_dir / "package.json").exists():
        print("⚠️  package.json no encontrado - Saltando")
        return True
    
    # Verificar si npm está disponible
    if shutil.which("npm") is None:
        print("❌ npm no encontrado - Instala Node.js")
        return False
    
    # Cambiar al directorio frontend
    original_dir = os.getcwd()
    os.chdir(frontend_dir)
    
    try:
        success = run_command("npm install", "Instalando dependencias del frontend")
        return success
    finally:
        os.chdir(original_dir)

def print_next_steps():
    """Imprime los próximos pasos"""
    print_header("¡CONFIGURACIÓN COMPLETADA!")
    
    print("🎉 Jarv1s está listo para usar")
    print("\n📋 Próximos pasos:")
    print("1. Activa el entorno virtual:")
    print("   source .venv/bin/activate")
    print("\n2. Configura LM Studio:")
    print("   - Abre LM Studio")
    print("   - Descarga un modelo (ej: Phi-3-mini-4k-instruct)")
    print("   - Inicia el servidor local en puerto 1234")
    print("\n3. Valida el sistema:")
    print("   python scripts/validate_system.py")
    print("\n4. Inicia el backend:")
    print("   uvicorn src.main:app --reload")
    print("\n5. Inicia el frontend (en otra terminal):")
    print("   cd frontend && npm run dev")
    print("\n6. ¡Abre tu navegador y comienza a conversar!")

def main():
    """Función principal"""
    print("🚀 CONFIGURACIÓN AUTOMATIZADA DE JARV1S")
    print("=" * 60)
    print("Este script configurará todo lo necesario para ejecutar Jarv1s")
    
    # Cambiar al directorio del proyecto
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    print(f"📁 Directorio de trabajo: {os.getcwd()}")
    
    steps = [
        ("Verificar dependencias del sistema", check_system_dependencies),
        ("Configurar entorno virtual", setup_virtual_environment),
        ("Instalar dependencias Python", install_python_dependencies),
        ("Descargar modelos TTS", download_tts_models),
        ("Configurar archivo de entorno", setup_environment_file),
        ("Configurar frontend", setup_frontend),
    ]
    
    failed_steps = []
    
    for step_name, step_func in steps:
        try:
            if not step_func():
                failed_steps.append(step_name)
        except KeyboardInterrupt:
            print("\n\n⚠️  Configuración interrumpida por el usuario")
            sys.exit(1)
        except Exception as e:
            print(f"\n❌ Error en {step_name}: {e}")
            failed_steps.append(step_name)
    
    if failed_steps:
        print(f"\n⚠️  Algunos pasos fallaron: {', '.join(failed_steps)}")
        print("Revisa los errores y ejecuta el script nuevamente")
        return 1
    else:
        print_next_steps()
        return 0

if __name__ == "__main__":
    sys.exit(main())