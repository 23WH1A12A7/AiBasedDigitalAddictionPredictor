# Quick Start Guide - Digital Wellness Predictor

## Setup & Installation

### 1. Install Requirements
```bash
cd /path/to/Phone-Addiction-Prediction
pip install -r requirements.txt
```

### 2. Initialize Database (First Time Only)
```bash
python -c "from database import db; print('Database initialized')"
```

### 3. Run Flask Application
```bash
# Development mode
python app.py

# Or with Gunicorn (Production)
gunicorn -w 4 -b 127.0.0.1:5000 app:app
```

Application will be available at: **http://localhost:5000**

---

## Testing Quick Links

### Create New Account
1. Go to: http://localhost:5000/signup
2. Fill in: Name, Email, Password
3. Click "Create Account"
4. Redirects to dashboard

### Login to Existing Account
1. Go to: http://localhost:5000/login
2. Enter email and password
3. Click "Sign In"
4. Access dashboard with charts

### Direct Dashboard Access (Authenticated)
- http://localhost:5000/dashboard

---

## API Endpoints Reference

### Authentication
```
POST   /api/auth/register     → Create new user
POST   /api/auth/login        → Authenticate user & get token
POST   /api/auth/logout       → Clear authentication
GET    /api/auth/me           → Get current user info [TOKEN REQUIRED]
```

### Dashboard Data
```
GET    /api/dashboard-data    → Get dashboard metrics [TOKEN REQUIRED]
GET    /api/quick-stats       → Get quick stats [TOKEN REQUIRED]
GET    /api/achievements      → Get achievements [TOKEN REQUIRED]
GET    /api/goals             → Get goals [TOKEN REQUIRED]
GET    /api/insights          → Get AI insights [TOKEN REQUIRED]
```

### Request Headers Format
```
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json
```

---

## Browser DevTools Debugging

### Check Authentication Token
```javascript
// In Browser Console:
localStorage.getItem('authToken')  // Returns JWT token
localStorage.removeItem('authToken')  // Clear token (will redirect to login)
```

### Monitor Network Requests
1. Open DevTools (F12)
2. Go to Network tab
3. Try login/signup or interact with dashboard
4. Look for:
   - `/api/auth/login` - POST with credentials
   - `/api/dashboard-data` - GET with token
   - Check response status (should be 2xx for success, 4xx for errors)

### Check Console for Errors
1. Open DevTools (F12)
2. Go to Console tab
3. Should see dashboard.js logs like:
   ```
   Dashboard loaded successfully
   Updated to show Last 30 days
   ```
4. No red errors should appear

---

## Test Scenarios

### Scenario 1: Complete User Journey
```
1. Start → http://localhost:5000
2. Click "Sign up" 
3. Create account: test@example.com / password123
4. Dashboard loads automatically
5. View charts and data
6. Change chart period (7 days / 30 days)
7. Check achievements and goals
```

### Scenario 2: Returning User
```
1. Clear browser cache (or different browser)
2. Go to http://localhost:5000/login
3. Login with test@example.com / password123
4. Dashboard shows same data (persistent user data)
5. Check localStorage for token
```

### Scenario 3: Error Handling
```
1. Signup page → mismatched passwords → Error shown
2. Login page → wrong password → Error shown
3. Remove token from localStorage → Dashboard redirects to login
4. Try /api/dashboard-data without token → 401 error (check Network tab)
```

---

## File Structure Overview

```
Phone-Addiction-Prediction/
│
├── app.py                    # Flask backend with API endpoints ⭐
├── database.py              # Database manager
├── requirements.txt         # Dependencies ⭐
│
├── templates/
│   ├── login.html          # Login page ⭐ (Updated with AJAX)
│   ├── signup.html         # Signup page ⭐ (Updated with AJAX)
│   ├── dashboard_new.html  # Dashboard ⭐ (Uses dashboard.js)
│   ├── base.html           # Base template
│   └── ...
│
└── static/
    ├── dashboard.js        # Dashboard logic ⭐ (NEW FILE)
    ├── script.js           # Other scripts
    ├── style.css           # Styling
    └── ...

⭐ = Recently updated/new files
```

---

## Key Features Implemented

✅ **JWT Token-Based Authentication**
- Secure token generation
- 7-day expiration
- HTTP-only secure cookies

✅ **API Endpoints with Authentication**
- Registration with validation
- Login with credentials
- Protected dashboard endpoints

✅ **Interactive Dashboard**
- Real-time chart updates
- Period selection (7/30/90 days)
- Dynamic data loading

✅ **Enhanced Error Handling**
- Inline error messages
- Loading states
- Network error recovery

✅ **Client-Side Validation**
- Email validation
- Password strength check
- Password matching

---

## Environment Variables (Optional)

```bash
export SECRET_KEY="your-secret-key-here"        # For production
export FLASK_ENV="production"                   # Set to production
export DATABASE_PATH="/path/to/wellness_data.db"  # Custom DB path
```

---

## Troubleshooting

### Charts Not Showing
```javascript
// Check dashboard.js is loaded:
typeof charts === 'object'  // Should return true

// Check historical data:
// Look in Network tab for /api/dashboard-data response
```

### Token Issues
```javascript
// Force logout:
localStorage.clear()
// Then refresh page - should redirect to login
```

### Database Issues
```bash
# Reset database (WARNING: Deletes all data)
rm wellness_data.db
python app.py  # Recreates empty database
```

---

## Performance Tips

1. **Clear Browser Cache** for updates
   - DevTools → Application → Clear site data

2. **Monitor Network** for slow requests
   - DevTools → Network → Check response times

3. **Check Database Size**
   - ```bash
     ls -lh wellness_data.db
     ```

4. **Enable Compression**
   - Flask gzip or nginx compression in production

---

## Security Checklist

- [x] Passwords hashed with bcrypt
- [x] JWT tokens with expiration
- [x] CORS enabled appropriately
- [x] HTTP-only secure cookies
- [x] Input validation on both client & server
- [x] SQL injection protection (using parameterized queries)
- [ ] HTTPS enabled (for production)
- [ ] Rate limiting (recommended for production)
- [ ] CSRF protection (can be added if needed)

---

## Next Steps

1. **Test the application** following test scenarios
2. **Monitor logs** in terminal for errors
3. **Check browser console** for JavaScript issues
4. **Verify API responses** in Network tab
5. **Deploy to production** when all tests pass

---

## Support Commands

```bash
# Check if Flask is running
curl http://localhost:5000/

# Test login endpoint
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# View Flask logs
# Watch terminal output where Flask is running

# Check installed packages
pip list | grep -E "Flask|PyJWT|cors"

# Kill Flask if stuck
pkill -f "python app.py"
```

---

**Happy Testing!** 🚀

For detailed changes, see: **CHANGES_SUMMARY.md**
