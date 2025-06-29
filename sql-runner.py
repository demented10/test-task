import pandas as pd
import psycopg2
import configparser
import os
import logging
from pathlib import Path
from datetime import datetime


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("sql_runner.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def load_config():
    config = configparser.ConfigParser()
    config.read('config.ini')
    
    required_db_keys = ['host', 'dbname', 'user', 'password','port']
    if 'database' not in config or not all(key in config['database'] for key in required_db_keys):
        raise ValueError("invalid database configuration")
    
    required_path_keys = ['querries_folder', 'output_excel']
    if 'path' not in config or not all(key in config['path'] for key in required_path_keys):
        raise ValueError("missing path configuration")
    
    return config

def get_sql_files(folder_path):
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"sql folder not found: {folder_path}")
    
    return sorted(
        Path(folder_path).glob('*.sql'),
        key=lambda x: x.name.lower()
    )

def execute_sql_file(connection, file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        with connection.cursor() as cursor:
            cursor.execute(sql_script)
            
            if cursor.description:
                columns = [col[0] for col in cursor.description]
                data = cursor.fetchall()
                logger.info(f"query returned {len(data)} rows: {file_path.name}")
                return columns, data
            else:
                connection.commit()
                logger.info(f"executed non-SELECT query: {file_path.name}")
                return None
                
    except Exception as e:
        connection.rollback()
        logger.error(f"error executing {file_path.name}: {str(e)}")
        return None

def save_to_excel(results, output_path):
    try:
        with pd.ExcelWriter(output_path, engine='auto') as writer:
            for file_name, (columns, data) in results.items():
                sheet_name = Path(file_name).stem[:31]
                df = pd.DataFrame(data, columns=columns)
                df.to_excel(writer, sheet_name=sheet_name, index=False)
        logger.info(f"excel file saved: {output_path}")
        return True
    except Exception as e:
        logger.error(f"failed to save excel: {str(e)}")
        return False

def main():
    try:
        # загрузка конфигурации
        config = load_config()
        db_config = config['database']
        scripts_folder = config['path']['querries_folder']
        output_excel = config['path']['output_excel']
        
        # имя файла для эксель таблицы с временой меткой
        output_path = Path(output_excel)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        final_output = output_path.parent / f"{output_path.stem}_{timestamp}{output_path.suffix}"
        

        conn = psycopg2.connect(
            host=db_config['host'],
            port=db_config['port'],
            dbname=db_config['dbname'],
            user=db_config['user'],
            password=db_config['password']
        )
        logger.info("connected to DB")
        
        sql_files = get_sql_files(scripts_folder)
        if not sql_files:
            logger.warning(f"no sql files founded {scripts_folder}")
            return
        
        logger.info(f"found {len(sql_files)} SQL files to execute")
        
        results = {}
        for sql_file in sql_files:
            result = execute_sql_file(conn, sql_file)
            if result:
                results[sql_file.name] = result
        
        # сохранение результатов в эксель
        if results:
            save_to_excel(results, final_output)
        else:
            logger.info("no SELECT queries with results found")
            
    except Exception as e:
        logger.exception(f"error: {str(e)}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()
            logger.info("db connection closed")

if __name__ == "__main__":
    main()