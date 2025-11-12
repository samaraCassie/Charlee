# Authentication System Migration Guide

## ✅ Completed Backend Changes

### 1. Authentication Core
- ✅ JWT utilities with access + refresh tokens (`backend/api/auth/jwt.py`)
- ✅ Password hashing with bcrypt (`backend/api/auth/password.py`)
- ✅ Authentication dependencies/middleware (`backend/api/auth/dependencies.py`)
- ✅ Pydantic schemas for auth requests/responses (`backend/api/auth/schemas.py`)

### 2. Authentication Routes
- ✅ POST `/api/v1/auth/register` - User registration
- ✅ POST `/api/v1/auth/login` - User login (returns JWT tokens)
- ✅ POST `/api/v1/auth/refresh` - Refresh access token
- ✅ POST `/api/v1/auth/logout` - Logout (revoke refresh token)
- ✅ POST `/api/v1/auth/logout-all` - Logout from all devices
- ✅ GET `/api/v1/auth/me` - Get current user info
- ✅ POST `/api/v1/auth/change-password` - Change password

### 3. Database Models
- ✅ `User` model with authentication fields
- ✅ `RefreshToken` model for token management
- ✅ Updated `BigRock`, `Task`, `MenstrualCycle`, `DailyLog` with `user_id` foreign keys
- ✅ Database migration created (`002_add_authentication.py`)

### 4. Configuration
- ✅ JWT settings in `.env.example`
- ✅ Settings class updated with JWT configuration
- ✅ Updated `requirements.txt` with auth dependencies

### 5. CRUD Operations
- ✅ Updated `crud.py` to filter by `user_id`
- ✅ All BigRock CRUD operations now require `user_id`
- ✅ All Task CRUD operations now require `user_id`

## 🔧 Required Route Updates

All routes need to be updated to:
1. Import the authentication dependency
2. Add `current_user: User = Depends(get_current_user)` parameter
3. Pass `user_id=current_user.id` to CRUD operations

### Example Pattern:

**Before:**
```python
@router.get("/")
def get_items(db: Session = Depends(get_db)):
    items = crud.get_items(db)
    return items
```

**After:**
```python
from api.auth.dependencies import get_current_user
from database.models import User

@router.get("/")
def get_items(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    items = crud.get_items(db, user_id=current_user.id)
    return items
```

### Routes That Need Updates:

#### ✅ Updated:
- `backend/api/routes/big_rocks.py` - Ready for auth (CRUD updated)
- `backend/api/routes/tasks.py` - Ready for auth (CRUD updated)

#### 🔧 Needs Update:
- `backend/api/routes/agent.py` - Currently uses hardcoded `user_id="samara"`
- `backend/api/routes/wellness.py` - Add user_id filtering
- `backend/api/routes/capacity.py` - Add user_id filtering
- `backend/api/routes/priorizacao.py` - Add user_id filtering
- `backend/api/routes/inbox.py` - Add user_id filtering
- `backend/api/routes/analytics.py` - Add user_id filtering
- `backend/api/routes/settings.py` - Add user_id filtering

## 📝 Frontend Changes Needed

### 1. Authentication Store (Zustand)
Create `interfaces/web/src/stores/authStore.ts`:
```typescript
interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  register: (data: RegisterData) => Promise<void>;
}
```

### 2. API Client Updates
Update `interfaces/web/src/services/api.ts`:
- Uncomment auth token interceptors (lines 15-19)
- Add Authorization header with Bearer token
- Handle 401 responses with token refresh logic

### 3. Auth Pages
Create:
- `interfaces/web/src/pages/Login.tsx`
- `interfaces/web/src/pages/Register.tsx`

### 4. Protected Routes
Create `interfaces/web/src/components/ProtectedRoute.tsx`:
```typescript
const ProtectedRoute = ({ children }) => {
  const { user } = useAuthStore();
  if (!user) return <Navigate to="/login" />;
  return children;
};
```

### 5. Update Router
Wrap protected routes with `<ProtectedRoute>`:
```typescript
<Route path="/dashboard" element={
  <ProtectedRoute>
    <Dashboard />
  </ProtectedRoute>
} />
```

## 🔄 Migration Steps

### Step 1: Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### Step 2: Update Environment Variables
Copy `.env.example` to `.env` and generate secure JWT keys:
```bash
# Generate JWT secret keys
openssl rand -hex 32
```

### Step 3: Run Database Migration
```bash
cd backend
alembic upgrade head
```

This will create:
- `users` table
- `refresh_tokens` table
- Add `user_id` columns to existing tables

### Step 4: Create First User
Use the `/api/v1/auth/register` endpoint:
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "email": "admin@charlee.com",
    "password": "SecureP@ss123",
    "full_name": "Admin User"
  }'
```

### Step 5: Test Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "SecureP@ss123"
  }'
```

Response will include `access_token` and `refresh_token`.

### Step 6: Test Authenticated Request
```bash
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 🔒 Security Notes

### Password Requirements:
- Minimum 8 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one digit

### Token Expiration:
- Access tokens: 30 minutes (configurable)
- Refresh tokens: 7 days (configurable)

### Best Practices:
1. **Never** commit JWT secret keys to version control
2. Use strong, random keys in production (32+ characters)
3. Enable HTTPS in production
4. Implement rate limiting on auth endpoints (already configured)
5. Log authentication attempts for security monitoring
6. Consider implementing 2FA for sensitive accounts

## 🧪 Testing Checklist

- [ ] Register new user
- [ ] Login with valid credentials
- [ ] Login with invalid credentials (should fail)
- [ ] Access protected endpoint with valid token
- [ ] Access protected endpoint without token (should return 401)
- [ ] Refresh access token using refresh token
- [ ] Logout (single device)
- [ ] Logout from all devices
- [ ] Change password
- [ ] User data isolation (users can only see their own data)

## 📚 API Documentation

After starting the server, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

All authentication endpoints are documented under the "Authentication" tag.

## 🐛 Troubleshooting

### Issue: "Could not validate credentials"
- Check if token is expired
- Verify Authorization header format: `Bearer <token>`
- Ensure JWT_SECRET_KEY in .env matches the one used to generate the token

### Issue: "User not found or inactive"
- Check if user exists in database
- Verify user.is_active = true
- Ensure user_id in token matches database

### Issue: Database migration fails
- Backup database first
- Check if tables already exist
- Review Alembic revision history: `alembic current`
- Try: `alembic downgrade -1` then `alembic upgrade head`

## 📞 Next Steps

1. Update remaining routes to require authentication
2. Implement frontend authentication flow
3. Add comprehensive tests for auth endpoints
4. Set up proper error handling and logging
5. Consider adding email verification
6. Implement password reset functionality
7. Add rate limiting specifically for auth endpoints
8. Set up monitoring for failed login attempts
