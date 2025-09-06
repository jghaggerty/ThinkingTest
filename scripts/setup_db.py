#!/usr/bin/env python3
"""
Database setup script for AI Bias Psychologist.

This script initializes the SQLite database with the required tables
for storing probe responses, bias scores, and metadata.
"""

import sys
import os
import sqlite3
from pathlib import Path
from datetime import datetime


def create_database_schema(db_path: str) -> None:
    """Create the database schema for AI Bias Psychologist."""
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create sessions table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'active',
            description TEXT,
            metadata TEXT
        )
    """)
    
    # Create models table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS models (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            provider TEXT NOT NULL,
            model_name TEXT NOT NULL,
            version TEXT,
            parameters TEXT,
            context_window INTEGER,
            max_tokens INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(provider, model_name, version)
        )
    """)
    
    # Create probe_responses table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS probe_responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            model_id INTEGER NOT NULL,
            probe_type TEXT NOT NULL,
            variant_id TEXT NOT NULL,
            prompt TEXT NOT NULL,
            response TEXT NOT NULL,
            response_time_ms INTEGER,
            tokens_used INTEGER,
            temperature REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES sessions (id),
            FOREIGN KEY (model_id) REFERENCES models (id)
        )
    """)
    
    # Create bias_scores table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bias_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            model_id INTEGER NOT NULL,
            probe_type TEXT NOT NULL,
            variant_id TEXT NOT NULL,
            raw_score REAL,
            normalized_score REAL,
            effect_size REAL,
            significance_level REAL,
            confidence_interval_lower REAL,
            confidence_interval_upper REAL,
            calibration_error REAL,
            contradiction_rate REAL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES sessions (id),
            FOREIGN KEY (model_id) REFERENCES models (id)
        )
    """)
    
    # Create bias_trends table for longitudinal tracking
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bias_trends (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model_id INTEGER NOT NULL,
            probe_type TEXT NOT NULL,
            variant_id TEXT NOT NULL,
            score REAL NOT NULL,
            measurement_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            session_id TEXT,
            FOREIGN KEY (model_id) REFERENCES models (id),
            FOREIGN KEY (session_id) REFERENCES sessions (id)
        )
    """)
    
    # Create model_metadata table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS model_metadata (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model_id INTEGER NOT NULL,
            metadata_key TEXT NOT NULL,
            metadata_value TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (model_id) REFERENCES models (id),
            UNIQUE(model_id, metadata_key)
        )
    """)
    
    # Create indexes for better performance
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_probe_responses_session ON probe_responses(session_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_probe_responses_model ON probe_responses(model_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_probe_responses_type ON probe_responses(probe_type)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_bias_scores_session ON bias_scores(session_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_bias_scores_model ON bias_scores(model_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_bias_scores_type ON bias_scores(probe_type)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_bias_trends_model ON bias_trends(model_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_bias_trends_type ON bias_trends(probe_type)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_bias_trends_date ON bias_trends(measurement_date)")
    
    # Create triggers for updating timestamps
    cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS update_sessions_timestamp 
        AFTER UPDATE ON sessions
        BEGIN
            UPDATE sessions SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
        END
    """)
    
    conn.commit()
    conn.close()
    
    print(f"Database schema created successfully at: {db_path}")


def insert_initial_data(db_path: str) -> None:
    """Insert initial reference data."""
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Insert known model configurations
    models_data = [
        ("openai", "gpt-4", "gpt-4", "8192", "128000", "8192"),
        ("openai", "gpt-4-turbo", "gpt-4-turbo", "4096", "128000", "4096"),
        ("openai", "gpt-3.5-turbo", "gpt-3.5-turbo", "4096", "16384", "4096"),
        ("anthropic", "claude-3-opus", "claude-3-opus", "4096", "200000", "4096"),
        ("anthropic", "claude-3-sonnet", "claude-3-sonnet", "4096", "200000", "4096"),
        ("anthropic", "claude-3-haiku", "claude-3-haiku", "4096", "200000", "4096"),
        ("ollama", "llama3", "llama3", "2048", "8192", "2048"),
        ("ollama", "llama3:70b", "llama3:70b", "2048", "8192", "2048"),
        ("ollama", "mistral", "mistral", "2048", "8192", "2048"),
        ("ollama", "codellama", "codellama", "2048", "8192", "2048"),
    ]
    
    for provider, model_name, version, max_tokens, context_window, tokens in models_data:
        cursor.execute("""
            INSERT OR IGNORE INTO models 
            (provider, model_name, version, max_tokens, context_window, max_tokens)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (provider, model_name, version, max_tokens, context_window, tokens))
    
    # Insert probe types reference
    probe_types = [
        "prospect_theory", "anchoring", "availability", "framing", "sunk_cost",
        "optimism", "confirmation", "base_rate", "conjunction", "overconfidence"
    ]
    
    # Create a reference table for probe types
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS probe_types (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            probe_type TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    probe_descriptions = {
        "prospect_theory": "Prospect Theory / Loss Aversion",
        "anchoring": "Anchoring Bias",
        "availability": "Availability Heuristic",
        "framing": "Framing Effect",
        "sunk_cost": "Sunk Cost Fallacy",
        "optimism": "Optimism Bias",
        "confirmation": "Confirmation Bias",
        "base_rate": "Base-Rate Neglect",
        "conjunction": "Conjunction Fallacy",
        "overconfidence": "Overconfidence Bias",
    }
    
    for probe_type in probe_types:
        name = probe_descriptions.get(probe_type, probe_type.replace("_", " ").title())
        cursor.execute("""
            INSERT OR IGNORE INTO probe_types (probe_type, name, description)
            VALUES (?, ?, ?)
        """, (probe_type, name, f"Tests for {name.lower()}"))
    
    conn.commit()
    conn.close()
    
    print("Initial reference data inserted successfully")


def ensure_data_directories():
    """Ensure data directories exist."""
    base_dir = Path("./data")
    database_dir = base_dir / "database"
    responses_dir = base_dir / "responses"
    exports_dir = base_dir / "exports"
    logs_dir = base_dir / "logs"
    
    for directory in [base_dir, database_dir, responses_dir, exports_dir, logs_dir]:
        directory.mkdir(parents=True, exist_ok=True)
        if not any(directory.iterdir()):
            (directory / ".gitkeep").touch()
    
    return database_dir / "bias_psych.db"


def main():
    """Main setup function."""
    print("Setting up AI Bias Psychologist database...")
    
    # Ensure data directories exist
    db_path = ensure_data_directories()
    
    print(f"Database path: {db_path}")
    
    # Create database schema
    create_database_schema(str(db_path))
    
    # Insert initial data
    insert_initial_data(str(db_path))
    
    print("✅ Database setup completed successfully!")
    print(f"Database file: {db_path}")
    print(f"Data directory: ./data")


if __name__ == "__main__":
    main()
