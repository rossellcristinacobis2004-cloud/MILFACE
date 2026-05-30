import os
import sqlite3
import glob

# 1. Update Database
try:
    print("Updating MILFACES DB...")
    conn = sqlite3.connect("milfaces.db")
    cursor = conn.cursor()
    # Add columns if they don't exist
    try:
        cursor.execute("ALTER TABLE soldados ADD COLUMN sexo TEXT DEFAULT 'No especificado'")
        print("Column 'sexo' added.")
    except Exception as e:
        print(e)
    try:
        cursor.execute("ALTER TABLE soldados ADD COLUMN tipo_sangre TEXT DEFAULT 'O+'")
        print("Column 'tipo_sangre' added.")
    except Exception as e:
        print(e)
    conn.commit()
    conn.close()
    print("DB DB Update successful.")
except Exception as e:
    print(f"Error updating DB: {e}")

# 2. Reemplazar 'Registrar Soldado' por 'Registrar Personal Militar'
try:
    print("Updating UI Templates...")
    templates_path = os.path.join("templates", "*.html")
    for filepath in glob.glob(templates_path):
        with open(filepath, 'r', encoding='utf-8') as file:
            data = file.read()
        
        # Replace
        data = data.replace("Registrar Soldado", "Registrar Personal Militar")
        
        with open(filepath, 'w', encoding='utf-8') as file:
            file.write(data)
    print("Templates successfully updated.")
except Exception as e:
    print(f"Error updating templates: {e}")

print("Done.")
