from .importador_personagens import ImportadorDePersonagens

NODE_CLASS_MAPPINGS = {
    "ImportadorDePersonagens": ImportadorDePersonagens
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ImportadorDePersonagens": "Importador de Personagens"
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
