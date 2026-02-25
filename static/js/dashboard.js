// Dashboard Functionality

// Initialize elements
const menuToggle = document.getElementById('menuToggle');
const dashboardNav = document.getElementById('dashboardNav');
const navClose = document.getElementById('navClose');
const notifBtn = document.getElementById('notifBtn');
const welcomeTime = document.getElementById('welcomeTime');
const recentList = document.getElementById('recentList');
const notificationToast = document.getElementById('notificationToast');

// Mobile menu toggle
menuToggle.addEventListener('click', () => {
    dashboardNav.classList.toggle('open');
});

navClose.addEventListener('click', () => {
    dashboardNav.classList.remove('open');
});

// Close nav when nav link clicked
document.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', () => {
        dashboardNav.classList.remove('open');
    });
});

// Update welcome message with current time
function updateWelcomeTime() {
    const now = new Date();
    let greeting = 'Good morning';
    const hour = now.getHours();
    
    if (hour >= 12 && hour < 17) {
        greeting = 'Good afternoon';
    } else if (hour >= 17) {
        greeting = 'Good evening';
    }
    
    const timeString = now.toLocaleString('en-US', { 
        weekday: 'long', 
        month: 'short', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
    
    welcomeTime.textContent = `${greeting}! Today is ${timeString}`;
}

// Load recent analyses from localStorage
function loadRecentAnalyses() {
    const recent = JSON.parse(localStorage.getItem('recentAnalyses') || '[]');
    
    // Update counters
    document.getElementById('todayCount').textContent = recent.length;
    
    const healthy = recent.filter(r => r.diagnosis && r.diagnosis.toLowerCase().includes('healthy')).length;
    document.getElementById('healthyCount').textContent = healthy;
    
    const issues = recent.filter(r => r.diagnosis && !r.diagnosis.toLowerCase().includes('healthy')).length;
    document.getElementById('issueCount').textContent = issues;
    
    // Display recent items
    if (recent.length === 0) {
        recentList.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">📭</div>
                <p>No recent analyses yet</p>
                <p class="empty-hint">Start by capturing an image</p>
            </div>
        `;
        return;
    }
    
    recentList.innerHTML = recent.slice(0, 5).map((item, index) => `
        <div class="recent-item">
            ${item.image ? `<img src="${item.image}" class="recent-image" alt="Analysis">` : '<div class="recent-image" style="background:#f0f0f0;display:flex;align-items:center;justify-content:center;">📷</div>'}
            <div class="recent-info">
                <div class="recent-diagnosis">${escapeHtml(item.diagnosis || 'Analysis')}</div>
                <div class="recent-time">${formatTime(item.timestamp)}</div>
                ${item.confidence ? `<div class="recent-confidence">Confidence: ${(item.confidence * 100).toFixed(1)}%</div>` : ''}
            </div>
        </div>
    `).join('');
}

// Show notification
function showNotification(message) {
    notificationToast.textContent = message;
    notificationToast.classList.add('show');
    
    setTimeout(() => {
        notificationToast.classList.remove('show');
    }, 3000);
}

// Format timestamp
function formatTime(timestamp) {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now - date;
    
    if (diff < 60000) return 'Just now';
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
    
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Scroll to section
function scrollToSection(sectionId) {
    const section = document.getElementById(sectionId);
    if (section) {
        section.scrollIntoView({ behavior: 'smooth' });
    }
}

// Initialize chart (placeholder for actual implementation)
function initChart() {
    const canvas = document.getElementById('analysisChart');
    if (!canvas) return;
    
    // Simple chart representation
    const ctx = canvas.getContext('2d');
    canvas.width = 200;
    canvas.height = 100;
    
    // Draw a simple bar chart
    const data = [12, 8, 15, 5];
    const maxVal = Math.max(...data);
    const barWidth = 40;
    const barSpacing = 10;
    
    // Color palette for bars
    const colors = ['#1a472a', '#ff6b35', '#4caf50', '#ff9800'];
    
    ctx.fillStyle = '#f0f0f0';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    data.forEach((val, i) => {
        const x = 20 + (i * (barWidth + barSpacing));
        const height = (val / maxVal) * 80;
        const y = 100 - height;
        
        ctx.fillStyle = colors[i];
        ctx.fillRect(x, y, barWidth, height);
    });
}

// Update statistics
function updateStats() {
    const recent = JSON.parse(localStorage.getItem('recentAnalyses') || '[]');
    document.getElementById('totalAnalyses').textContent = recent.length;
    document.getElementById('weekCount').textContent = `${recent.length} analyses`;
}

// Notification button
notifBtn.addEventListener('click', () => {
    showNotification('✅ All systems operational!');
});

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    updateWelcomeTime();
    loadRecentAnalyses();
    updateStats();
    initChart();
    
    // Update time every minute
    setInterval(updateWelcomeTime, 60000);
    
    // Listen for storage changes (from other tabs)
    window.addEventListener('storage', () => {
        loadRecentAnalyses();
        updateStats();
    });
});

// Touch/swipe support for better mobile experience
let touchStartX = 0;
let touchEndX = 0;

document.addEventListener('touchstart', (e) => {
    touchStartX = e.changedTouches[0].screenX;
});

document.addEventListener('touchend', (e) => {
    touchEndX = e.changedTouches[0].screenX;
    handleSwipe();
});

function handleSwipe() {
    const swipeThreshold = 50;
    if (touchEndX - touchStartX > swipeThreshold) {
        // Swiped right - open menu
        if (touchStartX < 50) {
            dashboardNav.classList.add('open');
        }
    }
    if (touchStartX - touchEndX > swipeThreshold) {
        // Swiped left - close menu
        dashboardNav.classList.remove('open');
    }
}

// Performance optimization for animations
const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
if (prefersReducedMotion) {
    document.documentElement.style.setProperty('--transition', 'none');
}

// Log page load time
window.addEventListener('load', () => {
    const perfData = window.performance.timing;
    const pageLoadTime = perfData.loadEventEnd - perfData.navigationStart;
    console.log(`Dashboard loaded in ${pageLoadTime}ms`);
});
