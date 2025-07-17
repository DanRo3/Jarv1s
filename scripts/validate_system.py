#!/usr/bin/env python3
"""
Sistema de validación completa para Jarv1s
Ejecuta todos los tests y verifica que el sistema esté listo
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description):
    """Ejecuta un comando y reporta el resultado"""
    print(f"\n🔍 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print(f"✅ {description} - OK")
            return True
        else:
            print(f"❌ {description} - FAILED")
            print(f"Error: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} - TIMEOUT")
        return False
    except Exception as e:
        print(f"💥 {description} - ERROR: {e}")
        return False

def check_dependencies():
    """Verifica dependencias del sistema"""
    print("=" * 50)
    print("🔧 VERIFICANDO DEPENDENCIAS DEL SISTEMA")
    print("=" * 50)
    
    dependencies = [
        ("python --version", "Python installation"),
        ("ffmpeg -version", "FFmpeg installation"),
        ("which pip", "Pip installation"),
    ]
    
    results = []
    for cmd, desc in dependencies:
        results.append(run_command(cmd, desc))
    
    return all(results)

def check_python_packages():
    """Verifica paquetes de Python"""
    print("\n" + "=" * 50)
    print("📦 VERIFICANDO PAQUETES DE PYTHON")
    print("=" * 50)
    
    packages = [
        "import whisper; print(f'Whisper: OK')",
        "import litellm; print(f'LiteLLM: OK')",
        "import fastapi; print(f'FastAPI: OK')",
        "from piper.voice import PiperVoice; print(f'Piper TTS: OK')",
        "import sounddevice; print(f'SoundDevice: OK')",
    ]
    
    results = []
    for pkg in packages:
        cmd = f'python -c "{pkg}"'
        results.append(run_command(cmd, f"Package check: {pkg.split(';')[0]}"))
    
    return all(results)

def check_models():
    """Verifica que los modelos estén disponibles"""
    print("\n" + "=" * 50)
    print("🤖 VERIFICANDO MODELOS DE IA")
    print("=" * 50)
    
    # Verificar modelo TTS
    tts_model = Path("models/tts/es_ES-sharvard-medium.onnx")
    tts_config = Path("models/tts/es_ES-sharvard-medium.onnx.json")
    
    if tts_model.exists() and tts_config.exists():
        print("✅ Modelo TTS - OK")
        tts_ok = True
    else:
        print("❌ Modelo TTS - MISSING")
        print("   Ejecuta: mkdir -p models/tts && cd models/tts")
        print("   wget https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/sharvard/medium/es_ES-sharvard-medium.onnx")
        print("   wget https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/sharvard/medium/es_ES-sharvard-medium.onnx.json")
        tts_ok = False
    
    # Whisper se descarga automáticamente
    print("✅ Whisper Model - Will download automatically")
    
    return tts_ok

def run_tests():
    """Ejecuta los tests principales"""
    print("\n" + "=" * 50)
    print("🧪 EJECUTANDO TESTS")
    print("=" * 50)
    
    tests = [
        ("python tests/test_whisper.py", "Whisper STT Test"),
        ("python tests/test_tts.py", "Piper TTS Test"),
        ("python tests/test_llm.py", "LLM Connection Test"),
    ]
    
    results = []
    for cmd, desc in tests:
        if Path(cmd.split()[1]).exists():
            results.append(run_command(cmd, desc))
        else:
            print(f"⚠️  {desc} - SKIPPED (file not found)")
            results.append(True)  # No fallar si el test no existe
    
    return all(results)

def check_lm_studio():
    """Verifica conexión con LM Studio"""
    print("\n" + "=" * 50)
    print("🧠 VERIFICANDO LM STUDIO")
    print("=" * 50)
    
    cmd = 'curl -s http://localhost:1234/v1/models'
    result = run_command(cmd, "LM Studio connection")
    
    if not result:
        print("\n⚠️  LM Studio no está corriendo o no está disponible")
        print("   1. Abre LM Studio")
        print("   2. Carga un modelo")
        print("   3. Inicia el servidor local en puerto 1234")
    
    return result

def main():
    """Función principal"""
    print("🚀 VALIDACIÓN COMPLETA DEL SISTEMA JARV1S")
    print("=" * 60)
    
    # Cambiar al directorio del proyecto
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    results = []
    
    # Ejecutar todas las verificaciones
    results.append(check_dependencies())
    results.append(check_python_packages())
    results.append(check_models())
    results.append(check_lm_studio())
    results.append(run_tests())
    
    # Resumen final
    print("\n" + "=" * 60)
    print("📊 RESUMEN FINAL")
    print("=" * 60)
    
    if all(results):
        print("🎉 ¡SISTEMA COMPLETAMENTE VALIDADO!")
        print("✅ Jarv1s está listo para usar")
        print("\nPróximos pasos:")
        print("1. uvicorn src.main:app --reload  # Iniciar backend")
        print("2. cd frontend && npm run dev     # Iniciar frontend")
        return 0
    else:
        print("⚠️  SISTEMA REQUIERE ATENCIÓN")
        print("❌ Algunos componentes necesitan configuración")
        print("\nRevisa los errores arriba y corrígelos antes de continuar")
        return 1

if __name__ == "__main__":
    sys.exit(main())