-- Migration: Add UserNotifications table
-- Purpose: Store notifications for intelligent alerts and daily reports

CREATE TABLE IF NOT EXISTS user_notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL,  -- 'opportunity', 'career_alert', 'daily_report', etc.
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    reference_id VARCHAR(100),  -- Optional reference to related entity (opportunity ID, etc.)
    priority VARCHAR(20) DEFAULT 'medium',  -- 'low', 'medium', 'high'
    read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    read_at TIMESTAMP,

    INDEX idx_user_notifications_user (user_id),
    INDEX idx_user_notifications_read (user_id, read),
    INDEX idx_user_notifications_type (user_id, type),
    INDEX idx_user_notifications_created (created_at)
);

COMMENT ON TABLE user_notifications IS 'Stores intelligent notifications and alerts for users';
COMMENT ON COLUMN user_notifications.type IS 'Type of notification: opportunity, career_alert, daily_report, stagnation, etc.';
COMMENT ON COLUMN user_notifications.priority IS 'Priority level: low, medium, high';
COMMENT ON COLUMN user_notifications.reference_id IS 'Optional ID of related entity (e.g., opportunity_id)';
