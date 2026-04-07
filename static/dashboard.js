// ==================== Dashboard JavaScript ====================
// This file handles all dashboard functionality including:
// - Chart initialization and updates
// - API data fetching
// - User authentication checks
// - Real-time updates

const charts = {};
const chartPeriods = {
    moodTrend: '7days',
    screenTime: '7days',
    sleepQuality: '7days',
    completion: '7days',
    focus: '7days'
};

// ==================== Authentication Functions ====================

function getAuthToken() {
    // Check localStorage first
    const token = localStorage.getItem('authToken');
    if (token) return token;
    
    // Check cookies as fallback
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        const [name, value] = cookie.trim().split('=');
        if (name === 'auth_token') return decodeURIComponent(value);
    }
    
    return null;
}

function setAuthToken(token) {
    localStorage.setItem('authToken', token);
}

function clearAuthToken() {
    localStorage.removeItem('authToken');
}

// ==================== API Functions ====================

async function fetchAPI(endpoint, method = 'GET', body = null) {
    const token = getAuthToken();
    
    const options = {
        method,
        headers: {
            'Content-Type': 'application/json',
        }
    };
    
    if (token) {
        options.headers['Authorization'] = `Bearer ${token}`;
    }
    
    if (body) {
        options.body = JSON.stringify(body);
    }
    
    try {
        const response = await fetch(`${endpoint}`, options);
        
        if (response.status === 401) {
            // Unauthorized - token may be expired
            clearAuthToken();
            window.location.href = '/login';
            return null;
        }
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || `HTTP ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error(`API Error (${endpoint}):`, error);
        showNotification(error.message, 'error');
        return null;
    }
}

// ==================== Dashboard Initialization ====================

document.addEventListener('DOMContentLoaded', async function() {
    // Load dashboard data (works with both JWT and session-based auth)
    await loadDashboardData();
    
    // Add event listeners
    addPeriodSelectors();
});

// ==================== Dashboard Data Loading ====================

async function loadDashboardData() {
    try {
        const [dashboardData, achievements, goals, insights] = await Promise.all([
            fetchAPI('/api/dashboard-data'),
            fetchAPI('/api/achievements'),
            fetchAPI('/api/goals'),
            fetchAPI('/api/insights')
        ]);
        
        if (dashboardData) {
            const quickStats = {
                wellbeing_score: dashboardData.wellbeing_score || 50,
                current_streak: dashboardData.current_streak || 0,
                achievement_count: dashboardData.achievement_count || 0,
                total_points: dashboardData.total_points || 0,
                points_this_week: dashboardData.points_this_week || 0,
                completion_rate: dashboardData.completion_rate || 0
            };
            
            updateQuickStatsDisplay(quickStats);
            initializeCharts(dashboardData.historical_data || {});
        } else {
            initializeCharts({});
        }

        if (Array.isArray(achievements)) {
            updateAchievements(achievements);
        }

        if (Array.isArray(goals)) {
            updateGoals(goals);
        }

        if (Array.isArray(insights)) {
            updateAIInsights(insights);
        }
    } catch (error) {
        console.error('Error loading dashboard data:', error);
        showNotification('Failed to load dashboard data', 'error');
        initializeCharts({});
    }
}

function updateQuickStatsDisplay(stats) {
    // Update all stat cards with real data
    const statCards = document.querySelectorAll('.stat-card');
    
    // Card 0: Wellbeing Score
    if (statCards.length >= 1) {
        const scoreNumber = statCards[0].querySelector('.stat-number');
        if (scoreNumber) {
            scoreNumber.textContent = `${Math.round(stats.wellbeing_score || 0)}%`;
        }
    }
    
    // Card 1: Day Streak
    if (statCards.length >= 2) {
        const streakNumber = statCards[1].querySelector('.stat-number');
        if (streakNumber) {
            streakNumber.textContent = stats.current_streak || 0;
        }
    }
    
    // Card 2: Completion Rate
    if (statCards.length >= 3) {
        const completionNumber = statCards[2].querySelector('.stat-number');
        if (completionNumber) {
            completionNumber.textContent = `${Math.round(stats.completion_rate || 0)}%`;
        }
    }

    // Card 3: Points This Week
    if (statCards.length >= 4) {
        const pointsNumber = statCards[3].querySelector('.stat-number');
        if (pointsNumber) {
            pointsNumber.textContent = stats.points_this_week || 0;
        }
    }
    
    // Card 4: Achievements
    if (statCards.length >= 5) {
        const achievementNumber = statCards[4].querySelector('.stat-number');
        if (achievementNumber) {
            achievementNumber.textContent = stats.achievement_count || 0;
        }
    }
}

function updateAchievements(achievements) {
    const container = document.querySelector('.achievements-grid');
    if (!container) return;
    
    if (!achievements || achievements.length === 0) {
        container.innerHTML = `
            <div style="text-align: center; grid-column: 1/-1; padding: 40px;">
                <i class="fa-solid fa-trophy" style="font-size: 3rem; color: #3b82f6; margin-bottom: 10px;"></i>
                <p style="color: #94a3b8;">Start completing daily tasks to unlock achievements!</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = achievements.map(achievement => `
        <div class="achievement-card ${achievement.unlocked ? 'unlocked' : 'locked'}">
            <div class="achievement-icon">
                <i class="fa-solid ${achievement.icon}"></i>
            </div>
            <div class="achievement-info">
                <h4>${achievement.title}</h4>
                <p>${achievement.description}</p>
            </div>
            <div class="achievement-date">${achievement.date || ''}</div>
        </div>
    `).join('');
}

function updateGoals(goals) {
    const container = document.querySelector('.goals-grid');
    if (!container) return;
    
    container.innerHTML = goals.map(goal => `
        <div class="goal-card">
            <div class="goal-header">
                <div class="goal-icon">
                    <i class="fa-solid fa-target"></i>
                </div>
                <div class="goal-progress">
                    <span class="progress-text">${Math.round(goal.progress || 0)}%</span>
                </div>
            </div>
            <h3>${goal.title}</h3>
            <p>Target: ${goal.target} ${goal.unit}</p>
            <div class="progress-bar">
                <div class="progress-fill" style="width: ${Math.round(goal.progress || 0)}%"></div>
            </div>
            <div class="goal-details">
                <span>${goal.current}/${goal.target} ${goal.unit} target</span>
            </div>
        </div>
    `).join('');
}

function updateAIInsights(insights) {
    const container = document.querySelector('.insights-grid');
    if (!container) return;
    
    container.innerHTML = insights.map(insight => `
        <div class="insight-card">
            <div class="insight-header">
                <div class="insight-icon ${insight.status_type}">
                    <i class="fa-solid ${getStatusIcon(insight.status_type)}"></i>
                </div>
                <div class="insight-status">${insight.status}</div>
            </div>
            <h3>${insight.title}</h3>
            <p>${insight.description}</p>
            ${insight.metrics ? `
                <div class="insight-metrics">
                    ${insight.metrics.map(metric => `
                        <div class="metric">
                            <span class="metric-value">${metric.value}</span>
                            <span class="metric-label">${metric.label}</span>
                        </div>
                    `).join('')}
                </div>
            ` : ''}
        </div>
    `).join('');
}

function getStatusIcon(statusType) {
    const icons = {
        'positive': 'fa-arrow-trend-up',
        'warning': 'fa-exclamation-triangle',
        'negative': 'fa-arrow-trend-down',
        'danger': 'fa-triangle-exclamation'
    };
    return icons[statusType] || 'fa-info-circle';
}

// ==================== Chart Functions ====================

function initializeCharts(historicalData) {
    const moodSeries = historicalData?.mood_trend || [];
    const screenSeries = historicalData?.stress_vs_screen_time || [];
    const sleepSeries = historicalData?.sleep_vs_mental_fatigue || [];
    const completionSeries = historicalData?.task_completion || [];
    const focusSeries = historicalData?.usage_vs_concentration || [];

    renderLineChart('moodTrendChart', 'moodTrend', moodSeries, '#ff8a5b', 'Mood Score', 0, 5);
    renderBarChart('screenTimeChart', 'screenTime', screenSeries, '#4ecdc4', 'Hours');
    renderLineChart('sleepQualityChart', 'sleepQuality', sleepSeries, '#60a5fa', 'Sleep Quality', 0, 10);
    renderBarChart('completionChart', 'completion', completionSeries, '#fb7185', 'Completion %', 0, 100);
    renderFocusChart(focusSeries);
}

function getChartOptions(yLabel = '', min = null, max = null) {
    return {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
            intersect: false,
            mode: 'index'
        },
        plugins: {
            legend: {
                display: false
            }
        },
        scales: {
            y: {
                beginAtZero: true,
                min,
                max,
                grid: {
                    color: 'rgba(255,255,255,0.05)'
                },
                ticks: {
                    color: '#94a3b8'
                },
                title: {
                    display: Boolean(yLabel),
                    text: yLabel,
                    color: '#94a3b8'
                }
            },
            x: {
                grid: {
                    display: false
                },
                ticks: {
                    color: '#94a3b8'
                }
            }
        }
    };
}

