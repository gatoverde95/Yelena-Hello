import json
import subprocess
from pathlib import Path

# Define the config file path
CONFIG_FILE = Path.home() / ".config" / "yelena-hello" / "config.json"

def _check_systemd_status(service_name="yelena-hello.service"):
    """
    Verifica si el servicio de usuario systemd está habilitado (instalado y activo).
    """
    try:
        result = subprocess.run(["systemctl", "--user", "is-enabled", service_name], 
                                capture_output=True, text=True, check=False)
        return result.stdout.strip() == 'enabled'
    except Exception:
        return False

def load_config():
    """
    Load configuration settings from file.
    
    IMPORTANTE: Esta función NO detecta ni establece el idioma.
    La detección de idioma se hace exclusivamente en hello.py al iniciar.
    
    Returns:
        dict: Configuración cargada del archivo, o configuración por defecto si no existe.
    """
    
    config_exists = CONFIG_FILE.exists()
    
    # Solo detectamos autostart si el archivo no existe
    if config_exists:
        initial_autostart_state = True
    else:
        initial_autostart_state = _check_systemd_status()
    
    # Configuración por defecto: SOLO autostart
    # El idioma será detectado y añadido por hello.py
    default_config = {
        'autostart': initial_autostart_state,
    }
    
    try:
        CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        if config_exists:
            # Cargar configuración existente
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
                
                # Solo añadir claves faltantes del default (actualmente solo autostart)
                for key, value in default_config.items():
                    if key not in user_config:
                        user_config[key] = value
                
                return user_config
        else:
            # Primera vez: guardar config por defecto (sin idioma)
            save_config(default_config)
            return default_config
    except Exception as e:
        print(f"Error loading config: {e}")
        # En caso de error, devolver config por defecto
        return default_config

def save_config(config_data):
    """
    Save configuration settings to file.
    
    Args:
        config_data (dict): Configuración a guardar (puede incluir 'language' si fue añadido por hello.py)
    
    Returns:
        bool: True si se guardó correctamente, False en caso de error.
    """
    try:
        CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False

if __name__ == "__main__":
    # Test: cargar y mostrar configuración
    config = load_config()
    print(f"Loaded configuration: {config}")
    print(f"Config file location: {CONFIG_FILE}")