import threading
import time
import random
from pymongo import MongoClient

# Configurações do MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['sensors_db']
collection = db['sensores']

# Função para simular a leitura de um sensor
def sensor_simulator(sensor_id, intervalo):
    while True:
        # Gerando uma temperatura aleatória entre 30 e 40 graus Celsius
        temperatura = random.uniform(30, 40)
        
        # Criando o documento para inserir no MongoDB
        sensor_data = {
            'sensor_id': sensor_id,
            'valorSensor': temperatura,
            'unidadeMedida': 'C',
            'sensorAlarmado': False
        }
        
        # Checando se a temperatura está acima do limite
        if temperatura > 38:
            sensor_data['sensorAlarmado'] = True
            print(f'Atenção! Temperatura muito alta! Verificar Sensor {sensor_id}')
        
        # Inserindo o documento no MongoDB
        collection.insert_one(sensor_data)
        
        # Exibindo a temperatura gerada no terminal
        print(f'Sensor {sensor_id}: {temperatura}°C')
        
        # Esperando o intervalo definido antes de gerar o próximo valor
        time.sleep(intervalo)

# Criando e iniciando três threads, cada uma simulando um sensor diferente
sensor_threads = []
for i in range(3):
    t = threading.Thread(target=sensor_simulator, args=(f'Temp{i+1}', 2))
    sensor_threads.append(t)
    t.start()

# Esperando as threads terminarem (nesse caso, elas rodam indefinidamente)
for t in sensor_threads:
    t.join()
