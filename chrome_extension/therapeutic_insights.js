/**
 * Therapeutic Insights Module for Catalyst Chrome Extension
 * Provides real-time therapeutic analysis and conflict detection
 */

(function() {
    'use strict';

    // Prevent multiple injections
    if (window.catalystTherapeuticInsights) {
        return;
    }
    window.catalystTherapeuticInsights = true;

    console.log('Catalyst Therapeutic Insights module loaded');

    // Configuration
    const THERAPEUTIC_CONFIG = {
        conflictDetectionThreshold: 0.7,
        sentimentAnalysisInterval: 2000,
        interventionCooldown: 30000, // 30 seconds between interventions
        urgencyLevels: {
            LOW: 'low',
            MEDIUM: 'medium',
            HIGH: 'high',
            CRITICAL: 'critical'
        },
        therapyApproaches: {
            CBT: 'cognitive_behavioral',
            DBT: 'dialectical_behavioral',
            GOTTMAN: 'gottman_method',
            EMOTIONALLY_FOCUSED: 'emotionally_focused',
            SOLUTION_FOCUSED: 'solution_focused'
        }
    };

    // State management
    let therapeuticState = {
        isActive: true,
        currentApproach: THERAPEUTIC_CONFIG.therapyApproaches.CBT,
        lastIntervention: 0,
        conversationContext: [],
        conflictLevel: 0,
        emotionalState: 'neutral',
        interventionHistory: []
    };

    // Conflict detection patterns
    const CONFLICT_PATTERNS = {
        aggressive: {
            keywords: ['always', 'never', 'you always', 'you never', 'stupid', 'idiot', 'hate'],
            weight: 0.8,
            description: 'Aggressive language detected'
        },
        defensive: {
            keywords: ['not my fault', 'you started', 'but you', 'whatever', 'fine'],
            weight: 0.6,
            description: 'Defensive responses detected'
        },
        dismissive: {
            keywords: ['don\'t care', 'whatever', 'sure', 'fine', 'ok'],
            weight: 0.5,
            description: 'Dismissive communication pattern'
        },
        escalation: {
            keywords: ['shut up', 'leave me alone', 'done talking', 'forget it'],
            weight: 0.9,
            description: 'Conversation escalation detected'
        },
        criticism: {
            keywords: ['you\'re wrong', 'that\'s stupid', 'ridiculous', 'nonsense'],
            weight: 0.7,
            description: 'Critical communication detected'
        }
    };

    // Therapeutic intervention templates
    const INTERVENTION_TEMPLATES = {
        [THERAPEUTIC_CONFIG.therapyApproaches.CBT]: {
            conflict_de_escalation: {
                title: "Cognitive Reframing Suggestion",
                message: "Consider reframing this thought: Instead of focusing on what's wrong, try expressing what you need or feel.",
                action: "Try saying: 'I feel [emotion] when [situation]. I need [specific request].'"
            },
            active_listening: {
                title: "Active Listening Reminder",
                message: "Practice active listening by reflecting back what you heard before responding.",
                action: "Try: 'What I hear you saying is... Is that right?'"
            },
            emotional_regulation: {
                title: "Emotional Regulation",
                message: "Take a moment to breathe and identify your emotions before responding.",
                action: "Pause, breathe deeply, and ask: 'What am I feeling right now?'"
            }
        },
        [THERAPEUTIC_CONFIG.therapyApproaches.GOTTMAN]: {
            soft_startup: {
                title: "Soft Startup Technique",
                message: "Use a soft startup to address concerns without criticism or blame.",
                action: "Start with: 'I feel...' instead of 'You always...' or 'You never...'"
            },
            repair_attempt: {
                title: "Repair Attempt",
                message: "This might be a good time for a repair attempt to de-escalate.",
                action: "Try: 'Can we take a break?' or 'I'm feeling overwhelmed, can we slow down?'"
            },
            positive_sentiment: {
                title: "Build Positive Sentiment",
                message: "Remember something you appreciate about this person.",
                action: "Express one thing you value about them or your relationship."
            }
        },
        [THERAPEUTIC_CONFIG.therapyApproaches.DBT]: {
            distress_tolerance: {
                title: "Distress Tolerance",
                message: "Use TIPP technique: Temperature, Intense exercise, Paced breathing, Paired muscle relaxation.",
                action: "Take 5 deep breaths before responding."
            },
            wise_mind: {
                title: "Wise Mind",
                message: "Access your wise mind - the balance between emotion and logic.",
                action: "Ask: 'What would be most effective right now?'"
            },
            interpersonal_effectiveness: {
                title: "DEAR MAN Technique",
                message: "Use DEAR MAN: Describe, Express, Assert, Reinforce, Mindful, Appear confident, Negotiate.",
                action: "Describe the situation factually without judgment."
            }
        }
    };

    // Real-time conflict detection
    function analyzeMessageForConflict(messageText, context = []) {
        if (!messageText || typeof messageText !== 'string') {
            return { conflictScore: 0, patterns: [], urgency: THERAPEUTIC_CONFIG.urgencyLevels.LOW };
        }

        const text = messageText.toLowerCase();
        let conflictScore = 0;
        let detectedPatterns = [];

        // Check for conflict patterns
        Object.entries(CONFLICT_PATTERNS).forEach(([patternName, pattern]) => {
            const matches = pattern.keywords.filter(keyword => text.includes(keyword));
            if (matches.length > 0) {
                conflictScore += pattern.weight * (matches.length / pattern.keywords.length);
                detectedPatterns.push({
                    type: patternName,
                    description: pattern.description,
                    matches: matches,
                    weight: pattern.weight
                });
            }
        });

        // Analyze context for escalation
        if (context.length > 0) {
            const recentMessages = context.slice(-3);
            const escalationIndicators = recentMessages.filter(msg => 
                msg.text && analyzeMessageForConflict(msg.text).conflictScore > 0.5
            );
            
            if (escalationIndicators.length >= 2) {
                conflictScore += 0.3; // Escalation bonus
                detectedPatterns.push({
                    type: 'escalation_pattern',
                    description: 'Escalating conflict pattern detected',
                    matches: ['pattern_escalation'],
                    weight: 0.3
                });
            }
        }

        // Determine urgency level
        let urgency = THERAPEUTIC_CONFIG.urgencyLevels.LOW;
        if (conflictScore >= 0.9) {
            urgency = THERAPEUTIC_CONFIG.urgencyLevels.CRITICAL;
        } else if (conflictScore >= 0.7) {
            urgency = THERAPEUTIC_CONFIG.urgencyLevels.HIGH;
        } else if (conflictScore >= 0.4) {
            urgency = THERAPEUTIC_CONFIG.urgencyLevels.MEDIUM;
        }

        return {
            conflictScore: Math.min(conflictScore, 1.0),
            patterns: detectedPatterns,
            urgency: urgency,
            recommendations: generateRecommendations(detectedPatterns, urgency)
        };
    }

    // Generate therapeutic recommendations
    function generateRecommendations(patterns, urgency) {
        const recommendations = [];
        const approach = therapeuticState.currentApproach;
        const templates = INTERVENTION_TEMPLATES[approach] || INTERVENTION_TEMPLATES[THERAPEUTIC_CONFIG.therapyApproaches.CBT];

        if (urgency === THERAPEUTIC_CONFIG.urgencyLevels.CRITICAL) {
            recommendations.push({
                type: 'immediate_action',
                priority: 'critical',
                message: 'Consider taking a break from this conversation to cool down.',
                action: 'Suggest: "Let\'s take a 20-minute break and come back to this."'
            });
        }

        // Pattern-specific recommendations
        patterns.forEach(pattern => {
            switch (pattern.type) {
                case 'aggressive':
                    recommendations.push(templates.emotional_regulation || templates.distress_tolerance);
                    break;
                case 'defensive':
                    recommendations.push(templates.active_listening || templates.wise_mind);
                    break;
                case 'dismissive':
                    recommendations.push(templates.repair_attempt || templates.interpersonal_effectiveness);
                    break;
                case 'escalation':
                    recommendations.push(templates.conflict_de_escalation || templates.soft_startup);
                    break;
                case 'criticism':
                    recommendations.push(templates.soft_startup || templates.positive_sentiment);
                    break;
            }
        });

        return recommendations.slice(0, 3); // Limit to top 3 recommendations
    }

    // Create therapeutic insights widget
    function createTherapeuticWidget() {
        // Remove existing widget if present
        const existingWidget = document.getElementById('catalyst-therapeutic-widget');
        if (existingWidget) {
            existingWidget.remove();
        }

        const widget = document.createElement('div');
        widget.id = 'catalyst-therapeutic-widget';
        widget.innerHTML = `
            <div class="catalyst-therapeutic-header">
                <span class="catalyst-therapeutic-title">💙 Therapeutic Insights</span>
                <div class="catalyst-therapeutic-controls">
                    <button id="catalyst-therapeutic-minimize" class="catalyst-btn-icon">−</button>
                    <button id="catalyst-therapeutic-close" class="catalyst-btn-icon">×</button>
                </div>
            </div>
            <div class="catalyst-therapeutic-content">
                <div class="catalyst-conflict-indicator">
                    <div class="catalyst-conflict-level">
                        <span class="catalyst-conflict-label">Conflict Level:</span>
                        <div class="catalyst-conflict-bar">
                            <div class="catalyst-conflict-fill" style="width: 0%"></div>
                        </div>
                        <span class="catalyst-conflict-text">Low</span>
                    </div>
                </div>
                <div class="catalyst-recommendations" id="catalyst-recommendations">
                    <p class="catalyst-no-recommendations">Monitoring conversation for therapeutic opportunities...</p>
                </div>
                <div class="catalyst-therapeutic-actions">
                    <button id="catalyst-request-coaching" class="catalyst-btn-primary">Request Coaching</button>
                    <button id="catalyst-therapeutic-settings" class="catalyst-btn-secondary">Settings</button>
                </div>
            </div>
        `;

        // Add styles
        const styles = `
            #catalyst-therapeutic-widget {
                position: fixed;
                top: 20px;
                right: 20px;
                width: 320px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 12px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                z-index: 10000;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                color: white;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
            .catalyst-therapeutic-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 12px 16px;
                border-bottom: 1px solid rgba(255, 255, 255, 0.2);
            }
            .catalyst-therapeutic-title {
                font-weight: 600;
                font-size: 14px;
            }
            .catalyst-therapeutic-controls {
                display: flex;
                gap: 8px;
            }
            .catalyst-btn-icon {
                background: rgba(255, 255, 255, 0.2);
                border: none;
                color: white;
                width: 24px;
                height: 24px;
                border-radius: 50%;
                cursor: pointer;
                font-size: 12px;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .catalyst-btn-icon:hover {
                background: rgba(255, 255, 255, 0.3);
            }
            .catalyst-therapeutic-content {
                padding: 16px;
            }
            .catalyst-conflict-indicator {
                margin-bottom: 16px;
            }
            .catalyst-conflict-level {
                display: flex;
                align-items: center;
                gap: 8px;
                font-size: 12px;
            }
            .catalyst-conflict-label {
                min-width: 80px;
            }
            .catalyst-conflict-bar {
                flex: 1;
                height: 6px;
                background: rgba(255, 255, 255, 0.2);
                border-radius: 3px;
                overflow: hidden;
            }
            .catalyst-conflict-fill {
                height: 100%;
                background: linear-gradient(90deg, #10b981, #f59e0b, #ef4444);
                transition: width 0.3s ease;
            }
            .catalyst-conflict-text {
                min-width: 40px;
                text-align: right;
                font-weight: 500;
            }
            .catalyst-recommendations {
                margin-bottom: 16px;
                min-height: 60px;
            }
            .catalyst-recommendation {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                padding: 12px;
                margin-bottom: 8px;
                font-size: 13px;
                line-height: 1.4;
            }
            .catalyst-recommendation-title {
                font-weight: 600;
                margin-bottom: 4px;
                color: #fbbf24;
            }
            .catalyst-recommendation-action {
                font-style: italic;
                margin-top: 6px;
                color: #d1fae5;
            }
            .catalyst-no-recommendations {
                font-size: 12px;
                color: rgba(255, 255, 255, 0.7);
                text-align: center;
                margin: 20px 0;
            }
            .catalyst-therapeutic-actions {
                display: flex;
                gap: 8px;
            }
            .catalyst-btn-primary, .catalyst-btn-secondary {
                flex: 1;
                padding: 8px 12px;
                border: none;
                border-radius: 6px;
                font-size: 12px;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.2s ease;
            }
            .catalyst-btn-primary {
                background: rgba(255, 255, 255, 0.9);
                color: #4c1d95;
            }
            .catalyst-btn-primary:hover {
                background: white;
            }
            .catalyst-btn-secondary {
                background: rgba(255, 255, 255, 0.2);
                color: white;
            }
            .catalyst-btn-secondary:hover {
                background: rgba(255, 255, 255, 0.3);
            }
            .catalyst-therapeutic-minimized {
                height: 48px;
                overflow: hidden;
            }
            .catalyst-therapeutic-minimized .catalyst-therapeutic-content {
                display: none;
            }
        `;

        // Inject styles
        const styleSheet = document.createElement('style');
        styleSheet.textContent = styles;
        document.head.appendChild(styleSheet);

        // Add event listeners
        widget.addEventListener('click', (e) => {
            e.stopPropagation();
        });

        // Minimize/maximize functionality
        const minimizeBtn = widget.querySelector('#catalyst-therapeutic-minimize');
        minimizeBtn.addEventListener('click', () => {
            widget.classList.toggle('catalyst-therapeutic-minimized');
            minimizeBtn.textContent = widget.classList.contains('catalyst-therapeutic-minimized') ? '+' : '−';
        });

        // Close functionality
        const closeBtn = widget.querySelector('#catalyst-therapeutic-close');
        closeBtn.addEventListener('click', () => {
            widget.remove();
            therapeuticState.isActive = false;
        });

        // Request coaching functionality
        const coachingBtn = widget.querySelector('#catalyst-request-coaching');
        coachingBtn.addEventListener('click', () => {
            requestTherapeuticCoaching();
        });

        // Settings functionality
        const settingsBtn = widget.querySelector('#catalyst-therapeutic-settings');
        settingsBtn.addEventListener('click', () => {
            showTherapeuticSettings();
        });

        document.body.appendChild(widget);
        return widget;
    }

    // Update conflict level display
    function updateConflictDisplay(conflictScore, urgency) {
        const widget = document.getElementById('catalyst-therapeutic-widget');
        if (!widget) return;

        const fillElement = widget.querySelector('.catalyst-conflict-fill');
        const textElement = widget.querySelector('.catalyst-conflict-text');

        if (fillElement && textElement) {
            const percentage = Math.round(conflictScore * 100);
            fillElement.style.width = `${percentage}%`;
            
            let levelText = 'Low';
            if (urgency === THERAPEUTIC_CONFIG.urgencyLevels.CRITICAL) {
                levelText = 'Critical';
            } else if (urgency === THERAPEUTIC_CONFIG.urgencyLevels.HIGH) {
                levelText = 'High';
            } else if (urgency === THERAPEUTIC_CONFIG.urgencyLevels.MEDIUM) {
                levelText = 'Medium';
            }
            
            textElement.textContent = levelText;
        }
    }

    // Display recommendations
    function displayRecommendations(recommendations) {
        const widget = document.getElementById('catalyst-therapeutic-widget');
        if (!widget) return;

        const recommendationsContainer = widget.querySelector('#catalyst-recommendations');
        if (!recommendationsContainer) return;

        if (recommendations.length === 0) {
            recommendationsContainer.innerHTML = '<p class="catalyst-no-recommendations">Conversation looks healthy! Keep up the good communication.</p>';
            return;
        }

        const recommendationsHTML = recommendations.map(rec => `
            <div class="catalyst-recommendation">
                <div class="catalyst-recommendation-title">${rec.title || 'Suggestion'}</div>
                <div>${rec.message}</div>
                ${rec.action ? `<div class="catalyst-recommendation-action">${rec.action}</div>` : ''}
            </div>
        `).join('');

        recommendationsContainer.innerHTML = recommendationsHTML;
    }

    // Request therapeutic coaching
    async function requestTherapeuticCoaching() {
        try {
            const response = await fetch('http://localhost:8000/api/v1/ai-therapy/real-time-coaching', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    project_id: therapeuticState.activeProject || 'default',
                    message_content: therapeuticState.conversationContext.slice(-1)[0]?.text || '',
                    platform: 'chrome_extension',
                    context: {
                        conflict_level: therapeuticState.conflictLevel,
                        emotional_state: therapeuticState.emotionalState,
                        conversation_history: therapeuticState.conversationContext.slice(-5)
                    }
                })
            });

            if (response.ok) {
                const coaching = await response.json();
                displayCoachingResponse(coaching);
            }
        } catch (error) {
            console.error('Failed to request therapeutic coaching:', error);
        }
    }

    // Display coaching response
    function displayCoachingResponse(coaching) {
        const recommendations = [
            {
                title: 'AI Coaching Suggestion',
                message: coaching.suggestion || 'Take a moment to reflect on your communication style.',
                action: coaching.action_suggestion || 'Consider how you can respond more constructively.'
            }
        ];
        displayRecommendations(recommendations);
    }

    // Show therapeutic settings
    function showTherapeuticSettings() {
        // Create settings modal
        const modal = document.createElement('div');
        modal.id = 'catalyst-therapeutic-settings-modal';
        modal.innerHTML = `
            <div class="catalyst-modal-backdrop">
                <div class="catalyst-modal-content">
                    <div class="catalyst-modal-header">
                        <h3>Therapeutic Settings</h3>
                        <button id="catalyst-close-settings">×</button>
                    </div>
                    <div class="catalyst-modal-body">
                        <div class="catalyst-setting-group">
                            <label>Therapy Approach:</label>
                            <select id="catalyst-therapy-approach">
                                <option value="cognitive_behavioral">Cognitive Behavioral Therapy (CBT)</option>
                                <option value="dialectical_behavioral">Dialectical Behavior Therapy (DBT)</option>
                                <option value="gottman_method">Gottman Method</option>
                                <option value="emotionally_focused">Emotionally Focused Therapy</option>
                                <option value="solution_focused">Solution-Focused Therapy</option>
                            </select>
                        </div>
                        <div class="catalyst-setting-group">
                            <label>Conflict Detection Sensitivity:</label>
                            <input type="range" id="catalyst-sensitivity" min="0.3" max="1.0" step="0.1" value="0.7">
                            <span id="catalyst-sensitivity-value">0.7</span>
                        </div>
                        <div class="catalyst-setting-group">
                            <label>
                                <input type="checkbox" id="catalyst-auto-suggestions" checked>
                                Enable automatic suggestions
                            </label>
                        </div>
                    </div>
                    <div class="catalyst-modal-footer">
                        <button id="catalyst-save-therapeutic-settings" class="catalyst-btn-primary">Save Settings</button>
                    </div>
                </div>
            </div>
        `;

        // Add modal styles
        const modalStyles = `
            #catalyst-therapeutic-settings-modal {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                z-index: 10001;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            }
            .catalyst-modal-backdrop {
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.5);
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .catalyst-modal-content {
                background: white;
                border-radius: 12px;
                width: 400px;
                max-width: 90vw;
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
            }
            .catalyst-modal-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 20px;
                border-bottom: 1px solid #e5e7eb;
            }
            .catalyst-modal-header h3 {
                margin: 0;
                color: #1f2937;
            }
            .catalyst-modal-body {
                padding: 20px;
            }
            .catalyst-setting-group {
                margin-bottom: 16px;
            }
            .catalyst-setting-group label {
                display: block;
                margin-bottom: 8px;
                font-weight: 500;
                color: #374151;
            }
            .catalyst-setting-group select,
            .catalyst-setting-group input[type="range"] {
                width: 100%;
                padding: 8px;
                border: 1px solid #d1d5db;
                border-radius: 6px;
            }
            .catalyst-modal-footer {
                padding: 20px;
                border-top: 1px solid #e5e7eb;
                text-align: right;
            }
        `;

        const modalStyleSheet = document.createElement('style');
        modalStyleSheet.textContent = modalStyles;
        document.head.appendChild(modalStyleSheet);

        document.body.appendChild(modal);

        // Modal event listeners
        modal.querySelector('#catalyst-close-settings').addEventListener('click', () => {
            modal.remove();
            modalStyleSheet.remove();
        });

        modal.querySelector('.catalyst-modal-backdrop').addEventListener('click', (e) => {
            if (e.target === e.currentTarget) {
                modal.remove();
                modalStyleSheet.remove();
            }
        });

        // Settings functionality
        const sensitivitySlider = modal.querySelector('#catalyst-sensitivity');
        const sensitivityValue = modal.querySelector('#catalyst-sensitivity-value');
        
        sensitivitySlider.addEventListener('input', () => {
            sensitivityValue.textContent = sensitivitySlider.value;
        });

        modal.querySelector('#catalyst-save-therapeutic-settings').addEventListener('click', () => {
            const approach = modal.querySelector('#catalyst-therapy-approach').value;
            const sensitivity = parseFloat(modal.querySelector('#catalyst-sensitivity').value);
            const autoSuggestions = modal.querySelector('#catalyst-auto-suggestions').checked;

            // Save settings
            therapeuticState.currentApproach = approach;
            THERAPEUTIC_CONFIG.conflictDetectionThreshold = sensitivity;
            therapeuticState.autoSuggestions = autoSuggestions;

            // Store in chrome storage
            if (typeof chrome !== 'undefined' && chrome.storage) {
                chrome.storage.local.set({
                    therapeuticSettings: {
                        approach,
                        sensitivity,
                        autoSuggestions
                    }
                });
            }

            modal.remove();
            modalStyleSheet.remove();
        });

        // Load current settings
        modal.querySelector('#catalyst-therapy-approach').value = therapeuticState.currentApproach;
        modal.querySelector('#catalyst-sensitivity').value = THERAPEUTIC_CONFIG.conflictDetectionThreshold;
        modal.querySelector('#catalyst-sensitivity-value').textContent = THERAPEUTIC_CONFIG.conflictDetectionThreshold;
    }

    // Process new message for therapeutic analysis
    function processMessageForTherapeuticInsights(messageText, sender, timestamp) {
        if (!therapeuticState.isActive || !messageText) return;

        // Add to conversation context
        therapeuticState.conversationContext.push({
            text: messageText,
            sender: sender,
            timestamp: timestamp || Date.now()
        });

        // Keep only recent messages
        if (therapeuticState.conversationContext.length > 20) {
            therapeuticState.conversationContext = therapeuticState.conversationContext.slice(-20);
        }

        // Analyze for conflict
        const analysis = analyzeMessageForConflict(messageText, therapeuticState.conversationContext);
        
        // Update state
        therapeuticState.conflictLevel = analysis.conflictScore;
        therapeuticState.emotionalState = analysis.urgency;

        // Update UI
        updateConflictDisplay(analysis.conflictScore, analysis.urgency);
        
        // Show recommendations if conflict detected
        if (analysis.conflictScore > THERAPEUTIC_CONFIG.conflictDetectionThreshold) {
            displayRecommendations(analysis.recommendations);
            
            // Check for intervention cooldown
            const now = Date.now();
            if (now - therapeuticState.lastIntervention > THERAPEUTIC_CONFIG.interventionCooldown) {
                therapeuticState.lastIntervention = now;
                
                // Log intervention
                therapeuticState.interventionHistory.push({
                    timestamp: now,
                    conflictScore: analysis.conflictScore,
                    patterns: analysis.patterns,
                    recommendations: analysis.recommendations
                });
            }
        } else if (analysis.recommendations.length === 0) {
            displayRecommendations([]);
        }
    }

    // Initialize therapeutic insights
    function initializeTherapeuticInsights() {
        // Load saved settings
        if (typeof chrome !== 'undefined' && chrome.storage) {
            chrome.storage.local.get(['therapeuticSettings'], (result) => {
                if (result.therapeuticSettings) {
                    const settings = result.therapeuticSettings;
                    therapeuticState.currentApproach = settings.approach || therapeuticState.currentApproach;
                    THERAPEUTIC_CONFIG.conflictDetectionThreshold = settings.sensitivity || THERAPEUTIC_CONFIG.conflictDetectionThreshold;
                    therapeuticState.autoSuggestions = settings.autoSuggestions !== false;
                }
            });
        }

        // Create widget
        createTherapeuticWidget();

        console.log('Therapeutic insights initialized');
    }

    // Export functions for use by content script
    window.catalystTherapeuticInsights = {
        processMessage: processMessageForTherapeuticInsights,
        initialize: initializeTherapeuticInsights,
        analyzeConflict: analyzeMessageForConflict,
        updateDisplay: updateConflictDisplay,
        showRecommendations: displayRecommendations,
        requestCoaching: requestTherapeuticCoaching
    };

    // Auto-initialize if DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeTherapeuticInsights);
    } else {
        initializeTherapeuticInsights();
    }

})();