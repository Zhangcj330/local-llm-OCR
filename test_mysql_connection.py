
import mysql.connector
from mysql.connector import Error

def test_root_connection():
    """Test root user connection"""
    
    db_config = {
        'host': 'localhost',
        'user': 'root',
        'password': 'MyRootPass123',
        'port': 3306
    }
    
    try:
        # Attempt connection
        connection = mysql.connector.connect(**db_config)
        
        if connection.is_connected():
            db_info = connection.server_info
            print(f"✅ Successfully connected to MySQL server version: {db_info}")
            
            cursor = connection.cursor()
            
            # Show existing databases
            cursor.execute("SHOW DATABASES;")
            databases = cursor.fetchall()
            print(f"📁 Existing databases: {[db[0] for db in databases]}")
            
            return connection, cursor
            
    except Error as e:
        print(f"❌ Connection failed: {e}")
        return None, None

def setup_database_and_user():
    """Create database and user"""
    
    connection, cursor = test_root_connection()
    
    if not connection:
        return False
    
    try:
        # Create database
        cursor.execute("CREATE DATABASE IF NOT EXISTS medical_reports_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        print("✅ Database medical_reports_db created successfully")
        
        # Create user and grant privileges
        cursor.execute("CREATE USER IF NOT EXISTS 'ocr_user'@'%' IDENTIFIED BY 'ocr_password';")
        cursor.execute("GRANT ALL PRIVILEGES ON medical_reports_db.* TO 'ocr_user'@'%';")
        cursor.execute("FLUSH PRIVILEGES;")
        print("✅ User ocr_user created and granted privileges successfully")
        
        connection.commit()
        return True
        
    except Error as e:
        print(f"❌ Setup failed: {e}")
        return False
    
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("🔌 MySQL connection closed")

def test_ocr_user_connection():
    """Test OCR user connection"""
    
    db_config = {
        'host': 'localhost',
        'database': 'medical_reports_db',
        'user': 'ocr_user',
        'password': 'ocr_password',
        'port': 3306
    }
    
    try:
        # Attempt connection
        connection = mysql.connector.connect(**db_config)
        
        if connection.is_connected():
            db_info = connection.server_info
            print(f"✅ OCR user successfully connected to MySQL server version: {db_info}")
            
            cursor = connection.cursor()
            cursor.execute("SELECT DATABASE();")
            database_name = cursor.fetchone()
            print(f"✅ Current database: {database_name[0]}")
            
            # Test table creation permissions
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS test_table (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    test_field VARCHAR(255)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """)
            print("✅ Table creation permission test successful")
            
            # Clean up test table
            cursor.execute("DROP TABLE IF EXISTS test_table;")
            
            return True
            
    except Error as e:
        print(f"❌ OCR user connection failed: {e}")
        return False
    
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("🔌 MySQL connection closed")

if __name__ == "__main__":
    print("🏥 MySQL Connection Test")
    print("=" * 50)
    
    print("\n1. Testing Root connection and setting up database...")
    if setup_database_and_user():
        print("\n2. Testing OCR user connection...")
        test_ocr_user_connection()
    else:
        print("❌ Database setup failed")