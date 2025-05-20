"""
Script to create a new admin user with a properly hashed password.
Run this script to create or update the admin user.
"""
import bcrypt
import pymysql
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Database connection parameters
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = int(os.getenv('DB_PORT', 3306))
DB_NAME = os.getenv('DB_NAME', 'evoting_rmu')
DB_USER = os.getenv('DB_USER', 'root')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')

def create_admin_user(email, password, name):
    """Create a new admin user with a properly hashed password."""
    # Hash the password using bcrypt
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(password_bytes, salt).decode('utf-8')
    
    # Connect to the database
    connection = pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    
    try:
        with connection.cursor() as cursor:
            # Check if admin already exists
            cursor.execute("SELECT id FROM admins WHERE email = %s", (email,))
            admin = cursor.fetchone()
            
            if admin:
                # Update existing admin
                cursor.execute(
                    "UPDATE admins SET name = %s, password_hash = %s WHERE email = %s",
                    (name, password_hash, email)
                )
                print(f"Admin user '{email}' updated successfully.")
            else:
                # Create new admin
                cursor.execute(
                    "INSERT INTO admins (name, email, password_hash) VALUES (%s, %s, %s)",
                    (name, email, password_hash)
                )
                print(f"Admin user '{email}' created successfully.")
            
            # Commit the changes
            connection.commit()
            
            # Show the hashed password for reference
            print(f"Password hash: {password_hash}")
            
    finally:
        connection.close()

if __name__ == "__main__":
    # Admin details
    admin_email = "admin@rmu.edu.gh"
    admin_password = "admin123"
    admin_name = "Admin User"
    
    # Create or update admin user
    create_admin_user(admin_email, admin_password, admin_name)
    print(f"\nYou can now log in with:")
    print(f"Email: {admin_email}")
    print(f"Password: {admin_password}")
