import pandas as pd
import sqlparse
import re
import os

# Archivo SQL con el dump
SQL_FILE = "app/data/Dataset.sql"  # Ajusta esta ruta a la ubicación correcta de tu archivo

# Nombre de la tabla objetivo que se desea extraer
TARGET_TABLE = "accounting_account_balances"


def extract_table_data_from_sql_dump(sql_file, target_table):
    """
    Extrae los nombres de columnas (del CREATE TABLE) y los valores (del INSERT INTO)
    desde un archivo dump de MySQL, adaptado específicamente para el formato mostrado.
    """
    # Leer el contenido del archivo SQL completo
    try:
        with open(sql_file, "r", encoding="utf-8") as f:
            sql_content = f.read()
    except FileNotFoundError:
        print(f"Error: El archivo {sql_file} no existe.")
        return [], []
    except Exception as e:
        print(f"Error al leer el archivo SQL: {e}")
        return [], []

    # Extraer columnas del CREATE TABLE
    columns = []
    create_table_pattern = re.compile(rf"CREATE TABLE `?{target_table}`?\s*\((.*?)\);", re.DOTALL)
    create_match = create_table_pattern.search(sql_content)
    
    if create_match:
        print(f"🛠️ Detectado CREATE TABLE para: {target_table}")
        # Obtener el contenido entre paréntesis del CREATE TABLE
        create_content = create_match.group(1)
        
        # Dividir por líneas para procesar cada definición de columna
        column_lines = [line.strip() for line in create_content.split('\n') if line.strip()]
        
        for line in column_lines:
            # Ignorar líneas que no son definiciones de columnas (PRIMARY KEY, etc.)
            if line.startswith('`') and not line.upper().startswith(('PRIMARY', 'KEY', 'CONSTRAINT', 'UNIQUE', 'INDEX', 'FOREIGN')):
                # Extraer el nombre de la columna (está entre backticks)
                column_match = re.match(r'`([^`]+)`', line)
                if column_match:
                    columns.append(column_match.group(1))
        
        print(f"📊 Columnas extraídas: {len(columns)}")
    else:
        print(f"⚠️ No se encontró la definición CREATE TABLE para: {target_table}")
    
    # Extraer valores de INSERT INTO
    table_data = []
    insert_pattern = re.compile(rf"INSERT INTO `?{target_table}`?\s+VALUES\s+(.*?);", re.DOTALL)
    insert_matches = insert_pattern.finditer(sql_content)
    
    insert_count = 0
    for match in insert_matches:
        insert_count += 1
        values_text = match.group(1)
        
        # Extraer cada conjunto de valores (entre paréntesis)
        row_pattern = re.compile(r'\((.*?)\)', re.DOTALL)
        for row_match in row_pattern.finditer(values_text):
            row_values = []
            current_value = ""
            in_quotes = False
            in_parenthesis = 0
            
            # Parsear manualmente los valores respetando comillas y comas dentro de valores
            for char in row_match.group(1) + ',':  # Agregar coma al final para procesar el último valor
                if char == "'" and (not current_value or current_value[-1] != '\\'):
                    in_quotes = not in_quotes
                    current_value += char
                elif char == '(' and not in_quotes:
                    in_parenthesis += 1
                    current_value += char
                elif char == ')' and not in_quotes:
                    in_parenthesis -= 1
                    current_value += char
                elif char == ',' and not in_quotes and in_parenthesis == 0:
                    # Fin de un valor individual
                    processed_value = process_value(current_value.strip())
                    row_values.append(processed_value)
                    current_value = ""
                else:
                    current_value += char
            
            # Verificar que tengamos el número correcto de columnas
            if columns and len(row_values) == len(columns):
                table_data.append(row_values)
            elif row_values:  # Tenemos valores pero no coincide el número con las columnas
                print(f"⚠️ Advertencia: Conjunto de valores con longitud diferente. Columnas: {len(columns)}, Valores: {len(row_values)}")
    
    if insert_count > 0:
        print(f"📥 Detectados {insert_count} INSERTs para la tabla: {target_table}")
        print(f"✅ Datos extraídos: {len(table_data)} filas")
    else:
        print(f"⚠️ No se encontraron sentencias INSERT INTO para la tabla: {target_table}")
        
    return table_data, columns