function renderLineChart(canvasId, chartKey, series, color, label, min = null, max = null) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;
    if (charts[chartKey]) charts[chartKey].destroy();

    charts[chartKey] = new Chart(ctx, {
        type: 'line',
        data: {
            labels: series.map(point => point.date),
            datasets: [{
                label,
                data: series.map(point => point.value),
                borderColor: color,
                backgroundColor: `${color}22`,
                fill: true,
                tension: 0.35,
                pointRadius: 4,
                pointHoverRadius: 6
            }]
        },
        options: getChartOptions(label, min, max)
    });
}

function renderBarChart(canvasId, chartKey, series, color, label, min = null, max = null) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;
    if (charts[chartKey]) charts[chartKey].destroy();

    charts[chartKey] = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: series.map(point => point.date),
            datasets: [{
                label,
                data: series.map(point => point.value),
                backgroundColor: color,
                borderRadius: 10
            }]
        },
        options: getChartOptions(label, min, max)
    });
}

function renderFocusChart(series) {
    const ctx = document.getElementById('focusChart');
    if (!ctx) return;
    if (charts.focus) charts.focus.destroy();

    charts.focus = new Chart(ctx, {
        type: 'line',
        data: {
            labels: series.map(point => point.date),
            datasets: [{
                label: 'Focus Score',
                data: series.map(point => point.value),
                borderColor: '#60a5fa',
                backgroundColor: 'rgba(96, 165, 250, 0.18)',
                fill: true,
                tension: 0.35,
                pointRadius: 4
            }]
        },
        options: getChartOptions('Focus Score', 0, 100)
    });
}

