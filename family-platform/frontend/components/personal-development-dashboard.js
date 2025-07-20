class PersonalDevelopmentDashboard {
    constructor() {
        this.apiClient = new APIClient();
        this.currentUser = null;
        this.dashboardData = null;
        this.init();
    }

    async init() {
        try {
            this.currentUser = await this.apiClient.getCurrentUser();
            await this.loadDashboardData();
            this.render();
            this.attachEventListeners();
        } catch (error) {
            console.error('Failed to initialize development dashboard:', error);
            this.showError('Failed to load dashboard data');
        }
    }

    async loadDashboardData() {
        try {
            const [dashboardData, goals, challenges, badges] = await Promise.all([
                this.apiClient.get('/development/dashboard'),
                this.apiClient.get('/development/goals'),
                this.apiClient.get('/development/challenges/my-participations'),
                this.apiClient.get('/development/badges/my-badges')
            ]);

            this.dashboardData = dashboardData;
            this.goals = goals;
            this.challenges = challenges;
            this.badges = badges;
        } catch (error) {
            console.error('Error loading dashboard data:', error);
            throw error;
        }
    }

    render() {
        const container = document.getElementById('development-dashboard');
        if (!container) return;

        container.innerHTML = `
            <div class="development-dashboard">
                <div class="dashboard-header">
                    <h1>Personal Development Journey</h1>
                    <p>Building the best version of yourself for meaningful relationships</p>
                </div>

                <div class="dashboard-stats">
                    ${this.renderStats()}
                </div>

                <div class="dashboard-content">
                    <div class="dashboard-grid">
                        <div class="dashboard-section">
                            <h2>Current Goals</h2>
                            ${this.renderActiveGoals()}
                        </div>

                        <div class="dashboard-section">
                            <h2>Active Challenges</h2>
                            ${this.renderActiveChallenges()}
                        </div>

                        <div class="dashboard-section">
                            <h2>Expertise Levels</h2>
                            ${this.renderExpertise()}
                        </div>

                        <div class="dashboard-section">
                            <h2>Recent Achievements</h2>
                            ${this.renderRecentBadges()}
                        </div>

                        <div class="dashboard-section">
                            <h2>Upcoming Deadlines</h2>
                            ${this.renderUpcomingDeadlines()}
                        </div>

                        <div class="dashboard-section">
                            <h2>Quick Actions</h2>
                            ${this.renderQuickActions()}
                        </div>
                    </div>
                </div>

                <div class="dashboard-recommendations">
                    <h2>Recommended Next Steps</h2>
                    <div id="recommendations-container">
                        ${this.renderRecommendations()}
                    </div>
                </div>
            </div>
        `;
    }

    renderStats() {
        const stats = this.dashboardData.stats;
        
        return `
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-icon">🎯</div>
                    <div class="stat-content">
                        <div class="stat-number">${stats.total_points}</div>
                        <div class="stat-label">Total Points</div>
                    </div>
                </div>
                
                <div class="stat-card">
                    <div class="stat-icon">⚡</div>
                    <div class="stat-content">
                        <div class="stat-number">${stats.active_goals}</div>
                        <div class="stat-label">Active Goals</div>
                    </div>
                </div>
                
                <div class="stat-card">
                    <div class="stat-icon">✅</div>
                    <div class="stat-content">
                        <div class="stat-number">${stats.completed_goals}</div>
                        <div class="stat-label">Completed Goals</div>
                    </div>
                </div>
                
                <div class="stat-card">
                    <div class="stat-icon">🏆</div>
                    <div class="stat-content">
                        <div class="stat-number">${stats.current_challenges}</div>
                        <div class="stat-label">Active Challenges</div>
                    </div>
                </div>
                
                <div class="stat-card">
                    <div class="stat-icon">🎖️</div>
                    <div class="stat-content">
                        <div class="stat-number">${stats.badges_earned}</div>
                        <div class="stat-label">Badges Earned</div>
                    </div>
                </div>
                
                <div class="stat-card">
                    <div class="stat-icon">🔥</div>
                    <div class="stat-content">
                        <div class="stat-number">${stats.development_streak}</div>
                        <div class="stat-label">Day Streak</div>
                    </div>
                </div>
            </div>
        `;
    }

    renderActiveGoals() {
        const activeGoals = this.goals.filter(goal => 
            goal.status === 'not_started' || goal.status === 'in_progress'
        );

        if (activeGoals.length === 0) {
            return `
                <div class="empty-state">
                    <p>No active goals yet</p>
                    <button class="btn btn-primary" onclick="window.location.href='/pages/goals.html'">
                        Set Your First Goal
                    </button>
                </div>
            `;
        }

        return `
            <div class="goals-list">
                ${activeGoals.slice(0, 3).map(goal => `
                    <div class="goal-card" data-goal-id="${goal.id}">
                        <div class="goal-header">
                            <h3>${goal.title}</h3>
                            <span class="goal-category">${this.formatCategory(goal.category)}</span>
                        </div>
                        <div class="goal-progress">
                            <div class="progress-bar">
                                <div class="progress-fill" style="width: ${goal.progress_percentage}%"></div>
                            </div>
                            <span class="progress-text">${goal.progress_percentage}%</span>
                        </div>
                        <div class="goal-actions">
                            <button class="btn btn-sm btn-primary" onclick="this.updateGoalProgress(${goal.id})">
                                Update Progress
                            </button>
                        </div>
                    </div>
                `).join('')}
            </div>
            ${activeGoals.length > 3 ? `<a href="/pages/goals.html" class="view-all-link">View All Goals</a>` : ''}
        `;
    }

    renderActiveChallenges() {
        const activeChallenges = this.challenges.filter(challenge => 
            challenge.status === 'in_progress'
        );

        if (activeChallenges.length === 0) {
            return `
                <div class="empty-state">
                    <p>No active challenges</p>
                    <button class="btn btn-primary" onclick="window.location.href='/pages/challenges.html'">
                        Join a Challenge
                    </button>
                </div>
            `;
        }

        return `
            <div class="challenges-list">
                ${activeChallenges.slice(0, 3).map(challenge => `
                    <div class="challenge-card" data-challenge-id="${challenge.id}">
                        <div class="challenge-header">
                            <h3>${challenge.challenge.title}</h3>
                            <span class="challenge-category">${this.formatCategory(challenge.challenge.category)}</span>
                        </div>
                        <div class="challenge-progress">
                            <div class="progress-info">
                                <span>Days: ${challenge.effort_days_completed}</span>
                                <span>Progress: ${challenge.progress_percentage}%</span>
                            </div>
                        </div>
                        <div class="challenge-actions">
                            <button class="btn btn-sm btn-primary" onclick="this.openChallengeCheckin(${challenge.id})">
                                Daily Check-in
                            </button>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }

    renderExpertise() {
        const expertise = this.dashboardData.expertise;
        const categories = [
            { key: 'fitness', label: 'Fitness', icon: '💪' },
            { key: 'practical_skills', label: 'Practical Skills', icon: '🔧' },
            { key: 'social', label: 'Social', icon: '👥' },
            { key: 'financial', label: 'Financial', icon: '💰' },
            { key: 'intellectual', label: 'Intellectual', icon: '🧠' },
            { key: 'emotional', label: 'Emotional', icon: '❤️' }
        ];

        return `
            <div class="expertise-grid">
                ${categories.map(cat => `
                    <div class="expertise-item">
                        <div class="expertise-icon">${cat.icon}</div>
                        <div class="expertise-info">
                            <div class="expertise-label">${cat.label}</div>
                            <div class="expertise-level ${expertise[cat.key] || 'beginner'}">
                                ${this.formatExpertiseLevel(expertise[cat.key] || 'beginner')}
                            </div>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }

    renderRecentBadges() {
        const recentBadges = this.dashboardData.recent_badges;

        if (recentBadges.length === 0) {
            return `<div class="empty-state"><p>No badges earned yet</p></div>`;
        }

        return `
            <div class="badges-list">
                ${recentBadges.map(badge => `
                    <div class="badge-item">
                        <div class="badge-info">
                            <h4>${badge.name}</h4>
                            <p>+${badge.points_earned} points</p>
                            <span class="badge-date">${this.formatDate(badge.earned_date)}</span>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }

    renderUpcomingDeadlines() {
        const deadlines = this.dashboardData.upcoming_deadlines;

        if (deadlines.length === 0) {
            return `<div class="empty-state"><p>No upcoming deadlines</p></div>`;
        }

        return `
            <div class="deadlines-list">
                ${deadlines.map(deadline => `
                    <div class="deadline-item">
                        <div class="deadline-info">
                            <h4>${deadline.challenge_title}</h4>
                            <div class="deadline-progress">
                                <div class="progress-bar">
                                    <div class="progress-fill" style="width: ${deadline.progress_percentage}%"></div>
                                </div>
                            </div>
                            <span class="deadline-date">${this.formatDeadline(deadline.end_date)}</span>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }

    renderQuickActions() {
        return `
            <div class="quick-actions">
                <button class="action-btn" onclick="this.createNewGoal()">
                    <div class="action-icon">🎯</div>
                    <div class="action-text">Set New Goal</div>
                </button>
                
                <button class="action-btn" onclick="this.browseActiveChallenges()">
                    <div class="action-icon">🏆</div>
                    <div class="action-text">Join Challenge</div>
                </button>
                
                <button class="action-btn" onclick="this.requestFeedback()">
                    <div class="action-icon">💬</div>
                    <div class="action-text">Get Feedback</div>
                </button>
                
                <button class="action-btn" onclick="this.findMentor()">
                    <div class="action-icon">👨‍🏫</div>
                    <div class="action-text">Find Mentor</div>
                </button>
                
                <button class="action-btn" onclick="this.joinSupportGroup()">
                    <div class="action-icon">👥</div>
                    <div class="action-text">Support Group</div>
                </button>
                
                <button class="action-btn" onclick="this.viewProgress()">
                    <div class="action-icon">📈</div>
                    <div class="action-text">View Progress</div>
                </button>
            </div>
        `;
    }

    renderRecommendations() {
        // This would typically come from the API
        const recommendations = [
            {
                type: 'goal',
                title: 'Start Fitness Journey',
                description: 'Begin with daily 20-minute walks to build consistency',
                category: 'fitness',
                difficulty: 'beginner',
                points: 100
            },
            {
                type: 'challenge',
                title: 'Learn Basic Cooking',
                description: 'Master 5 healthy meals this month',
                category: 'practical_skills',
                difficulty: 'beginner',
                points: 200
            }
        ];

        return `
            <div class="recommendations-grid">
                ${recommendations.map(rec => `
                    <div class="recommendation-card">
                        <div class="recommendation-header">
                            <h3>${rec.title}</h3>
                            <span class="recommendation-type">${rec.type}</span>
                        </div>
                        <p>${rec.description}</p>
                        <div class="recommendation-meta">
                            <span class="category">${this.formatCategory(rec.category)}</span>
                            <span class="difficulty">${this.formatDifficulty(rec.difficulty)}</span>
                            <span class="points">+${rec.points} points</span>
                        </div>
                        <button class="btn btn-primary" onclick="this.handleRecommendation('${rec.type}', ${JSON.stringify(rec).replace(/"/g, '&quot;')})">
                            Get Started
                        </button>
                    </div>
                `).join('')}
            </div>
        `;
    }

    attachEventListeners() {
        // Refresh dashboard data every 5 minutes
        setInterval(() => {
            this.loadDashboardData().then(() => {
                this.updateStatsOnly();
            });
        }, 5 * 60 * 1000);
    }

    updateStatsOnly() {
        const statsContainer = document.querySelector('.dashboard-stats');
        if (statsContainer) {
            statsContainer.innerHTML = this.renderStats();
        }
    }

    // Utility methods
    formatCategory(category) {
        return category.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    }

    formatDifficulty(difficulty) {
        return difficulty.charAt(0).toUpperCase() + difficulty.slice(1);
    }

    formatExpertiseLevel(level) {
        const levels = {
            beginner: 'Beginner',
            intermediate: 'Intermediate', 
            advanced: 'Advanced',
            expert: 'Expert'
        };
        return levels[level] || 'Beginner';
    }

    formatDate(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const diffTime = Math.abs(now - date);
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
        
        if (diffDays === 1) return 'Yesterday';
        if (diffDays < 7) return `${diffDays} days ago`;
        return date.toLocaleDateString();
    }

    formatDeadline(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const diffTime = date - now;
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
        
        if (diffDays < 0) return 'Overdue';
        if (diffDays === 0) return 'Today';
        if (diffDays === 1) return 'Tomorrow';
        if (diffDays < 7) return `${diffDays} days`;
        return date.toLocaleDateString();
    }

    showError(message) {
        const container = document.getElementById('development-dashboard');
        if (container) {
            container.innerHTML = `
                <div class="error-state">
                    <h2>Oops! Something went wrong</h2>
                    <p>${message}</p>
                    <button class="btn btn-primary" onclick="location.reload()">Try Again</button>
                </div>
            `;
        }
    }

    // Action handlers
    async updateGoalProgress(goalId) {
        // Open modal for progress update
        const modal = new ProgressUpdateModal(goalId);
        modal.show();
    }

    async openChallengeCheckin(challengeId) {
        // Open challenge check-in modal
        const modal = new ChallengeCheckinModal(challengeId);
        modal.show();
    }

    createNewGoal() {
        window.location.href = '/pages/goals.html?action=create';
    }

    browseActiveChallenges() {
        window.location.href = '/pages/challenges.html';
    }

    requestFeedback() {
        window.location.href = '/pages/feedback.html?action=request';
    }

    findMentor() {
        window.location.href = '/pages/mentorship.html';
    }

    joinSupportGroup() {
        window.location.href = '/pages/support-groups.html';
    }

    viewProgress() {
        window.location.href = '/pages/progress.html';
    }

    handleRecommendation(type, recommendation) {
        if (type === 'goal') {
            window.location.href = `/pages/goals.html?action=create&template=${encodeURIComponent(JSON.stringify(recommendation))}`;
        } else if (type === 'challenge') {
            window.location.href = `/pages/challenges.html?recommended=${recommendation.id}`;
        }
    }
}

