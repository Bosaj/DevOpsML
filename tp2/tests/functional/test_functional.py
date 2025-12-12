"""
Functional tests for Flask web application (Exercise 5)
"""
import pytest
from src.web_app import create_app


@pytest.fixture
def app():
    """Create and configure a test instance of the app"""
    app = create_app({"TESTING": True})
    yield app


@pytest.fixture
def client(app):
    """A test client for the app"""
    return app.test_client()


class TestHealthEndpoint:
    """Tests for /health endpoint"""
    
    def test_health_check(self, client):
        """Test health endpoint returns ok status"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json == {"status": "ok"}


class TestCreateUser:
    """Tests for POST /users endpoint"""
    
    def test_create_user_success(self, client):
        """Test creating a valid user"""
        response = client.post("/users", json={"name": "Alice", "age": 25})
        assert response.status_code == 201
        data = response.json
        assert "id" in data
        assert data["name"] == "Alice"
        assert data["age"] == 25
    
    def test_create_user_without_json(self, client):
        """Test creating user without JSON content type"""
        response = client.post("/users", data="not json")
        assert response.status_code == 400
        assert response.json == {"error": "JSON required"}
    
    def test_create_user_missing_name(self, client):
        """Test creating user without name"""
        response = client.post("/users", json={"age": 25})
        assert response.status_code == 400
        assert response.json == {"error": "name is required"}
    
    def test_create_user_empty_name(self, client):
        """Test creating user with empty name"""
        response = client.post("/users", json={"name": "   ", "age": 25})
        assert response.status_code == 400
        assert response.json == {"error": "name is required"}
    
    def test_create_user_invalid_age_type(self, client):
        """Test creating user with non-integer age"""
        response = client.post("/users", json={"name": "Bob", "age": "25"})
        assert response.status_code == 400
        assert response.json == {"error": "age must be a non-negative integer"}
    
    def test_create_user_negative_age(self, client):
        """Test creating user with negative age"""
        response = client.post("/users", json={"name": "Charlie", "age": -5})
        assert response.status_code == 400
        assert response.json == {"error": "age must be a non-negative integer"}
    
    def test_create_user_age_zero(self, client):
        """Test creating user with age 0"""
        response = client.post("/users", json={"name": "Baby", "age": 0})
        assert response.status_code == 201
        assert response.json["age"] == 0
    
    def test_create_user_name_with_spaces(self, client):
        """Test creating user with name containing spaces"""
        response = client.post("/users", json={"name": "  Alice Smith  ", "age": 30})
        assert response.status_code == 201
        assert response.json["name"] == "Alice Smith"


class TestListUsers:
    """Tests for GET /users endpoint"""
    
    def test_list_users_empty(self, client):
        """Test listing users when none exist"""
        response = client.get("/users")
        assert response.status_code == 200
        assert response.json == []
    
    def test_list_users_after_creation(self, client):
        """Test listing users after creating some"""
        client.post("/users", json={"name": "Alice", "age": 25})
        client.post("/users", json={"name": "Bob", "age": 30})
        
        response = client.get("/users")
        assert response.status_code == 200
        users = response.json
        assert len(users) == 2
        assert users[0]["name"] == "Alice"
        assert users[1]["name"] == "Bob"
    
    def test_list_users_returns_all_fields(self, client):
        """Test that list returns all user fields"""
        client.post("/users", json={"name": "Alice", "age": 25})
        
        response = client.get("/users")
        users = response.json
        assert len(users) == 1
        assert "id" in users[0]
        assert "name" in users[0]
        assert "age" in users[0]


class TestGetUser:
    """Tests for GET /users/<uid> endpoint"""
    
    def test_get_existing_user(self, client):
        """Test getting an existing user"""
        create_response = client.post("/users", json={"name": "Alice", "age": 25})
        user_id = create_response.json["id"]
        
        response = client.get(f"/users/{user_id}")
        assert response.status_code == 200
        user = response.json
        assert user["id"] == user_id
        assert user["name"] == "Alice"
        assert user["age"] == 25
    
    def test_get_nonexistent_user(self, client):
        """Test getting a user that doesn't exist"""
        response = client.get("/users/nonexistent-id")
        assert response.status_code == 404
        assert response.json == {"error": "not found"}
    
    def test_get_user_after_multiple_creations(self, client):
        """Test getting specific user when multiple exist"""
        client.post("/users", json={"name": "Alice", "age": 25})
        create_response = client.post("/users", json={"name": "Bob", "age": 30})
        bob_id = create_response.json["id"]
        
        response = client.get(f"/users/{bob_id}")
        assert response.status_code == 200
        assert response.json["name"] == "Bob"


