"""
LIMPIEZA DE ARCHIVOS CONFLICTIVOS
"""
import os

def remove_conflicting_files():
    files_to_remove = [
        # Archivos viejos de UI
        "infrastructure/ui/pygame_rendering_adapter.py",
        "infrastructure/ui/pygame_input_adapter.py",
        
        # Archivos temporales de pruebas
        "main_final.py",
        "minimal_working.py", 
        "simple_test.py",
        "fix_imports.py",
        "fix_all_imports.py",
        "cleanup.py",
        "cleanup_final.py",
        "cleanup_conflicts.py",  # Este mismo se elimina
    ]
    
    removed_count = 0
    for file_path in files_to_remove:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"🗑️ Eliminado: {file_path}")
            removed_count += 1
    
    # Crear __init__.py necesarios
    init_files = {
        "infrastructure/ui/__init__.py": '''from .input_service import InputService
from .rendering_service import RenderingService
from .game_loop import GameLoop

__all__ = [
    "InputService",
    "RenderingService", 
    "GameLoop"
]
''',
        "core/application/services/__init__.py": '''from .turn_service import TurnService

__all__ = [
    "TurnService"
]
'''
    }
    
    created_count = 0
    for file_path, content in init_files.items():
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"📁 Creado: {file_path}")
        created_count += 1
    
    print(f"\n🎯 {removed_count} archivos eliminados, {created_count} archivos creados")
    print("✅ Conflicto de imports resuelto")
    print("🚀 Ejecuta: python main.py")

if __name__ == "__main__":
    remove_conflicting_files()