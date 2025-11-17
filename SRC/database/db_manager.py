import mysql.connector
import json

class DatabaseManager:
    def __init__(self):
        self.connection = mysql.connector.connect(
            host='localhost',
            user='onion_user',
            password='onion_password',
            database='onion_routing'
        )
        self.create_tables()
    
    def create_tables(self):
        cursor = self.connection.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS routers (
                router_id VARCHAR(50) PRIMARY KEY,
                public_key TEXT,
                host VARCHAR(100),
                port INT,
                registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS routing_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                source_router VARCHAR(50),
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                message_size INT,
                FOREIGN KEY (source_router) REFERENCES routers(router_id)
            )
        ''')
        
        self.connection.commit()
        cursor.close()
    
    def save_router(self, router_id, public_key, host='localhost', port=6000):
        cursor = self.connection.cursor()
        cursor.execute('''
            INSERT INTO routers (router_id, public_key, host, port)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE public_key=%s, host=%s, port=%s
        ''', (router_id, json.dumps(public_key), host, port, 
              json.dumps(public_key), host, port))
        self.connection.commit()
        cursor.close()