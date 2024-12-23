import pytest
import json
from unittest.mock import patch, MagicMock
from lambda_function import create_user, read_user, update_user, delete_user

# Sample data for testing
sample_data = {
    "email": "test@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "password_hash": "hashedpassword123"
}

sample_email = "test@example.com"

# Mocks for database connection
@pytest.fixture
def mock_db_cursor():
    # Mock the MySQL cursor
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = (
        1,  # id
        "test@example.com",
        "John",
        "Doe",
        "2024-12-20",  # created_at
        "2024-12-20"   # updated_at
    )
    return mock_cursor

@pytest.fixture
def mock_db_connection(mock_db_cursor):
    # Mock the MySQL connection
    mock_conn = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_db_cursor
    return mock_conn


# Test for create_user
@patch("lambda_function.pymysql.connect")
def test_create_user(mock_db_connection):
    mock_db_connection.return_value = mock_db_connection
    response = create_user(sample_data)
    
    assert response["statusCode"] == 201
    assert "User created successfully." in response["body"]


# Test for read_user
@patch("lambda_function.pymysql.connect")
def test_read_user(mock_db_connection):
    mock_db_connection.return_value = mock_db_connection
    response = read_user(sample_email)
    
    assert response["statusCode"] == 200
    response_body = json.loads(response["body"])
    assert response_body["user"]["email"] == sample_email
    assert response_body["user"]["first_name"] == "John"
    assert response_body["user"]["last_name"] == "Doe"


# Test for update_user
@patch("lambda_function.pymysql.connect")
def test_update_user(mock_db_connection):
    mock_db_connection.return_value = mock_db_connection
    update_data = {
        "first_name": "Jane",
        "last_name": "Smith",
        "email": sample_email
    }
    
    response = update_user(sample_email, update_data)
    
    assert response["statusCode"] == 200
    assert "User updated successfully." in response["body"]


# Test for delete_user
@patch("lambda_function.pymysql.connect")
def test_delete_user(mock_db_connection):
    mock_db_connection.return_value = mock_db_connection
    response = delete_user(sample_email)
    
    assert response["statusCode"] == 200
    assert "User deleted successfully." in response["body"]


# Test for error handling (e.g., user not found)
@patch("lambda_function.pymysql.connect")
def test_read_user_not_found(mock_db_connection):
    mock_db_connection.return_value = mock_db_connection
    # Simulate a case where no user is found for the email
    mock_db_connection.cursor.return_value.__enter__.return_value.fetchone.return_value = None
    
    response = read_user("nonexistent@example.com")
    
    assert response["statusCode"] == 404
    assert "User not found" in response["body"]


@patch("lambda_function.pymysql.connect")
def test_create_user_missing_fields(mock_db_connection):
    mock_db_connection.return_value = mock_db_connection
    incomplete_data = {"email": "test@example.com"}  # Missing first_name, last_name, and password_hash
    
    response = create_user(incomplete_data)
    
    assert response["statusCode"] == 400
    assert "Missing required fields" in response["body"]

