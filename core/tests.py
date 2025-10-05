import unittest
from sqlmodel import create_engine, Session, SQLModel, select
from sqlmodel.pool import StaticPool
from fastapi.testclient import TestClient
from core.app import app
from core.database import get_session
from core.models import Note, User
from core.utils.security import verify_password
from core.utils.jwt import decode_token


class TestNotesAPI(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """Set up test database engine once for all tests"""
        cls.engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
    
    def setUp(self):
        """Create fresh database and session for each test"""
        SQLModel.metadata.create_all(type(self).engine)
        self.session = Session(type(self).engine)
        
        # Override the dependency
        def get_session_override():
            return self.session
        
        app.dependency_overrides[get_session] = get_session_override
        self.addCleanup(app.dependency_overrides.clear)
        
        # Sample note data
        self.sample_note = {
            "body": "This is a test note",
            "color_id": "blue",
            "color_header": "#0000FF",
            "color_body": "#E0E0FF",
            "color_text": "#000000",
            "pos_x": 100,
            "pos_y": 200
        }
    
    def tearDown(self):
        """Clean up after each test"""
        self.session.close()
        SQLModel.metadata.drop_all(self.engine)
        app.dependency_overrides.clear()
    
    def _create_note(self, note_data=None):
        """Helper method to create a note directly in database"""
        if note_data is None:
            note_data = self.sample_note
        note = Note(**note_data)
        self.session.add(note)
        self.session.commit()
        self.session.refresh(note)
        return note
    
    # Test Create Note
    def test_create_note_valid(self):
        """Test creating a note with valid data"""
        note = self._create_note()
        self.assertIsNotNone(note.id)
        self.assertEqual(note.body, self.sample_note["body"])
        self.assertEqual(note.color_id, self.sample_note["color_id"])
        self.assertEqual(note.pos_x, self.sample_note["pos_x"])
    
    def test_create_note_with_owner(self):
        """Test creating a note with an owner"""
        note_data = self.sample_note.copy()
        note_data["owner_id"] = 1
        note = Note(**note_data)
        self.session.add(note)
        self.session.commit()
        self.assertEqual(note.owner_id, 1)
    
    # Test Read Notes
    def test_get_all_notes_empty(self):
        """Test getting all notes when database is empty"""
        notes = self.session.exec(select(Note)).all()
        self.assertEqual(len(notes), 0)
    
    def test_get_all_notes_with_data(self):
        """Test getting all notes when data exists"""
        self._create_note()
        self._create_note({
            **self.sample_note,
            "body": "Second note",
            "pos_x": 300
        })
        
        notes = self.session.exec(select(Note)).all()
        self.assertEqual(len(notes), 2)
    
    def test_get_note_by_id(self):
        """Test getting a specific note by ID"""
        created_note = self._create_note()
        
        retrieved_note = self.session.get(Note, created_note.id)
        self.assertIsNotNone(retrieved_note, "Retrieved note should not be None")
        if retrieved_note:  # Only compare if note exists
            self.assertEqual(retrieved_note.id, created_note.id)
            self.assertEqual(retrieved_note.body, created_note.body)
    
    def test_get_note_by_id_not_found(self):
        """Test getting a note that doesn't exist"""
        note = self.session.get(Note, 999)
        self.assertIsNone(note)
    
    # Test Update Note
    def test_update_note_body(self):
        """Test updating a note's body"""
        note = self._create_note()
        original_color = note.color_id
        
        note.body = "Updated body"
        self.session.add(note)
        self.session.commit()
        self.session.refresh(note)
        
        self.assertEqual(note.body, "Updated body")
        self.assertEqual(note.color_id, original_color)
    
    def test_update_note_position(self):
        """Test updating a note's position"""
        note = self._create_note()
        
        note.pos_x = 500
        note.pos_y = 600
        self.session.add(note)
        self.session.commit()
        self.session.refresh(note)
        
        self.assertEqual(note.pos_x, 500)
        self.assertEqual(note.pos_y, 600)
    
    def test_update_note_colors(self):
        """Test updating a note's colors"""
        note = self._create_note()
        
        note.color_header = "#FF0000"
        note.color_body = "#FFE0E0"
        note.color_text = "#FFFFFF"
        self.session.add(note)
        self.session.commit()
        self.session.refresh(note)
        
        self.assertEqual(note.color_header, "#FF0000")
        self.assertEqual(note.color_body, "#FFE0E0")
        self.assertEqual(note.color_text, "#FFFFFF")
    
    def test_update_nonexistent_note(self):
        """Test updating a note that doesn't exist"""
        note = self.session.get(Note, 999)
        self.assertIsNone(note)
    
    # Test Delete Note
    def test_delete_note(self):
        """Test deleting a note"""
        note = self._create_note()
        note_id = note.id
        
        self.session.delete(note)
        self.session.commit()
        
        deleted_note = self.session.get(Note, note_id)
        self.assertIsNone(deleted_note)
    
    def test_delete_nonexistent_note(self):
        """Test deleting a note that doesn't exist"""
        note = self.session.get(Note, 999)
        self.assertIsNone(note)
    
    # Test Model Validations
    def test_note_with_minimum_body_length(self):
        """Test note with minimum body length (1 character)"""
        note_data = self.sample_note.copy()
        note_data["body"] = "A"
        note = self._create_note(note_data)
        self.assertEqual(len(note.body), 1)
    
    def test_note_with_maximum_body_length(self):
        """Test note with maximum body length (500 characters)"""
        note_data = self.sample_note.copy()
        note_data["body"] = "A" * 500
        note = self._create_note(note_data)
        self.assertEqual(len(note.body), 500)
    
    def test_note_position_boundaries(self):
        """Test note position at boundaries"""
        note_data = self.sample_note.copy()
        
        # Test minimum positions
        note_data["pos_x"] = 0
        note_data["pos_y"] = 0
        note_min = self._create_note(note_data)
        self.assertEqual(note_min.pos_x, 0)
        self.assertEqual(note_min.pos_y, 0)
        
        # Test maximum positions
        note_data["pos_x"] = 5000
        note_data["pos_y"] = 5000
        note_data["body"] = "Max position note"
        note_max = self._create_note(note_data)
        self.assertEqual(note_max.pos_x, 5000)
        self.assertEqual(note_max.pos_y, 5000)
    
    def test_full_crud_cycle(self):
        """Test complete CRUD operations"""
        # Create
        note = self._create_note()
        note_id = note.id
        self.assertIsNotNone(note_id)
        
        # Read
        retrieved = self.session.get(Note, note_id)
        self.assertIsNotNone(retrieved, "Retrieved note should not be None")
        if retrieved:  # Only proceed if note exists
            self.assertEqual(retrieved.body, self.sample_note["body"])
            
            # Update
            retrieved.body = "Updated in cycle"
            self.session.add(retrieved)
            self.session.commit()
            self.session.refresh(retrieved)
            self.assertEqual(retrieved.body, "Updated in cycle")
        
        # Delete
        self.session.delete(retrieved)
        self.session.commit()
        
        # Verify deletion
        deleted = self.session.get(Note, note_id)
        self.assertIsNone(deleted)
    
    def test_multiple_notes_independence(self):
        """Test that multiple notes can coexist independently"""
        note1 = self._create_note()
        note2 = self._create_note({
            **self.sample_note,
            "body": "Second note",
            "pos_x": 300
        })
        
        # Update one note
        note1.body = "Modified first note"
        self.session.add(note1)
        self.session.commit()
        self.session.refresh(note2)
        
        # Second note should be unchanged
        self.assertEqual(note2.body, "Second note")
        self.assertEqual(note1.body, "Modified first note")


class TestAuthAPI(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        """Set up test database engine and client once for all tests"""
        cls.engine = create_engine(
            "sqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        cls.client = TestClient(app)
    
    def setUp(self):
        """Create fresh database and session for each test"""
        SQLModel.metadata.create_all(type(self).engine)
        self.session = Session(type(self).engine)
        
        # Override the dependency
        def get_session_override():
            try:
                yield self.session
            finally:
                pass
        
        app.dependency_overrides[get_session] = get_session_override
        self.addCleanup(app.dependency_overrides.clear)
        
        # Sample user data
        self.sample_user = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123"
        }
    
    def tearDown(self):
        """Clean up after each test"""
        self.session.close()
        SQLModel.metadata.drop_all(self.engine)
        app.dependency_overrides.clear()
    
    def _register_user(self, user_data=None):
        """Helper method to register a user via API"""
        if user_data is None:
            user_data = self.sample_user
        response = type(self).client.post("/register", json=user_data)
        return response
    
    # Test Registration
    def test_register_valid_user(self):
        """Test registering a user with valid credentials"""
        response = self._register_user()
        self.assertEqual(response.status_code, 200)
        self.assertIn("Message", response.json())
        
        # Verify user was created in database
        user = self.session.exec(
            select(User).where(User.username == self.sample_user["username"])
        ).first()
        self.assertIsNotNone(user, "User should be created in database")
        
        if user:
            self.assertEqual(user.username, self.sample_user["username"])
            self.assertEqual(user.email, self.sample_user["email"])
            self.assertNotEqual(user.password_hash, self.sample_user["password"])
    
    def test_register_duplicate_username(self):
        """Test registering with an already existing username"""
        self._register_user()
        
        # Try to register with same username but different email
        duplicate_user = self.sample_user.copy()
        duplicate_user["email"] = "different@example.com"
        response = self._register_user(duplicate_user)
        
        self.assertEqual(response.status_code, 400)
        self.assertIn("Username already registered", response.json()["detail"])
    
    def test_register_duplicate_email(self):
        """Test registering with an already existing email"""
        self._register_user()
        
        # Try to register with same email but different username
        duplicate_user = self.sample_user.copy()
        duplicate_user["username"] = "differentuser"
        response = self._register_user(duplicate_user)
        
        self.assertEqual(response.status_code, 400)
        self.assertIn("Email already registered", response.json()["detail"])
    
    def test_register_invalid_username_too_short(self):
        """Test registering with username that's too short"""
        invalid_user = self.sample_user.copy()
        invalid_user["username"] = "ab"  # Less than 3 characters
        response = self._register_user(invalid_user)
        
        self.assertEqual(response.status_code, 422)
    
    def test_register_invalid_username_too_long(self):
        """Test registering with username that's too long"""
        invalid_user = self.sample_user.copy()
        invalid_user["username"] = "a" * 31  # More than 30 characters
        response = self._register_user(invalid_user)
        
        self.assertEqual(response.status_code, 422)
    
    def test_register_invalid_password_too_short(self):
        """Test registering with password that's too short"""
        invalid_user = self.sample_user.copy()
        invalid_user["password"] = "12345"  # Less than 6 characters
        response = self._register_user(invalid_user)
        
        self.assertEqual(response.status_code, 422)
    
    def test_register_missing_fields(self):
        """Test registering with missing required fields"""
        incomplete_user = {"username": "testuser"}
        response = type(self).client.post("/register", json=incomplete_user)
        
        self.assertEqual(response.status_code, 422)
    
    def test_register_password_is_hashed(self):
        """Test that password is properly hashed in database"""
        self._register_user()
        
        user = self.session.exec(
            select(User).where(User.username == self.sample_user["username"])
        ).first()
        
        self.assertIsNotNone(user, "User should exist in database")
        
        if user:
            self.assertNotEqual(user.password_hash, self.sample_user["password"])
            self.assertTrue(verify_password(self.sample_user["password"], user.password_hash))
    
    # Test Login
    def test_login_valid_credentials(self):
        """Test login with valid credentials"""
        self._register_user()
        
        login_data = {
            "username": self.sample_user["username"],
            "password": self.sample_user["password"]
        }
        response = type(self).client.post("/login", json=login_data)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("access_token", data)
        self.assertIn("refresh_token", data)
        self.assertEqual(data["token_type"], "bearer")
    
    def test_login_invalid_username(self):
        """Test login with non-existent username"""
        login_data = {
            "username": "nonexistentuser",
            "password": "password123"
        }
        response = type(self).client.post("/login", json=login_data)
        
        self.assertEqual(response.status_code, 401)
        self.assertIn("Invalid username or password", response.json()["detail"])
    
    def test_login_invalid_password(self):
        """Test login with incorrect password"""
        self._register_user()
        
        login_data = {
            "username": self.sample_user["username"],
            "password": "wrongpassword"
        }
        response = type(self).client.post("/login", json=login_data)
        
        self.assertEqual(response.status_code, 401)
        self.assertIn("Invalid username or password", response.json()["detail"])
    
    def test_login_missing_username(self):
        """Test login with missing username"""
        login_data = {"password": "password123"}
        response = type(self).client.post("/login", json=login_data)
        
        self.assertEqual(response.status_code, 422)
    
    def test_login_missing_password(self):
        """Test login with missing password"""
        login_data = {"username": "testuser"}
        response = type(self).client.post("/login", json=login_data)
        
        self.assertEqual(response.status_code, 422)
    
    def test_login_returns_valid_tokens(self):
        """Test that login returns valid JWT tokens"""
        self._register_user()
        
        login_data = {
            "username": self.sample_user["username"],
            "password": self.sample_user["password"]
        }
        response = type(self).client.post("/login", json=login_data)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Verify tokens can be decoded
        access_payload = decode_token(data["access_token"])
        refresh_payload = decode_token(data["refresh_token"])
        
        self.assertIsNotNone(access_payload, "Access token should decode successfully")
        self.assertIsNotNone(refresh_payload, "Refresh token should decode successfully")
        
        if access_payload:
            self.assertEqual(access_payload["sub"], self.sample_user["username"])
        if refresh_payload:
            self.assertEqual(refresh_payload["sub"], self.sample_user["username"])
    
    def test_login_case_sensitive_username(self):
        """Test that usernames are case-sensitive"""
        self._register_user()
        
        login_data = {
            "username": self.sample_user["username"].upper(),
            "password": self.sample_user["password"]
        }
        response = type(self).client.post("/login", json=login_data)
        
        self.assertEqual(response.status_code, 401)
    
    # Test Integration Scenarios
    def test_multiple_users_registration(self):
        """Test registering multiple users"""
        user1 = self.sample_user.copy()
        user2 = {
            "username": "seconduser",
            "email": "second@example.com",
            "password": "password456"
        }
        
        response1 = self._register_user(user1)
        response2 = self._register_user(user2)
        
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response2.status_code, 200)
        
        # Verify both users exist
        users = self.session.exec(select(User)).all()
        self.assertEqual(len(users), 2)
    
    def test_register_login_flow(self):
        """Test complete register and login flow"""
        # Register
        register_response = self._register_user()
        self.assertEqual(register_response.status_code, 200)
        
        # Login
        login_data = {
            "username": self.sample_user["username"],
            "password": self.sample_user["password"]
        }
        login_response = type(self).client.post("/login", json=login_data)
        self.assertEqual(login_response.status_code, 200)
        
        # Verify tokens
        data = login_response.json()
        self.assertIsNotNone(data["access_token"])
        self.assertIsNotNone(data["refresh_token"])
    
    def test_multiple_logins_same_user(self):
        """Test that same user can login multiple times"""
        self._register_user()
        
        login_data = {
            "username": self.sample_user["username"],
            "password": self.sample_user["password"]
        }
        
        response1 = type(self).client.post("/login", json=login_data)
        response2 = type(self).client.post("/login", json=login_data)
        
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response2.status_code, 200)
        
        # Tokens should be different (new tokens each time)
        token1 = response1.json()["access_token"]
        token2 = response2.json()["access_token"]
        self.assertNotEqual(token1, token2)


if __name__ == '__main__':
    unittest.main()