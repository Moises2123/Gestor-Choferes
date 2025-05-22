import sqlite3
import csv
import shutil
from datetime import datetime
import os

# Respaldo a CSV
def backup_to_csv(db_path="choferes.db", backup_file="backup_choferes.csv"):
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    
    # Cambiar de "choferes" a "registros"
    cursor.execute("SELECT * FROM registros")
    records = cursor.fetchall()
    
    column_names = [description[0] for description in cursor.description]
    
    with open(backup_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(column_names)
        writer.writerows(records)

    connection.close()
    print(f"Copia de seguridad CSV creada: {backup_file}")


# Respaldo del archivo SQLite
def backup_database(db_path="choferes.db", backup_dir="backups/"):
    os.makedirs(backup_dir, exist_ok=True)  # Crear carpeta si no existe
    backup_file = f"{backup_dir}choferes_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    shutil.copy(db_path, backup_file)
    print(f"Copia de seguridad SQLite creada: {backup_file}")
