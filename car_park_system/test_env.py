from dotenv import load_dotenv
import os

# Load the .env file
load_dotenv()

# Print out environment variables to check
print("Host:", os.getenv("DB_HOST"))
print("User:", os.getenv("DB_USER"))
print("Password:", os.getenv("DB_PASSWORD"))
print("Database:", os.getenv("DB_NAME"))
