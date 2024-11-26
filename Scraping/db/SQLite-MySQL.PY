import sqlite3
import mysql.connector

# Conexão com o SQLite
sqlite_conn = sqlite3.connect("stations.db")
sqlite_cursor = sqlite_conn.cursor()

# Conexão com o MySQL
mysql_conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root123",
    database="galp_stations"
)
mysql_cursor = mysql_conn.cursor()

# Ler dados do SQLite
sqlite_cursor.execute("SELECT name, address FROM stations")
rows = sqlite_cursor.fetchall()

# Inserir dados no MySQL
for row in rows:
    mysql_cursor.execute(
        "INSERT INTO stations (name, address) VALUES (%s, %s)",
        row
    )

# Confirmar mudanças no MySQL
mysql_conn.commit()

# Fechar conexões
sqlite_conn.close()
mysql_conn.close()

print("Migração concluída com sucesso!")