function addPeriodSelectors() {
    document.querySelectorAll('.period-select').forEach(select => {
        select.addEventListener('change', function() {
            const period = this.value;
            const chartKey = this.dataset.chart;
            if (chartKey) {
                updateChartPeriod(chartKey, period);
            }
        });
    });
}

async function updateChartPeriod(chartKey, periodLabel) {
    let periodParam = '7days';
    
    if (periodLabel.includes('30')) {
        periodParam = '30days';
    } else if (periodLabel.includes('3 months') || periodLabel.includes('90')) {
        periodParam = '90days';
    }

    chartPeriods[chartKey] = periodParam;
    
    try {
        const data = await fetchAPI(`/api/dashboard-data?period=${periodParam}`);
        
        if (data && data.historical_data) {
            updateSingleChart(chartKey, data.historical_data);
            showNotification(`Updated ${getChartLabel(chartKey)} to show ${periodLabel}`, 'success');
        }
    } catch (error) {
        console.error('Error updating charts:', error);
        showNotification('Failed to update charts', 'error');
    }
}

function updateCharts(historicalData) {
    initializeCharts(historicalData);
}

function updateSingleChart(chartKey, historicalData) {
    const moodSeries = historicalData?.mood_trend || [];
    const screenSeries = historicalData?.stress_vs_screen_time || [];
    const sleepSeries = historicalData?.sleep_vs_mental_fatigue || [];
    const completionSeries = historicalData?.task_completion || [];
    const focusSeries = historicalData?.usage_vs_concentration || [];

    if (chartKey === 'moodTrend') {
        renderLineChart('moodTrendChart', 'moodTrend', moodSeries, '#ff8a5b', 'Mood Score', 0, 5);
    } else if (chartKey === 'screenTime') {
        renderBarChart('screenTimeChart', 'screenTime', screenSeries, '#4ecdc4', 'Hours', 0, 12);
    } else if (chartKey === 'sleepQuality') {
        renderLineChart('sleepQualityChart', 'sleepQuality', sleepSeries, '#60a5fa', 'Sleep Quality', 0, 10);
    } else if (chartKey === 'completion') {
        renderBarChart('completionChart', 'completion', completionSeries, '#fb7185', 'Completion %', 0, 100);
    } else if (chartKey === 'focus') {
        renderFocusChart(focusSeries);
    }
}

function getChartLabel(chartKey) {
    const labels = {
        moodTrend: 'Mood Trend',
        screenTime: 'Screen Time',
        sleepQuality: 'Sleep Quality',
        completion: 'Task Completion',
        focus: 'Focus & Productivity'
    };
    return labels[chartKey] || 'Chart';
}

// ==================== Utility Functions ====================

function showNotification(message, type = 'info') {
    // Create a simple notification
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        background: ${type === 'error' ? '#ef4444' : type === 'success' ? '#10b981' : '#3b82f6'};
        color: white;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        z-index: 9999;
        animation: slideIn 0.3s ease-out;
    `;
    notification.textContent = message;
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

function exportData() {
    showNotification('Exporting your data...', 'info');
    fetchAPI('/api/export-data?period=30days')
        .then((payload) => {
            if (!payload) return;
            const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.download = 'digital-wellbeing-export.json';
            document.body.appendChild(link);
            link.click();
            link.remove();
            URL.revokeObjectURL(url);
            showNotification('Export complete', 'success');
        });
}

// ==================== CSS Animation ====================

const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);
