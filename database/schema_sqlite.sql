-- Telegram AI Chatbot Management System: database schema (SQLite)
-- Generated from app/models.py (SQLAlchemy). 17 tables: the 16 ERD entities + unknown_questions.
-- Tables are ordered so every foreign key points to a table created above it.
-- Note: the app itself creates/updates tables through Alembic (migrations/); this file is a reference/standalone script.

PRAGMA foreign_keys = ON;

CREATE TABLE bots (
	id INTEGER NOT NULL,
	name VARCHAR(100) NOT NULL,
	username VARCHAR(100) NOT NULL,
	default_language VARCHAR(5) NOT NULL,
	welcome_message TEXT NOT NULL,
	fallback_message TEXT NOT NULL,
	support_contact VARCHAR(200) NOT NULL,
	working_status VARCHAR(20) NOT NULL,
	maintenance_mode BOOLEAN NOT NULL,
	system_prompt TEXT NOT NULL,
	ai_model VARCHAR(100) NOT NULL,
	ai_temperature FLOAT NOT NULL,
	ai_max_length INTEGER NOT NULL,
	response_style VARCHAR(20) NOT NULL,
	PRIMARY KEY (id)
);

CREATE TABLE faqs (
	id INTEGER NOT NULL,
	question TEXT NOT NULL,
	answer TEXT NOT NULL,
	category VARCHAR(50) NOT NULL,
	keywords TEXT NOT NULL,
	language VARCHAR(5) NOT NULL,
	priority INTEGER NOT NULL,
	status VARCHAR(20) NOT NULL,
	PRIMARY KEY (id)
);

CREATE TABLE logs (
	id INTEGER NOT NULL,
	log_type VARCHAR(20) NOT NULL,
	actor VARCHAR(100) NOT NULL,
	action VARCHAR(200) NOT NULL,
	record_id INTEGER,
	details TEXT NOT NULL,
	created_at DATETIME NOT NULL,
	PRIMARY KEY (id)
);

CREATE TABLE roles (
	id INTEGER NOT NULL,
	name VARCHAR(50) NOT NULL,
	permissions JSON NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (name)
);

CREATE TABLE telegram_users (
	id INTEGER NOT NULL,
	telegram_user_id BIGINT NOT NULL,
	username VARCHAR(100),
	full_name VARCHAR(200) NOT NULL,
	language VARCHAR(5) NOT NULL,
	first_interaction_at DATETIME NOT NULL,
	last_interaction_at DATETIME NOT NULL,
	status VARCHAR(20) NOT NULL,
	phone VARCHAR(30),
	email VARCHAR(200),
	PRIMARY KEY (id)
);

CREATE UNIQUE INDEX ix_telegram_users_telegram_user_id ON telegram_users (telegram_user_id);

CREATE TABLE unknown_questions (
	id INTEGER NOT NULL,
	question TEXT NOT NULL,
	frequency INTEGER NOT NULL,
	status VARCHAR(20) NOT NULL,
	last_asked_at DATETIME NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (question)
);

CREATE TABLE admins (
	id INTEGER NOT NULL,
	name VARCHAR(100) NOT NULL,
	email VARCHAR(200) NOT NULL,
	password_hash VARCHAR(255) NOT NULL,
	role_id INTEGER NOT NULL,
	status VARCHAR(20) NOT NULL,
	last_login_at DATETIME,
	PRIMARY KEY (id),
	UNIQUE (email),
	FOREIGN KEY(role_id) REFERENCES roles (id)
);

CREATE TABLE commands (
	id INTEGER NOT NULL,
	bot_id INTEGER NOT NULL,
	name VARCHAR(50) NOT NULL,
	description VARCHAR(200) NOT NULL,
	response TEXT NOT NULL,
	status VARCHAR(20) NOT NULL,
	permission VARCHAR(50) NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(bot_id) REFERENCES bots (id),
	UNIQUE (name)
);

CREATE TABLE intents (
	id INTEGER NOT NULL,
	bot_id INTEGER NOT NULL,
	name VARCHAR(100) NOT NULL,
	description TEXT NOT NULL,
	response TEXT NOT NULL,
	priority INTEGER NOT NULL,
	status VARCHAR(20) NOT NULL,
	entities JSON DEFAULT '[]' NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(bot_id) REFERENCES bots (id),
	UNIQUE (name)
);

