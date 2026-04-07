# Digital Wellness Predictor - System Updates & Fixes

## Overview of Changes

This document outlines all the improvements made to fix signup/login functionalities, backend-frontend communication, and graph visualization.

---

## 1. **Backend API Endpoints (Flask)**

### Files Modified: `app.py`

#### New JWT Authentication Endpoints:

1. **POST `/api/auth/register`**
   - Accepts JSON: `{ name, email, password }`
   - Returns: JWT token + user data
   - Validates email uniqueness, password strength (6+ chars), name length

2. **POST `/api/auth/login`**
   - Accepts JSON: `{ email, password }`
   - Returns: JWT token + user data
   - Updates last_active timestamp

3. **POST `/api/auth/logout`**
   - Clears authentication
   - Returns: `{ success: true }`

4. **GET `/api/auth/me`** (requires token)
   - Returns current authenticated user info
   - Authorization: Bearer token in header

5. **GET `/api/dashboard-data`** (requires token)
   - Optional query param: `?period=7days|30days|90days`
   - Returns dashboard metrics and historical data

6. **GET `/api/quick-stats`** (requires token)
   - Returns wellbeing score, streak, completion rate, screen time

7. **GET `/api/achievements`** (requires token)
   - Returns user achievements list

8. **GET `/api/goals`** (requires token)
   - Returns user goals with progress

9. **GET `/api/insights`** (requires token)
   - Returns AI-generated insights about user patterns

#### Features:
- JWT token-based authentication
- Token expiration (7 days)
- Secure HTTP-only cookies as fallback
- CORS enabled for frontend communication
- Proper error handling with descriptive messages

---

## 2. **Frontend Authentication (Updated Templates)**

### Files Modified:
- `templates/login.html`
- `templates/signup.html`

#### Changes:
- **Form Submission Method**: Changed from traditional form POST to AJAX/fetch API
- **Error Handling**: Dynamic error messages displayed inline
- **Token Storage**: JWT tokens saved to localStorage
- **Validation**: Client-side validation before API call
- **User Feedback**: Loading states during authentication

#### Login Flow:
```
User fills email/password → Client validates → POST to /api/auth/login 
→ Backend authenticates → Returns JWT token → Store in localStorage 
→ Redirect to /dashboard
```

#### Signup Flow:
```
User fills name/email/password → Client validates password match 
→ POST to /api/auth/register → Backend creates user
→ Returns JWT token → Store in localStorage → Redirect to /dashboard
```

---

## 3. **Dashboard Charts & Data** (Updated Templates)

### Files Modified:
- `templates/dashboard_new.html`
- `static/dashboard.js` (new file)

#### Dashboard JavaScript (`dashboard.js`):

**Features:**
1. **Automatic Token Validation**
   - Checks localStorage for auth token
   - Redirects to login if not authenticated
   - Handles token expiration gracefully

2. **API Data Fetching**
   - Parallel loading of dashboard, stats, achievements, goals, insights
   - Proper error handling for each endpoint
   - Authorization header included in all requests

3. **Chart Initialization**
   - Screen Time Trends (Line chart)
   - Mood Patterns (Bar chart)
   - Sleep Quality (Line chart)
   - Focus & Productivity (Doughnut chart)

4. **Dynamic Chart Updates**
   - Period selector triggers data refresh
   - Charts update without page reload
   - Support for 7-day, 30-day, 90-day views

5. **Dynamic Content Rendering**
   - Achievements list
   - Goals with progress bars
   - AI insights with status indicators
   - Quick stats updates

6. **User Notifications**
   - Success/error/info notifications
   - Auto-dismiss after 3 seconds
   - Slide-in animation

---

## 4. **Dependencies Updated**

### Files Modified: `requirements.txt`

#### New Dependencies:
```
flask-cors==4.0.0      # Enable CORS for frontend
PyJWT==2.8.1           # JWT token creation/validation
```

---

## 5. **Complete Data Flow Diagram**

```
┌─────────────────────────────────────────────────────────────┐
│                     USER INTERACTION                         │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Browser Login/Signup → Fetch API (JSON) → Flask Backend    │
│       ↓                                            ↓          │
│  Store Token in           Database Auth        Create/Verify │
│  localStorage              (Bcrypt Hash)        User & Token  │
│       ↓                                            ↓          │
│  /dashboard.js            ← Return JWT + ← Dashboard Data   │
│  (Load with token)        User Info      API Endpoints      │
│       ↓                                            ↓          │
│  Fetch API with Bearer    Fetch API         Return JSON:    │
│  Authorization header      (with token)     - Metrics       │
│       ↓                                    - Historical Data │
│  Render Charts                            - Goals/Insights  │
│  & Insights               Database Queries ← User Data      │
│  in Real-time                                               │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 6. **Testing Instructions**

### Prerequisites:
```bash
# Install new dependencies
pip install flask-cors PyJWT -r requirements.txt

# Ensure database exists
python database.py  # Initializes database if needed
```

### Test Case 1: User Signup
```
1. Navigate to http://localhost:5000/signup
2. Fill in:
   - Name: "John Doe"
   - Email: "john@example.com"
   - Password: "password123"
   - Confirm Password: "password123"
3. Click "Create Account"
4. Expected: Redirects to /dashboard with chart data
5. Check browser console: Should see dashboard.js console logs
```

### Test Case 2: User Login
```
1. Navigate to http://localhost:5000/login
2. Fill in:
   - Email: "john@example.com"
   - Password: "password123"