// Progress Update Modal
class ProgressUpdateModal {
    constructor(goalId) {
        this.goalId = goalId;
        this.apiClient = new APIClient();
    }

    show() {
        const modalHtml = `
            <div class="modal-overlay" id="progress-modal">
                <div class="modal-content">
                    <div class="modal-header">
                        <h2>Update Goal Progress</h2>
                        <button class="modal-close" onclick="this.close()">&times;</button>
                    </div>
                    <div class="modal-body">
                        <form id="progress-form">
                            <div class="form-group">
                                <label for="progress-description">What did you accomplish?</label>
                                <textarea id="progress-description" name="description" 
                                         placeholder="Describe your progress..." required></textarea>
                            </div>
                            <div class="form-group">
                                <label for="current-value">Current Value (optional)</label>
                                <input type="number" id="current-value" name="currentValue" 
                                       placeholder="e.g., weight, reps, minutes" step="0.1">
                            </div>
                            <div class="form-group">
                                <label>Progress Photos (optional)</label>
                                <input type="file" id="progress-photos" name="photos" 
                                       multiple accept="image/*">
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button class="btn btn-secondary" onclick="this.close()">Cancel</button>
                        <button class="btn btn-primary" onclick="this.submitProgress()">Update Progress</button>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', modalHtml);
    }

    close() {
        const modal = document.getElementById('progress-modal');
        if (modal) {
            modal.remove();
        }
    }

    async submitProgress() {
        const form = document.getElementById('progress-form');
        const formData = new FormData(form);
        
        try {
            const progressData = {
                progress_description: formData.get('description'),
                current_value: formData.get('currentValue') ? parseFloat(formData.get('currentValue')) : null,
                photos: [] // Would handle photo uploads here
            };

            await this.apiClient.put(`/development/goals/${this.goalId}/progress`, progressData);
            
            this.close();
            // Refresh dashboard
            location.reload();
            
        } catch (error) {
            console.error('Error updating progress:', error);
            alert('Failed to update progress. Please try again.');
        }
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PersonalDevelopmentDashboard;
}

// Auto-initialize if on development dashboard page
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('development-dashboard')) {
        new PersonalDevelopmentDashboard();
    }
});