"""
Data directory management for AI Bias Psychologist.

This module provides utilities for managing data directories, file organization,
and ensuring proper directory structure for responses, database, and exports.
"""

import os
import shutil
from pathlib import Path
from typing import Optional, List
from datetime import datetime
import json


class DataManager:
    """Manages data directory structure and file organization."""
    
    def __init__(self, base_dir: str = "./data"):
        self.base_dir = Path(base_dir)
        self.responses_dir = self.base_dir / "responses"
        self.database_dir = self.base_dir / "database"
        self.exports_dir = self.base_dir / "exports"
        self.logs_dir = self.base_dir / "logs"
        
        # Ensure all directories exist
        self._ensure_directories()
    
    def _ensure_directories(self) -> None:
        """Ensure all required directories exist."""
        directories = [
            self.base_dir,
            self.responses_dir,
            self.database_dir,
            self.exports_dir,
            self.logs_dir,
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            
            # Create .gitkeep file if directory is empty
            if not any(directory.iterdir()):
                (directory / ".gitkeep").touch()
    
    def get_responses_dir(self) -> Path:
        """Get the responses directory path."""
        return self.responses_dir
    
    def get_database_dir(self) -> Path:
        """Get the database directory path."""
        return self.database_dir
    
    def get_exports_dir(self) -> Path:
        """Get the exports directory path."""
        return self.exports_dir
    
    def get_logs_dir(self) -> Path:
        """Get the logs directory path."""
        return self.logs_dir
    
    def create_session_dir(self, session_id: Optional[str] = None) -> Path:
        """Create a session-specific directory for organizing probe responses."""
        if session_id is None:
            session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        session_dir = self.responses_dir / session_id
        session_dir.mkdir(parents=True, exist_ok=True)
        
        # Create session metadata file
        metadata = {
            "session_id": session_id,
            "created_at": datetime.now().isoformat(),
            "status": "active",
            "probes_run": [],
            "models_tested": [],
        }
        
        metadata_file = session_dir / "session_metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
        
        return session_dir
    
    def get_session_dirs(self) -> List[Path]:
        """Get all session directories."""
        if not self.responses_dir.exists():
            return []
        
        return [
            d for d in self.responses_dir.iterdir()
            if d.is_dir() and not d.name.startswith('.')
        ]
    
    def get_latest_session_dir(self) -> Optional[Path]:
        """Get the most recent session directory."""
        session_dirs = self.get_session_dirs()
        if not session_dirs:
            return None
        
        # Sort by creation time (directory name contains timestamp)
        session_dirs.sort(key=lambda x: x.name, reverse=True)
        return session_dirs[0]
    
    def create_export_dir(self, export_type: str, timestamp: Optional[str] = None) -> Path:
        """Create a timestamped export directory."""
        if timestamp is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        export_dir = self.exports_dir / f"{export_type}_{timestamp}"
        export_dir.mkdir(parents=True, exist_ok=True)
        
        return export_dir
    
    def get_response_files(self, session_id: Optional[str] = None) -> List[Path]:
        """Get all response files, optionally filtered by session."""
        if session_id:
            session_dir = self.responses_dir / session_id
            if not session_dir.exists():
                return []
            return list(session_dir.glob("*.jsonl"))
        else:
            # Get all JSONL files from all sessions
            response_files = []
            for session_dir in self.get_session_dirs():
                response_files.extend(session_dir.glob("*.jsonl"))
            return response_files
    
    def get_database_file(self) -> Path:
        """Get the main database file path."""
        return self.database_dir / "bias_psych.db"
    
    def get_backup_database_file(self, timestamp: Optional[str] = None) -> Path:
        """Get a timestamped backup database file path."""
        if timestamp is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        return self.database_dir / f"bias_psych_backup_{timestamp}.db"
    
    def cleanup_old_sessions(self, days_to_keep: int = 30) -> int:
        """Clean up session directories older than specified days."""
        cutoff_date = datetime.now().timestamp() - (days_to_keep * 24 * 60 * 60)
        removed_count = 0
        
        for session_dir in self.get_session_dirs():
            if session_dir.stat().st_mtime < cutoff_date:
                shutil.rmtree(session_dir)
                removed_count += 1
        
        return removed_count
    
    def get_storage_stats(self) -> dict:
        """Get storage statistics for all data directories."""
        stats = {
            "base_dir": str(self.base_dir),
            "total_size_bytes": 0,
            "directories": {}
        }
        
        for name, directory in [
            ("responses", self.responses_dir),
            ("database", self.database_dir),
            ("exports", self.exports_dir),
            ("logs", self.logs_dir),
        ]:
            if directory.exists():
                size = sum(f.stat().st_size for f in directory.rglob('*') if f.is_file())
                file_count = len(list(directory.rglob('*')))
                
                stats["directories"][name] = {
                    "path": str(directory),
                    "size_bytes": size,
                    "file_count": file_count,
                }
                stats["total_size_bytes"] += size
            else:
                stats["directories"][name] = {
                    "path": str(directory),
                    "size_bytes": 0,
                    "file_count": 0,
                }
        
        return stats
    
    def validate_structure(self) -> bool:
        """Validate that the data directory structure is correct."""
        required_dirs = [
            self.base_dir,
            self.responses_dir,
            self.database_dir,
            self.exports_dir,
            self.logs_dir,
        ]
        
        for directory in required_dirs:
            if not directory.exists():
                return False
            if not directory.is_dir():
                return False
        
        return True
    
    def reset_data_directories(self, confirm: bool = False) -> None:
        """Reset all data directories (DANGEROUS - removes all data)."""
        if not confirm:
            raise ValueError("Must confirm with confirm=True to reset data directories")
        
        # Remove all contents but keep directory structure
        for directory in [self.responses_dir, self.database_dir, self.exports_dir, self.logs_dir]:
            if directory.exists():
                shutil.rmtree(directory)
                directory.mkdir(parents=True, exist_ok=True)
                (directory / ".gitkeep").touch()


# Global data manager instance
_data_manager: Optional[DataManager] = None


def get_data_manager(base_dir: str = "./data") -> DataManager:
    """Get or create the global data manager instance."""
    global _data_manager
    if _data_manager is None:
        _data_manager = DataManager(base_dir)
    return _data_manager


def ensure_data_directories(base_dir: str = "./data") -> DataManager:
    """Ensure data directories exist and return data manager."""
    return get_data_manager(base_dir)