CREATE TABLE agents (
	id INTEGER NOT NULL,
	admin_id INTEGER NOT NULL,
	availability VARCHAR(20) NOT NULL,
	PRIMARY KEY (id),
	UNIQUE (admin_id),
	FOREIGN KEY(admin_id) REFERENCES admins (id)
);

CREATE TABLE broadcasts (
	id INTEGER NOT NULL,
	bot_id INTEGER NOT NULL,
	message TEXT NOT NULL,
	audience VARCHAR(20) NOT NULL,
	target_user_ids JSON DEFAULT '[]' NOT NULL,
	status VARCHAR(20) DEFAULT 'draft' NOT NULL,
	scheduled_at DATETIME,
	sent_at DATETIME,
	delivery_result JSON NOT NULL,
	sent_by INTEGER,
	PRIMARY KEY (id),
	FOREIGN KEY(bot_id) REFERENCES bots (id),
	FOREIGN KEY(sent_by) REFERENCES admins (id)
);

CREATE TABLE knowledge_articles (
	id INTEGER NOT NULL,
	title VARCHAR(200) NOT NULL,
	category VARCHAR(50) NOT NULL,
	content TEXT NOT NULL,
	keywords TEXT NOT NULL,
	language VARCHAR(5) NOT NULL,
	author_id INTEGER,
	updated_at DATETIME NOT NULL,
	status VARCHAR(20) NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(author_id) REFERENCES admins (id)
);

CREATE TABLE training_phrases (
	id INTEGER NOT NULL,
	intent_id INTEGER NOT NULL,
	phrase TEXT NOT NULL,
	language VARCHAR(5) NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(intent_id) REFERENCES intents (id)
);

CREATE TABLE conversations (
	id INTEGER NOT NULL,
	user_id INTEGER NOT NULL,
	started_at DATETIME NOT NULL,
	last_message_at DATETIME NOT NULL,
	status VARCHAR(20) NOT NULL,
	intent VARCHAR(100),
	assigned_agent_id INTEGER,
	support_status VARCHAR(20),
	handoff_requested_at DATETIME,
	resolution_status VARCHAR(20) NOT NULL,
	session_step VARCHAR(50),
	context JSON NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(user_id) REFERENCES telegram_users (id),
	FOREIGN KEY(assigned_agent_id) REFERENCES agents (id)
);

CREATE INDEX ix_conversations_user_id ON conversations (user_id);

CREATE TABLE notifications (
	id INTEGER NOT NULL,
	user_id INTEGER NOT NULL,
	broadcast_id INTEGER,
	type VARCHAR(30) NOT NULL,
	content TEXT NOT NULL,
	sent_at DATETIME,
	delivery_status VARCHAR(20) NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(user_id) REFERENCES telegram_users (id),
	FOREIGN KEY(broadcast_id) REFERENCES broadcasts (id)
);

CREATE TABLE messages (
	id INTEGER NOT NULL,
	conversation_id INTEGER NOT NULL,
	user_id INTEGER NOT NULL,
	direction VARCHAR(10) NOT NULL,
	message_type VARCHAR(20) NOT NULL,
	content TEXT NOT NULL,
	response_source VARCHAR(20),
	agent_id INTEGER,
	created_at DATETIME NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(conversation_id) REFERENCES conversations (id),
	FOREIGN KEY(user_id) REFERENCES telegram_users (id),
	FOREIGN KEY(agent_id) REFERENCES agents (id)
);

CREATE INDEX ix_messages_conversation_id ON messages (conversation_id);

CREATE INDEX ix_messages_user_id ON messages (user_id);

CREATE TABLE feedback (
	id INTEGER NOT NULL,
	user_id INTEGER NOT NULL,
	message_id INTEGER,
	conversation_id INTEGER,
	rating INTEGER NOT NULL,
	comment TEXT NOT NULL,
	created_at DATETIME NOT NULL,
	PRIMARY KEY (id),
	FOREIGN KEY(user_id) REFERENCES telegram_users (id),
	FOREIGN KEY(message_id) REFERENCES messages (id),
	FOREIGN KEY(conversation_id) REFERENCES conversations (id)
);

