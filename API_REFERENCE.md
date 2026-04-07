# API Reference - Updated Endpoints

## Base URL
```
http://127.0.0.1:5000
```

## Authentication
All endpoints marked with 🔒 require Bearer token in header:
```
Authorization: Bearer <JWT_TOKEN>
```

Get token from login:
```
POST /api/auth/login
Response: { "token": "jwt_token_here" }
```

---

## Authentication Endpoints

### Register User
```
POST /api/auth/register
Content-Type: application/json

{
  "name": "John Doe",
  "email": "user@example.com",
  "password": "securepassword"
}

Response (201):
{
  "user_id": "user_abc123",
  "email": "user@example.com",
  "token": "jwt_token"
}

Response (400):
{
  "error": "Email already exists"
}
```

### Login
```
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword"
}

Response (200):
{
  "user_id": "user_abc123",
  "email": "user@example.com",
  "username": "johndoe",
  "token": "jwt_token"
}

Response (401):
{
  "error": "Invalid email or password"
}
```

### Get Current User 🔒
```
GET /api/auth/me
Authorization: Bearer <token>

Response (200):
{
  "user_id": "user_abc123",
  "email": "user@example.com",
  "username": "johndoe",
  "created_at": "2024-03-17T10:30:00"
}
```

---

## Dashboard Endpoints

### Get Dashboard Data 🔒
```
GET /api/dashboard-data?period=7days
Authorization: Bearer <token>

Query Parameters:
- period: "7days" (default), "30days", "3months"

Response (200):
{
  "session_data": {
    "risk": "CRITICAL",
    "risk_score": 92,
    "confidence": 35,
    "risk_factors": [
      "High screen time (>8 hours/day)",
      "Insufficient sleep (<5 hours)",
      "Poor sleep quality",
      "Low mood/mental health concerns"
    ],
    "usage_data": {
      "daily_screen_time": 9.5,
      "night_usage": 2.85
    },
    "mood_analysis": {
      "avg_mood_score": 2.1,
      "stress_level": "High",
      "sleep_hours": 4.2,
      "sleep_quality": false
    }
  },
  "historical_data": {
    "mood_trend": [
      {"date": "Mon", "value": 2.1},
      {"date": "Tue", "value": 2.3},
      ...
    ],
    "stress_vs_screen_time": [
      {"date": "Mon", "value": 85},
      ...
    ],
    "sleep_vs_mental_fatigue": [
      {"date": "Mon", "value": 4.2},
      ...
    ],
    "usage_vs_concentration": [
      {"date": "Mon", "value": 3.5},
      ...
    ]
  },
  "period": "7 days",
  "user_id": "user_abc123"
}
```

### Get Quick Stats 🔒
```
GET /api/quick-stats
Authorization: Bearer <token>

Response (200):
{
  "wellbeing_score": 45,
  "current_streak": 3,
  "longest_streak": 7,
  "completion_rate": 72,
  "total_points": 150,
  "points_this_week": 85,
  "daily_screen_time": 8.3
}
```

---

## Goals Endpoints

### Get Goals 🔒
```
GET /api/goals
Authorization: Bearer <token>

Response (200):
[
  {
    "title": "Better Sleep",
    "current": 6.5,
    "target": 8,
    "unit": "hours",
    "progress": 81,
    "icon": "fa-moon"
  },
  {
    "title": "Reduce Screen Time",
    "current": 5.2,
    "target": 4,
    "unit": "hours",
    "progress": 35,
    "icon": "fa-mobile"
  },
  {
    "title": "Social Balance",
    "current": 2,
    "target": 3,
    "unit": "interactions",
    "progress": 67,
    "icon": "fa-users"
  }
]
```

**Progress Calculation:**
- Sleep Goal: `(current_hours / 8) * 100`
- Screen Time Goal: `100 - ((current_hours / 8) * 100)`
- Social Goal: `(completed_tasks / 3) * 100`

---

## Achievements Endpoints