class TestUpdateUser:
    """Tests for PUT /users/<uid> endpoint"""
    
    def test_update_user_success(self, client):
        """Test updating an existing user"""
        create_response = client.post("/users", json={"name": "Alice", "age": 25})
        user_id = create_response.json["id"]
        
        response = client.put(f"/users/{user_id}", json={"name": "Alice Smith", "age": 26})
        assert response.status_code == 200
        updated_user = response.json
        assert updated_user["id"] == user_id
        assert updated_user["name"] == "Alice Smith"
        assert updated_user["age"] == 26
    
    def test_update_user_partial_name(self, client):
        """Test updating only name field"""
        create_response = client.post("/users", json={"name": "Bob", "age": 30})
        user_id = create_response.json["id"]
        
        response = client.put(f"/users/{user_id}", json={"name": "Robert"})
        assert response.status_code == 200
        assert response.json["name"] == "Robert"
        assert response.json["age"] == 30
    
    def test_update_user_partial_age(self, client):
        """Test updating only age field"""
        create_response = client.post("/users", json={"name": "Charlie", "age": 35})
        user_id = create_response.json["id"]
        
        response = client.put(f"/users/{user_id}", json={"age": 36})
        assert response.status_code == 200
        assert response.json["name"] == "Charlie"
        assert response.json["age"] == 36
    
    def test_update_nonexistent_user(self, client):
        """Test updating a user that doesn't exist"""
        response = client.put("/users/nonexistent-id", json={"name": "Ghost", "age": 99})
        assert response.status_code == 404
        assert response.json == {"error": "not found"}
    
    def test_update_user_without_json(self, client):
        """Test updating without JSON content type"""
        create_response = client.post("/users", json={"name": "Charlie", "age": 35})
        user_id = create_response.json["id"]
        
        response = client.put(f"/users/{user_id}", data="not json")
        assert response.status_code == 400
        assert response.json == {"error": "JSON required"}
    
    def test_update_user_invalid_name(self, client):
        """Test updating with invalid name"""
        create_response = client.post("/users", json={"name": "David", "age": 40})
        user_id = create_response.json["id"]
        
        response = client.put(f"/users/{user_id}", json={"name": "   "})
        assert response.status_code == 400
        assert response.json == {"error": "invalid name"}
    
    def test_update_user_invalid_age(self, client):
        """Test updating with invalid age"""
        create_response = client.post("/users", json={"name": "Eve", "age": 22})
        user_id = create_response.json["id"]
        
        response = client.put(f"/users/{user_id}", json={"age": -10})
        assert response.status_code == 400
        assert response.json == {"error": "invalid age"}
    
    def test_update_user_invalid_age_type(self, client):
        """Test updating with non-integer age"""
        create_response = client.post("/users", json={"name": "Frank", "age": 50})
        user_id = create_response.json["id"]
        
        response = client.put(f"/users/{user_id}", json={"age": "fifty"})
        assert response.status_code == 400
        assert response.json == {"error": "invalid age"}


class TestDeleteUser:
    """Tests for DELETE /users/<uid> endpoint"""
    
    def test_delete_existing_user(self, client):
        """Test deleting an existing user"""
        create_response = client.post("/users", json={"name": "Alice", "age": 25})
        user_id = create_response.json["id"]
        
        response = client.delete(f"/users/{user_id}")
        assert response.status_code == 204
        assert response.data == b""
        
        get_response = client.get(f"/users/{user_id}")
        assert get_response.status_code == 404
    
    def test_delete_nonexistent_user(self, client):
        """Test deleting a user that doesn't exist"""
        response = client.delete("/users/nonexistent-id")
        assert response.status_code == 404
        assert response.json == {"error": "not found"}
    
    def test_delete_user_not_in_list(self, client):
        """Test that deleted user is not in list"""
        client.post("/users", json={"name": "Alice", "age": 25})
        create_response = client.post("/users", json={"name": "Bob", "age": 30})
        bob_id = create_response.json["id"]
        
        client.delete(f"/users/{bob_id}")
        
        response = client.get("/users")
        users = response.json
        assert len(users) == 1
        assert users[0]["name"] == "Alice"
    
    def test_delete_all_users(self, client):
        """Test deleting all users"""
        response1 = client.post("/users", json={"name": "Alice", "age": 25})
        response2 = client.post("/users", json={"name": "Bob", "age": 30})
        response3 = client.post("/users", json={"name": "Charlie", "age": 35})
        
        client.delete(f"/users/{response1.json['id']}")
        client.delete(f"/users/{response2.json['id']}")
        client.delete(f"/users/{response3.json['id']}")
        
        response = client.get("/users")
        assert response.json == []


class TestEndToEndScenarios:
    """End-to-end test scenarios"""
    
    def test_complete_crud_workflow(self, client):
        """Test complete Create-Read-Update-Delete workflow"""
        create_response = client.post("/users", json={"name": "Alice", "age": 25})
        assert create_response.status_code == 201
        user_id = create_response.json["id"]
        
        get_response = client.get(f"/users/{user_id}")
        assert get_response.status_code == 200
        assert get_response.json["name"] == "Alice"
        
        update_response = client.put(f"/users/{user_id}", json={"name": "Alice Smith", "age": 26})
        assert update_response.status_code == 200
        assert update_response.json["name"] == "Alice Smith"
        
        get_response2 = client.get(f"/users/{user_id}")
        assert get_response2.json["age"] == 26
        
        delete_response = client.delete(f"/users/{user_id}")
        assert delete_response.status_code == 204
        
        get_response3 = client.get(f"/users/{user_id}")
        assert get_response3.status_code == 404
    
    def test_multiple_users_management(self, client):
        """Test managing multiple users"""
        users_data = [
            {"name": "Alice", "age": 25},
            {"name": "Bob", "age": 30},
            {"name": "Charlie", "age": 35},
        ]
        
        user_ids = []
        for user_data in users_data:
            response = client.post("/users", json=user_data)
            user_ids.append(response.json["id"])
        
        list_response = client.get("/users")
        assert len(list_response.json) == 3
        
        client.put(f"/users/{user_ids[1]}", json={"age": 31})
        
        get_response = client.get(f"/users/{user_ids[1]}")
        assert get_response.json["age"] == 31
        
        client.delete(f"/users/{user_ids[0]}")
        
        list_response2 = client.get("/users")
        assert len(list_response2.json) == 2