def process_value(value):
    """
    Procesa un valor individual del SQL para convertirlo al tipo adecuado.
    """
    if value == 'NULL':
        return None
    elif value.startswith("'") and value.endswith("'"):
        return value[1:-1]  # Quitar comillas
    elif value.lower() == 'true':
        return True
    elif value.lower() == 'false':
        return False
    else:
        try:
            # Intentar convertir a número si es posible
            return float(value) if '.' in value else int(value)
        except ValueError:
            return value


def create_dataframe(data, columns):
    """
    Convierte los datos extraídos en un DataFrame preservando los tipos de datos originales.
    """
    if not data or not columns:
        print("⚠️ No hay datos o columnas para crear el DataFrame")
        return pd.DataFrame()
        
    try:
        # Crear DataFrame con los datos extraídos
        df = pd.DataFrame(data, columns=columns)
        
        # Convertir solo columnas que son claramente numéricas
        for col in df.columns:
            # Verificar si la columna parece ser numérica (>50% de valores son números)
            numeric_count = sum(1 for val in df[col] if isinstance(val, (int, float)) or 
                               (isinstance(val, str) and val.replace('.', '', 1).isdigit()))
            
            if numeric_count > len(df[col]) * 0.5:  # Si más del 50% son numéricos
                try:
                    df[col] = pd.to_numeric(df[col], errors="ignore")
                except:
                    pass  # Mantener como está si falla la conversión
            
            # Intentar convertir columnas que parecen fechas (tienen 'date', 'time', 'year' en su nombre)
            elif any(date_indicator in col.lower() for date_indicator in ['date', 'time', 'year', 'month', 'day']):
                try:
                    # Solo intentar convertir si al menos el 50% de los valores no son nulos
                    non_null_count = df[col].count()
                    if non_null_count > len(df[col]) * 0.5:
                        pd.to_datetime(df[col], errors="ignore")
                except:
                    pass  # Mantener como está si falla la conversión
        
        # Asegurarnos de que None no se convierte a 'None' sino que se mantiene como None/NaN
        for col in df.columns:
            if df[col].dtype == object:  # Solo para columnas de tipo objeto/string
                df[col] = df[col].where(pd.notna(df[col]), None)
        
        return df
    except Exception as e:
        print(f"Error al crear DataFrame: {e}")
        return pd.DataFrame()


# ------------------ Ejecución principal ------------------
if __name__ == "__main__":
    print(f"🔍 Buscando tabla '{TARGET_TABLE}' en el archivo '{SQL_FILE}'...")
    
    # Validar que el archivo exista
    try:
        with open(SQL_FILE, "r", encoding="utf-8") as f:
            pass
    except FileNotFoundError:
        print(f"Error: El archivo {SQL_FILE} no existe. Verifica la ruta.")
        exit(1)
    
    # Extrae datos y columnas desde el archivo SQL
    data, columns = extract_table_data_from_sql_dump(SQL_FILE, TARGET_TABLE)

    if data and columns:
        # Crea un DataFrame con los datos extraídos
        df = create_dataframe(data, columns)

        if not df.empty:
            # Muestra resumen
            print("\n✅ DataFrame creado con shape:", df.shape)
            print("\nPrimeras filas del DataFrame:")
            print(df.head())
            print("\nInformación de tipos de datos:")
            print(df.dtypes)

            # Obtener la ruta de la carpeta donde está el archivo SQL
            output_folder = os.path.dirname(SQL_FILE)
            output_file = os.path.join(output_folder, f"{TARGET_TABLE}.csv")
            
            # Guarda el DataFrame como CSV
            df.to_csv(output_file, index=False)
            print(f"\n💾 Datos guardados en {output_file}")
        else:
            print("⚠️ El DataFrame está vacío.")
    else:
        print("⚠️ No se extrajeron datos o columnas. Verifica que el nombre de la tabla sea correcto.")
        print(f"    La tabla buscada fue: '{TARGET_TABLE}'")