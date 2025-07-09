# tests/check_gpu.py
import torch

print("--- Diagnóstico de PyTorch y CUDA ---")
is_available = torch.cuda.is_available()
print(f"¿CUDA disponible?           : {is_available}")

if is_available:
    print(f"Número de GPUs detectadas   : {torch.cuda.device_count()}")
    print(f"Nombre de la GPU actual     : {torch.cuda.get_device_name(0)}")
    print(f"Versión de CUDA de PyTorch  : {torch.version.cuda}")
else:
    print("\nPyTorch no puede encontrar una GPU compatible con CUDA.")
    print("Asegúrate de haber instalado la versión de PyTorch para GPU.")
print("-------------------------------------")