### Get Achievements 🔒
```
GET /api/achievements
Authorization: Bearer <token>

Response (200):
[
  {
    "title": "Week Warrior",
    "description": "7-day streak completed",
    "icon": "fa-fire",
    "unlocked": true,
    "points": 50,
    "date": "2024-03-15T10:30:00"
  },
  {
    "title": "Sleep Champion",
    "description": "5 nights of quality sleep",
    "icon": "fa-moon",
    "unlocked": false,
    "points": 100,
    "date": null
  },
  ...
]

Available Achievements:
- Week Warrior (50 pts): 7-day streak
- Sleep Champion (100 pts): 5 quality nights
- Mindful Master (75 pts): 10 mood check-ins
- Balance Score (100 pts): 80+ wellbeing score
- Real Connections (80 pts): Social tasks
- Detox Hero (150 pts): 7-day phone-free
- Digital Balance (120 pts): 50% screen reduction
```

---

## Insights Endpoints

### Get Insights 🔒
```
GET /api/insights
Authorization: Bearer <token>

Response (200):
[
  {
    "title": "Digital Wellness Alert",
    "description": "Your phone usage is critical (9.5 hours/day). Consider setting daily limits...",
    "status": "Critical",
    "status_type": "danger",
    "metrics": [
      {"label": "Screen Time", "value": "9.5h/day"},
      {"label": "Risk Level", "value": "Critical"}
    ]
  },
  {
    "title": "Sleep Quality Concern",
    "description": "You're getting 4 hours of sleep. Try to aim for 7-9 hours...",
    "status": "Needs Improvement",
    "status_type": "warning",
    "metrics": [
      {"label": "Current Sleep", "value": "4h"},
      {"label": "Recommended", "value": "7-9h"}
    ]
  },
  {
    "title": "Mental Health Check-in",
    "description": "Your mood scores suggest you might be stressed. Consider mindfulness...",
    "status": "Support Needed",
    "status_type": "danger",
    "metrics": [
      {"label": "Mood Score", "value": "2.1/5"},
      {"label": "Recommendation", "value": "Self-care time"}
    ]
  }
]

Status Types:
- "danger": Critical issues needing immediate attention
- "warning": Issues needing attention
- "positive": Positive trends and achievements
```

---

## Tasks Endpoints

### Get Daily Tasks 🔒
```
GET /api/tasks
Authorization: Bearer <token>

Response (200):
{
  "tasks": [
    {
      "title": "No Phone Before Bed",
      "points": 10,
      "completed": false
    },
    {
      "title": "Real Connection",
      "points": 15,
      "completed": false
    },
    {
      "title": "Read Offline",
      "points": 20,
      "completed": false
    },
    {
      "title": "Stretch Break",
      "points": 25,
      "completed": false
    },
    {
      "title": "Notification Detox",
      "points": 30,
      "completed": false
    },
    {
      "title": "Nature Time",
      "points": 35,
      "completed": false
    }
  ],
  "total": 6
}
```

### Complete Task 🔒
```
POST /api/tasks
Authorization: Bearer <token>
Content-Type: application/json

{
  "task_name": "Real Connection",
  "points": 15
}

Response (200):
{
  "success": true,
  "points_earned": 15,
  "total_points": 150,
  "current_streak": 3,
  "unlocked_achievements": ["sleep_champion"],
  "wellbeing_score": 72
}

Response (400):
{
  "error": "task_name is required"
}
```

---

## Data Input Endpoints

### Record Screen Time 🔒
```
POST /api/data/screen-time
Authorization: Bearer <token>
Content-Type: application/json

{
  "hours": 8.5,
  "app_sessions": 42,
  "notifications": 128,
  "night_usage": 2.3
}

Response (200):
{
  "success": true,
  "message": "Screen time recorded"
}
```

### Record Sleep Data 🔒
```
POST /api/data/sleep
Authorization: Bearer <token>
Content-Type: application/json

{
  "hours_slept": 7.5,
  "quality_score": 8,
  "bedtime": "23:30",
  "wake_time": "07:00"
}

Response (200):
{
  "success": true,
  "message": "Sleep data recorded"
}
```

