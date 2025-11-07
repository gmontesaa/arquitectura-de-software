from abc import ABC, abstractmethod

class ProductLoader(ABC):
    @abstractmethod
    def load_products(self):
        pass

class ApiProductLoader(ProductLoader):
    def load_products(self):
        # Simulación de llamada a API externa
        import requests
        response = requests.get("https://api.example.com/products")
        return response.json()

class HardcodedProductLoader(ProductLoader):
    def load_products(self):
        # Datos quemados
        return [
            {"id": 1, "nombre": "Artesanía A", "precio": 100},
            {"id": 2, "nombre": "Artesanía B", "precio": 200},
        ]