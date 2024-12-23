import sys
import logging
import pymysql
import json

# Setting up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Database configuration
DB_CONFIG = {
    "host": "database-1.czwg6qqq43qz.us-east-2.rds.amazonaws.com",
    "user": "admin",
    "passwd": "TryingRds_123",
    "db": "db",
    "connect_timeout": 5,
}

# Utility function for consistent CORS headers
def cors_headers():
    return {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE",
        "Access-Control-Allow-Headers": "Content-Type",
    }

# Utility function to establish a database connection
def get_db_connection():
    try:
        return pymysql.connect(**DB_CONFIG)
    except pymysql.MySQLError as e:
        logger.error("ERROR: Could not connect to MySQL instance.")
        logger.error(e)
        raise

# Utility function for consistent error responses
def error_response(status_code, message):
    return {
        "statusCode": status_code,
        "headers": cors_headers(),
        "body": json.dumps({"error": message}),
    }

# Create user
def create_user(data):
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            query = """
                INSERT INTO users (email, first_name, last_name, password_hash)
                VALUES (%s, %s, %s, %s)
            """
            cur.execute(query, (data['email'], data['first_name'], data['last_name'], data['password_hash']))
            conn.commit()
            return {
                "statusCode": 201,
                "headers": cors_headers(),
                "body": json.dumps({"message": "User created successfully."}),
            }
    except Exception as e:
        logger.error("Error while creating user: %s", e)
        return error_response(500, "An error occurred while creating the user.")
    finally:
        if conn:
            conn.close()

# Read user
def read_user(email):
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            query = "SELECT id, email, first_name, last_name FROM users WHERE email = %s"
            cur.execute(query, (email,))
            result = cur.fetchone()
            if result:
                user = {
                    "id": result[0],
                    "email": result[1],
                    "first_name": result[2],
                    "last_name": result[3],
                }
                return {
                    "statusCode": 200,
                    "headers": cors_headers(),
                    "body": json.dumps({"user": user}),
                }
            else:
                return error_response(404, "User not found.")
    except Exception as e:
        logger.error("Error while reading user: %s", e)
        return error_response(500, "An error occurred while fetching the user.")
    finally:
        if conn:
            conn.close()

# Update user
def update_user(email, data):
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            query = """
                UPDATE users
                SET first_name = %s, last_name = %s
                WHERE email = %s
            """
            cur.execute(query, (data['first_name'], data['last_name'], email))
            conn.commit()
            if cur.rowcount > 0:
                return {
                    "statusCode": 200,
                    "headers": cors_headers(),
                    "body": json.dumps({"message": "User updated successfully."}),
                }
            else:
                return error_response(404, "User not found or no changes made.")
    except Exception as e:
        logger.error("Error while updating user: %s", e)
        return error_response(500, "An error occurred while updating the user.")
    finally:
        if conn:
            conn.close()

# Delete user
def delete_user(email):
    try:
        conn = get_db_connection()
        with conn.cursor() as cur:
            query = "DELETE FROM users WHERE email = %s"
            cur.execute(query, (email,))
            conn.commit()
            if cur.rowcount > 0:
                return {
                    "statusCode": 200,
                    "headers": cors_headers(),
                    "body": json.dumps({"message": "User deleted successfully."}),
                }
            else:
                return error_response(404, "User not found.")
    except Exception as e:
        logger.error("Error while deleting user: %s", e)
        return error_response(500, "An error occurred while deleting the user.")
    finally:
        if conn:
            conn.close()

# Lambda handler function
def lambda_handler(event, context):
    logger.info("Processing request...")
    
    http_method = event.get("httpMethod")
    query_params = event.get("queryStringParameters", {})
    body = event.get("body")

    if body:
        body = json.loads(body)

    if http_method == "POST":
        return create_user(body)
    elif http_method == "GET" and "email" in query_params:
        return read_user(query_params["email"])
    elif http_method == "PUT" and "email" in query_params:
        return update_user(query_params["email"], body)
    elif http_method == "DELETE" and "email" in query_params:
        return delete_user(query_params["email"])
    else:
        return error_response(400, "Invalid HTTP method or parameters.")