### Record Mood Data 🔒
```
POST /api/data/mood
Authorization: Bearer <token>
Content-Type: application/json

{
  "mood_score": 4.2,
  "note": "Feeling better today"
}

Response (200):
{
  "success": true,
  "message": "Mood data recorded"
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "error": "Missing required field: email"
}
```

### 401 Unauthorized
```json
{
  "error": "Missing or invalid token"
}
```

### 404 Not Found
```json
{
  "error": "User not found"
}
```

### 500 Server Error
```json
{
  "error": "An error occurred: [error message]"
}
```

---

## Usage Examples

### Complete Flow Example

**1. Register**
```bash
curl -X POST http://127.0.0.1:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "password": "secure123"
  }'

# Response: { "token": "eyJ0eXAi..." }
```

**2. Get Dashboard**
```bash
curl http://127.0.0.1:5000/api/dashboard-data \
  -H "Authorization: Bearer eyJ0eXAi..."

# Response: { "session_data": {...} }
```

**3. Record Data**
```bash
curl -X POST http://127.0.0.1:5000/api/data/screen-time \
  -H "Authorization: Bearer eyJ0eXAi..." \
  -H "Content-Type: application/json" \
  -d '{
    "hours": 9.5,
    "app_sessions": 50,
    "notifications": 200,
    "night_usage": 3.0
  }'

# Response: { "success": true }
```

**4. Complete Task**
```bash
curl -X POST http://127.0.0.1:5000/api/tasks \
  -H "Authorization: Bearer eyJ0eXAi..." \
  -H "Content-Type: application/json" \
  -d '{
    "task_name": "Real Connection",
    "points": 15
  }'

# Response: { "success": true, "points_earned": 15 }
```

**5. Check Achievements**
```bash
curl http://127.0.0.1:5000/api/achievements \
  -H "Authorization: Bearer eyJ0eXAi..."

# Response: [{ "title": "Week Warrior", "unlocked": true }]
```

---

## Data Types

### Risk Levels
- `"LOW"` - Score < 40
- `"MEDIUM"` - Score 40-59
- `"HIGH"` - Score 60-79
- `"CRITICAL"` - Score >= 80

### Status Types
- `"positive"` - Green/success indicator
- `"warning"` - Yellow/caution indicator
- `"danger"` - Red/critical indicator

### Units
- `"hours"` - Sleep/screen time
- `"interactions"` - Social activities
- `"points"` - Gamification points
- `"days"` - Streaks

---

## Response Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request (Missing/invalid fields) |
| 401 | Unauthorized (Missing/invalid token) |
| 404 | Not Found |
| 500 | Server Error |

---

## Rate Limiting

Currently no rate limiting is enforced. In production, consider:
- 100 requests/minute per user
- 1000 requests/hour per IP
- Burst limits for authentication

---

## Rate Calculation Details

### Risk Score Calculation
```
Total Score = Screen Risk + Sleep Hours Risk + Sleep Quality Risk + Mood Risk

Components:
- Screen Time Risk
  - If avg > 8h: +40
  - If 6-8h: +20
  - Otherwise: 0

- Sleep Hours Risk
  - If < 5h: +30
  - If 5-6h: +15
  - Otherwise: 0

- Sleep Quality Risk
  - If quality < 5: +15
  - Otherwise: 0

- Mood Risk
  - If < 2.5/5: +15
  - Otherwise: 0
```

### Wellbeing Score Calculation
```
Score = Mood Contribution + Streak Contribution + Screen Time Contribution

- Mood: (avg_mood / 5.0) * 40
- Streak: completion_rate * 0.4
- Screen: (1 - min(daily_screen_time / 8, 1)) * 20

Max: 95%, Min: 0%
```

---

## Notes for Frontend Integration

1. **Store Token:** Save JWT in localStorage after login
2. **Add Header:** Include token in all authenticated requests
3. **Refresh Data:** Call dashboard-data every 30 seconds
4. **Handle Errors:** Check for 401 and redirect to login
5. **Display Risk:** Show risk level prominently
6. **Update Charts:** Historical data changes with period selection