3. Click "Sign In"
4. Expected: Redirects to /dashboard with authenticated data
5. Verify token in localStorage: `localStorage.getItem('authToken')`
```

### Test Case 3: Dashboard Charts
```
1. After login, verify charts are rendered
2. Try changing period dropdown (7 days, 30 days, 3 months)
3. Expected: Charts update with new data
4. Check browser Network tab: Should see /api/dashboard-data requests
5. Verify response contains historical_data object
```

### Test Case 4: Token Expiration
```
1. Login and note the token in localStorage
2. Wait for token to expire (7 days) OR manually delete:
   localStorage.removeItem('authToken')
3. Refresh dashboard page
4. Expected: Should redirect to /login with error message
```

### Test Case 5: Invalid Credentials
```
1. Navigate to login
2. Try with wrong email/password
3. Expected: Error message appears inline
4. Message should be: "Invalid email or password"
5. Form should remain for retry
```

### Test Case 6: Password Mismatch (Signup)
```
1. Navigate to signup
2. Enter password "password123"
3. Confirm password "password124"
4. Click "Create Account"
5. Expected: Error "Passwords do not match" appears
```

---

## 7. **Security Enhancements**

1. **JWT Tokens**
   - 7-day expiration
   - HS256 algorithm
   - Secure token validation on every API call

2. **Password Security**
   - Bcrypt hashing in database
   - Minimum 6 characters enforced
   - Salt generation per user

3. **CORS Configuration**
   - Credentials allowed
   - Specific origin restrictions (can be configured)

4. **API Authentication**
   - Token required for all data endpoints
   - Bearer token in Authorization header
   - Graceful 401 handling

---

## 8. **File Structure**

```
Phone-Addiction-Prediction/
├── app.py                          # Flask app (UPDATED - new API endpoints)
├── database.py                     # Database manager (unchanged)
├── requirements.txt                # Dependencies (UPDATED - added JWT, CORS)
├── templates/
│   ├── login.html                 # Login page (UPDATED - AJAX form)
│   ├── signup.html                # Signup page (UPDATED - AJAX form)
│   ├── dashboard_new.html         # Dashboard (UPDATED - uses dashboard.js)
│   └── ... (other templates)
├── static/
│   ├── dashboard.js               # Dashboard functionality (NEW FILE)
│   ├── script.js                  # Existing minimal script
│   ├── style.css                  # Styling
│   └── ... (other static files)
└── ... (other files)
```

---

## 9. **Common Issues & Troubleshooting**

### Issue: "Token is missing" error
**Solution**: Check if token is properly stored in localStorage
```javascript
// Check in browser console:
localStorage.getItem('authToken')  // Should return a JWT string
```

### Issue: CORS errors
**Solution**: Ensure flask-cors is installed and imported
```python
# In app.py, verify:
from flask_cors import CORS
CORS(app, supports_credentials=True)
```

### Issue: Charts not rendering
**Solution**: 
1. Verify /api/dashboard-data endpoint returns correct structure
2. Check browser console for JavaScript errors
3. Ensure Chart.js CDN is loading (check Network tab)
4. Verify historical_data object has correct keys

### Issue: Login endless loop
**Solution**: 
1. Clear localStorage: `localStorage.clear()`
2. Delete authToken cookie from browser DevTools
3. Clear browser cache
4. Restart Flask server

---

## 10. **Future Improvements**

1. **Email Verification**
   - Send confirmation email on signup
   - Activate account link

2. **Password Reset**
   - Forgot password endpoint
   - Reset token sent via email

3. **Two-Factor Authentication**
   - SMS/Email OTP verification
   - TOTP support

4. **Refresh Token Implementation**
   - Access tokens (shorter expiration)
   - Refresh tokens (7 days)

5. **Rate Limiting**
   - Prevent brute force attacks
   - API endpoint throttling

6. **User Profiles**
   - Avatar upload
   - Bio/settings
   - Privacy controls

7. **Data Export**
   - CSV export functionality
   - PDF reports
   - Data archiving

---

## 11. **Summary of Key Changes**

| Component | Before | After |
|-----------|--------|-------|
| Auth Method | Form POST | AJAX + JWT |
| Login Endpoint | `/login` (HTML) | `/api/auth/login` (JSON) |
| Data Flow | Session-based | Token-based |
| Charts | Static HTML | Dynamic JS with API |
| Error Handling | Flash messages | Inline error display |
| Dashboard Reset | Page reload | API call |
| Frontend Framework | None | Fetch API with vanilla JS |
| CORS | Not enabled | Enabled |
| Token Storage | Session only | localStorage + cookies |

---

## 12. **Testing Checklist**

- [ ] Signup with valid credentials
- [ ] Signup with duplicate email (should fail)
- [ ] Signup with mismatched passwords (should fail)
- [ ] Login with correct credentials
- [ ] Login with wrong password (should fail)
- [ ] Logout redirects to login
- [ ] Dashboard loads with authenticated user
- [ ] Charts display data correctly
- [ ] Period dropdown updates charts
- [ ] Achievements render properly
- [ ] Goals show progress bars
- [ ] Insights display with status icons
- [ ] Token persists in localStorage
- [ ] Expired token redirects to login
- [ ] API returns 401 for missing token
- [ ] Error messages display correctly
- [ ] Loading states show during requests
- [ ] No console errors in browser
- [ ] Network tab shows correct API calls
- [ ] CORS headers present in responses

---

**Last Updated**: March 17, 2026
**Version**: 1.0
**Status**: Ready for testing
