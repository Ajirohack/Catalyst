/**
 * Real-time Analysis Module for Catalyst Chrome Extension
 * Provides immediate conflict detection and therapeutic recommendations
 */

(function() {
    'use strict';

    // Prevent multiple injections
    if (window.catalystRealTimeAnalysis) {
        return;
    }
    window.catalystRealTimeAnalysis = true;

    console.log('Catalyst Real-time Analysis module loaded');

    // Configuration
    const ANALYSIS_CONFIG = {
        apiEndpoint: 'http://localhost:8000/api/v1/ai-therapy',
        analysisInterval: 3000, // 3 seconds
        batchSize: 5, // Analyze 5 messages at a time
        urgencyThresholds: {
            low: 0.3,
            medium: 0.5,
            high: 0.7,
            critical: 0.9
        },
        emotionalIndicators: {
            anger: ['angry', 'mad', 'furious', 'pissed', 'hate', 'stupid', 'idiot'],
            sadness: ['sad', 'depressed', 'hurt', 'crying', 'devastated', 'heartbroken'],
            anxiety: ['worried', 'anxious', 'scared', 'nervous', 'panic', 'stress'],
            joy: ['happy', 'excited', 'love', 'amazing', 'wonderful', 'great'],
            frustration: ['frustrated', 'annoyed', 'irritated', 'fed up', 'sick of']
        }
    };

    // State management
    let analysisState = {
        messageBuffer: [],
        lastAnalysis: 0,
        currentEmotionalState: 'neutral',
        conversationTrend: 'stable',
        activeAlerts: [],
        analysisHistory: []
    };

    // Real-time conflict detection patterns
    const CONFLICT_INDICATORS = {
        escalation: {
            patterns: [
                /you (always|never)/gi,
                /that's (stupid|ridiculous|nonsense)/gi,
                /(shut up|leave me alone)/gi,
                /i (hate|can't stand)/gi
            ],
            weight: 0.8,
            urgency: 'high'
        },
        defensiveness: {
            patterns: [
                /(not my fault|you started|but you)/gi,
                /(whatever|fine|sure)/gi,
                /i don't care/gi
            ],
            weight: 0.6,
            urgency: 'medium'
        },
        criticism: {
            patterns: [
                /you're (wrong|stupid|crazy)/gi,
                /(that's|you're) ridiculous/gi,
                /how can you/gi
            ],
            weight: 0.7,
            urgency: 'medium'
        },
        stonewalling: {
            patterns: [
                /^(ok|fine|whatever|sure)$/gi,
                /i'm done/gi,
                /forget it/gi
            ],
            weight: 0.5,
            urgency: 'medium'
        },
        contempt: {
            patterns: [
                /(pathetic|loser|worthless)/gi,
                /you're such a/gi,
                /(roll|rolling) (my )?eyes/gi
            ],
            weight: 0.9,
            urgency: 'critical'
        }
    };

    // Emotional state detection
    function detectEmotionalState(messageText) {
        const text = messageText.toLowerCase();
        const emotions = {};
        
        Object.entries(ANALYSIS_CONFIG.emotionalIndicators).forEach(([emotion, indicators]) => {
            const matches = indicators.filter(indicator => text.includes(indicator));
            emotions[emotion] = matches.length / indicators.length;
        });
        
        // Find dominant emotion
        const dominantEmotion = Object.entries(emotions)
            .reduce((max, [emotion, score]) => score > max.score ? {emotion, score} : max, {emotion: 'neutral', score: 0});
        
        return {
            primary: dominantEmotion.emotion,
            confidence: dominantEmotion.score,
            breakdown: emotions
        };
    }

    // Analyze conversation trend
    function analyzeConversationTrend(messages) {
        if (messages.length < 3) return 'insufficient_data';
        
        const recentMessages = messages.slice(-5);
        let conflictScores = [];
        
        recentMessages.forEach(msg => {
            const analysis = analyzeMessageForConflict(msg.text);
            conflictScores.push(analysis.conflictScore);
        });
        
        // Calculate trend
        const avgScore = conflictScores.reduce((sum, score) => sum + score, 0) / conflictScores.length;
        const trend = conflictScores.length > 1 ? 
            conflictScores[conflictScores.length - 1] - conflictScores[0] : 0;
        
        if (trend > 0.2) return 'escalating';
        if (trend < -0.2) return 'de_escalating';
        if (avgScore > 0.6) return 'high_conflict';
        if (avgScore < 0.3) return 'stable';
        return 'moderate';
    }

    // Analyze single message for conflict indicators
    function analyzeMessageForConflict(messageText) {
        let conflictScore = 0;
        let detectedPatterns = [];
        let urgencyLevel = 'low';
        
        Object.entries(CONFLICT_INDICATORS).forEach(([type, indicator]) => {
            indicator.patterns.forEach(pattern => {
                const matches = messageText.match(pattern);
                if (matches) {
                    conflictScore += indicator.weight * (matches.length * 0.2);
                    detectedPatterns.push({
                        type: type,
                        pattern: pattern.source,
                        matches: matches,
                        weight: indicator.weight
                    });
                    
                    // Update urgency level
                    if (indicator.urgency === 'critical') urgencyLevel = 'critical';
                    else if (indicator.urgency === 'high' && urgencyLevel !== 'critical') urgencyLevel = 'high';
                    else if (indicator.urgency === 'medium' && !['critical', 'high'].includes(urgencyLevel)) urgencyLevel = 'medium';
                }
            });
        });
        
        return {
            conflictScore: Math.min(conflictScore, 1.0),
            patterns: detectedPatterns,
            urgency: urgencyLevel,
            timestamp: Date.now()
        };
    }

    // Perform real-time analysis on message
    async function performRealTimeAnalysis(message) {
        try {
            // Add message to buffer
            analysisState.messageBuffer.push({
                ...message,
                analysisTimestamp: Date.now()
            });
            
            // Keep buffer size manageable
            if (analysisState.messageBuffer.length > 20) {
                analysisState.messageBuffer = analysisState.messageBuffer.slice(-20);
            }
            
            // Immediate conflict detection
            const conflictAnalysis = analyzeMessageForConflict(message.text);
            
            // Emotional state detection
            const emotionalState = detectEmotionalState(message.text);
            
            // Update state
            analysisState.currentEmotionalState = emotionalState.primary;
            analysisState.conversationTrend = analyzeConversationTrend(analysisState.messageBuffer);
            
            // Check for immediate intervention needs
            if (conflictAnalysis.urgency === 'critical' || conflictAnalysis.conflictScore > 0.8) {
                await triggerImmediateIntervention(message, conflictAnalysis, emotionalState);
            }
            
            // Batch analysis every few seconds
            const now = Date.now();
            if (now - analysisState.lastAnalysis > ANALYSIS_CONFIG.analysisInterval) {
                await performBatchAnalysis();
                analysisState.lastAnalysis = now;
            }
            
            // Update UI indicators
            updateRealTimeIndicators(conflictAnalysis, emotionalState);
            
        } catch (error) {
            console.error('Real-time analysis error:', error);
        }
    }

    // Trigger immediate intervention for critical situations
    async function triggerImmediateIntervention(message, conflictAnalysis, emotionalState) {
        const intervention = {
            type: 'immediate',
            urgency: conflictAnalysis.urgency,
            message: message,
            conflictScore: conflictAnalysis.conflictScore,
            emotionalState: emotionalState.primary,
            timestamp: Date.now(),
            recommendations: generateImmediateRecommendations(conflictAnalysis, emotionalState)
        };
        
        // Add to active alerts
        analysisState.activeAlerts.push(intervention);
        
        // Show immediate notification
        showImmediateAlert(intervention);
        
        // Send to backend for logging
        try {
            await fetch(`${ANALYSIS_CONFIG.apiEndpoint}/real-time-coaching`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    project_id: 'real_time_session',
                    message_content: message.text,
                    platform: message.platform,
                    context: {
                        conflict_analysis: conflictAnalysis,
                        emotional_state: emotionalState,
                        conversation_trend: analysisState.conversationTrend,
                        urgency_override: conflictAnalysis.urgency
                    }
                })
            });
        } catch (error) {
            console.error('Failed to send intervention to backend:', error);
        }
    }

    // Generate immediate recommendations
    function generateImmediateRecommendations(conflictAnalysis, emotionalState) {
        const recommendations = [];
        
        if (conflictAnalysis.urgency === 'critical') {
            recommendations.push({
                type: 'pause',
                title: '⚠️ Take a Break',
                message: 'This conversation is becoming heated. Consider taking a 10-minute break.',
                action: 'Suggest: "Let\'s take a short break and come back to this in 10 minutes."'
            });
        }
        
        if (emotionalState.primary === 'anger') {
            recommendations.push({
                type: 'emotional_regulation',
                title: '🧘 Emotional Regulation',
                message: 'Take three deep breaths before responding.',
                action: 'Count to 10 and focus on your breathing.'
            });
        }
        
        if (conflictAnalysis.patterns.some(p => p.type === 'criticism')) {
            recommendations.push({
                type: 'communication_style',
                title: '💬 Softer Communication',
                message: 'Try expressing your needs without criticism.',
                action: 'Use "I feel..." instead of "You always..."'
            });
        }
        
        if (conflictAnalysis.patterns.some(p => p.type === 'defensiveness')) {
            recommendations.push({
                type: 'active_listening',
                title: '👂 Active Listening',
                message: 'Try to understand their perspective first.',
                action: 'Ask: "Help me understand what you\'re feeling."'
            });
        }
        
        return recommendations;
    }

    // Show immediate alert
    function showImmediateAlert(intervention) {
        // Create alert element
        const alert = document.createElement('div');
        alert.className = 'catalyst-immediate-alert';
        alert.innerHTML = `
            <div class="catalyst-alert-header">
                <span class="catalyst-alert-title">🚨 Catalyst Alert</span>
                <button class="catalyst-alert-close">×</button>
            </div>
            <div class="catalyst-alert-content">
                <div class="catalyst-alert-urgency ${intervention.urgency}">
                    ${intervention.urgency.toUpperCase()} PRIORITY
                </div>
                <div class="catalyst-alert-recommendations">
                    ${intervention.recommendations.map(rec => `
                        <div class="catalyst-alert-recommendation">
                            <div class="catalyst-rec-title">${rec.title}</div>
                            <div class="catalyst-rec-message">${rec.message}</div>
                            <div class="catalyst-rec-action">${rec.action}</div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
        
        // Add styles
        const alertStyles = `
            .catalyst-immediate-alert {
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                width: 400px;
                max-width: 90vw;
                background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%);
                color: white;
                border-radius: 12px;
                box-shadow: 0 20px 40px rgba(220, 38, 38, 0.4);
                z-index: 10002;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                animation: catalystAlertSlideIn 0.3s ease-out;
            }
            @keyframes catalystAlertSlideIn {
                from {
                    opacity: 0;
                    transform: translate(-50%, -50%) scale(0.9);
                }
                to {
                    opacity: 1;
                    transform: translate(-50%, -50%) scale(1);
                }
            }
            .catalyst-alert-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 16px 20px;
                border-bottom: 1px solid rgba(255, 255, 255, 0.2);
            }
            .catalyst-alert-title {
                font-weight: 600;
                font-size: 16px;
            }
            .catalyst-alert-close {
                background: rgba(255, 255, 255, 0.2);
                border: none;
                color: white;
                width: 28px;
                height: 28px;
                border-radius: 50%;
                cursor: pointer;
                font-size: 16px;
            }
            .catalyst-alert-content {
                padding: 20px;
            }
            .catalyst-alert-urgency {
                text-align: center;
                padding: 8px 16px;
                border-radius: 20px;
                font-weight: 700;
                font-size: 12px;
                margin-bottom: 16px;
                background: rgba(255, 255, 255, 0.2);
            }
            .catalyst-alert-urgency.critical {
                background: rgba(255, 255, 255, 0.9);
                color: #dc2626;
            }
            .catalyst-alert-recommendation {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                padding: 12px;
                margin-bottom: 12px;
            }
            .catalyst-rec-title {
                font-weight: 600;
                margin-bottom: 6px;
                color: #fbbf24;
            }
            .catalyst-rec-message {
                font-size: 14px;
                margin-bottom: 8px;
                line-height: 1.4;
            }
            .catalyst-rec-action {
                font-style: italic;
                font-size: 13px;
                color: #d1fae5;
                border-left: 3px solid #10b981;
                padding-left: 8px;
            }
        `;
        
        // Inject styles
        const styleSheet = document.createElement('style');
        styleSheet.textContent = alertStyles;
        document.head.appendChild(styleSheet);
        
        // Add event listeners
        alert.querySelector('.catalyst-alert-close').addEventListener('click', () => {
            alert.remove();
            styleSheet.remove();
        });
        
        // Auto-remove after 10 seconds
        setTimeout(() => {
            if (alert.parentNode) {
                alert.remove();
                styleSheet.remove();
            }
        }, 10000);
        
        document.body.appendChild(alert);
    }

    // Perform batch analysis
    async function performBatchAnalysis() {
        if (analysisState.messageBuffer.length === 0) return;
        
        try {
            const recentMessages = analysisState.messageBuffer.slice(-ANALYSIS_CONFIG.batchSize);
            
            const response = await fetch(`${ANALYSIS_CONFIG.apiEndpoint}/analyze-conversation`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    project_id: 'real_time_session',
                    conversation_data: recentMessages.map(msg => ({
                        text: msg.text,
                        sender: msg.sender,
                        timestamp: msg.timestamp,
                        platform: msg.platform
                    })),
                    analysis_types: ['sentiment', 'communication_style', 'conflict_detection'],
                    include_therapeutic: true,
                    custom_context: {
                        real_time: true,
                        conversation_trend: analysisState.conversationTrend,
                        emotional_state: analysisState.currentEmotionalState
                    }
                })
            });
            
            if (response.ok) {
                const analysis = await response.json();
                processAnalysisResults(analysis);
            }
        } catch (error) {
            console.error('Batch analysis error:', error);
        }
    }

    // Process analysis results
    function processAnalysisResults(analysis) {
        // Store in history
        analysisState.analysisHistory.push({
            timestamp: Date.now(),
            analysis: analysis
        });
        
        // Keep history manageable
        if (analysisState.analysisHistory.length > 50) {
            analysisState.analysisHistory = analysisState.analysisHistory.slice(-50);
        }
        
        // Update therapeutic insights if available
        if (window.catalystTherapeuticInsights && analysis.therapeutic_recommendations) {
            window.catalystTherapeuticInsights.showRecommendations(analysis.therapeutic_recommendations);
        }
        
        // Broadcast analysis to other components
        window.dispatchEvent(new CustomEvent('catalystAnalysisUpdate', {
            detail: {
                analysis: analysis,
                trend: analysisState.conversationTrend,
                emotionalState: analysisState.currentEmotionalState
            }
        }));
    }

    // Update real-time indicators
    function updateRealTimeIndicators(conflictAnalysis, emotionalState) {
        // Update therapeutic insights display
        if (window.catalystTherapeuticInsights) {
            window.catalystTherapeuticInsights.updateDisplay(
                conflictAnalysis.conflictScore,
                conflictAnalysis.urgency
            );
        }
        
        // Create or update status indicator
        updateStatusIndicator(conflictAnalysis, emotionalState);
    }

    // Create/update status indicator
    function updateStatusIndicator(conflictAnalysis, emotionalState) {
        let indicator = document.getElementById('catalyst-status-indicator');
        
        if (!indicator) {
            indicator = document.createElement('div');
            indicator.id = 'catalyst-status-indicator';
            
            const indicatorStyles = `
                #catalyst-status-indicator {
                    position: fixed;
                    bottom: 20px;
                    right: 20px;
                    width: 60px;
                    height: 60px;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 24px;
                    z-index: 9999;
                    cursor: pointer;
                    transition: all 0.3s ease;
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
                }
                #catalyst-status-indicator:hover {
                    transform: scale(1.1);
                }
                .catalyst-status-low {
                    background: linear-gradient(135deg, #10b981, #059669);
                }
                .catalyst-status-medium {
                    background: linear-gradient(135deg, #f59e0b, #d97706);
                }
                .catalyst-status-high {
                    background: linear-gradient(135deg, #ef4444, #dc2626);
                }
                .catalyst-status-critical {
                    background: linear-gradient(135deg, #dc2626, #991b1b);
                    animation: catalystPulse 1s infinite;
                }
                @keyframes catalystPulse {
                    0%, 100% { transform: scale(1); }
                    50% { transform: scale(1.05); }
                }
            `;
            
            const styleSheet = document.createElement('style');
            styleSheet.textContent = indicatorStyles;
            document.head.appendChild(styleSheet);
            
            document.body.appendChild(indicator);
        }
        
        // Update indicator based on conflict level
        indicator.className = '';
        let emoji = '💚';
        
        if (conflictAnalysis.urgency === 'critical') {
            indicator.classList.add('catalyst-status-critical');
            emoji = '🚨';
        } else if (conflictAnalysis.urgency === 'high') {
            indicator.classList.add('catalyst-status-high');
            emoji = '⚠️';
        } else if (conflictAnalysis.urgency === 'medium') {
            indicator.classList.add('catalyst-status-medium');
            emoji = '⚡';
        } else {
            indicator.classList.add('catalyst-status-low');
            emoji = '💚';
        }
        
        indicator.textContent = emoji;
        indicator.title = `Conflict Level: ${conflictAnalysis.urgency.toUpperCase()}\nEmotional State: ${emotionalState.primary.toUpperCase()}`;
    }

    // Export functions for use by content script
    window.catalystRealTimeAnalysis = {
        performAnalysis: performRealTimeAnalysis,
        analyzeConflict: analyzeMessageForConflict,
        detectEmotion: detectEmotionalState,
        getAnalysisState: () => analysisState,
        triggerIntervention: triggerImmediateIntervention
    };

    console.log('Real-time analysis module ready');

})();