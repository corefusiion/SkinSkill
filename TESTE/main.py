import requests

def fetch_data():
    # Simula um erro comum: esquecer de instalar requests ou a porta da API não estar funcionando
    print("Iniciando coleta de dados...")
    response = requests.get("http://localhost:9090/data")
    print(f"Dados recebidos: {response.json()}")

if __name__ == "__main__":
    fetch_data()
