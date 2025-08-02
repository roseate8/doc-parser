"""
File upload and storage management system.
"""
import os
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional
import hashlib
from datetime import datetime


class FileManager:
    """Manages file uploads and storage."""
    
    def __init__(self, upload_dir: str = "uploads"):
        self.upload_dir = Path(upload_dir)
        self.upload_dir.mkdir(exist_ok=True)
        
        # Supported file extensions
        self.supported_extensions = {
            '.pdf', '.docx', '.xlsx', '.html', '.md', '.jpg', '.jpeg', 
            '.png', '.csv', '.txt', '.xml', '.pptx', '.doc', '.xls'
        }
    
    def save_uploaded_file(self, file_content: bytes, filename: str) -> Optional[Path]:
        """
        Save uploaded file content to the uploads directory.
        
        Args:
            file_content: The file content as bytes
            filename: The original filename
            
        Returns:
            Path to the saved file or None if failed
        """
        try:
            # Validate file extension
            file_path = Path(filename)
            if file_path.suffix.lower() not in self.supported_extensions:
                raise ValueError(f"Unsupported file type: {file_path.suffix}")
            
            # Generate unique filename to avoid conflicts
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_hash = hashlib.md5(file_content).hexdigest()[:8]
            safe_filename = f"{timestamp}_{file_hash}_{filename}"
            
            # Save file
            save_path = self.upload_dir / safe_filename
            with open(save_path, 'wb') as f:
                f.write(file_content)
            
            return save_path
            
        except Exception as e:
            print(f"Error saving file: {e}")
            return None
    
    def get_uploaded_files(self) -> List[Dict[str, Any]]:
        """
        Get list of all uploaded files with metadata.
        
        Returns:
            List of dictionaries containing file information
        """
        files = []
        
        if not self.upload_dir.exists():
            return files
        
        for file_path in self.upload_dir.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in self.supported_extensions:
                try:
                    stat = file_path.stat()
                    files.append({
                        'filename': file_path.name,
                        'path': file_path,
                        'size': stat.st_size,
                        'size_mb': round(stat.st_size / (1024 * 1024), 2),
                        'modified': datetime.fromtimestamp(stat.st_mtime),
                        'extension': file_path.suffix.lower()
                    })
                except Exception as e:
                    print(f"Error reading file {file_path}: {e}")
                    continue
        
        # Sort by modification time, newest first
        files.sort(key=lambda x: x['modified'], reverse=True)
        return files
    
    def delete_file(self, filename: str) -> bool:
        """
        Delete a file from the uploads directory.
        
        Args:
            filename: Name of the file to delete
            
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            file_path = self.upload_dir / filename
            if file_path.exists() and file_path.is_file():
                file_path.unlink()
                return True
            return False
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False
    
    def get_file_path(self, filename: str) -> Optional[Path]:
        """
        Get the full path to a file in the uploads directory.
        
        Args:
            filename: Name of the file
            
        Returns:
            Path object if file exists, None otherwise
        """
        file_path = self.upload_dir / filename
        return file_path if file_path.exists() else None
    
    def is_supported_format(self, filename: str) -> bool:
        """
        Check if file format is supported.
        
        Args:
            filename: Name of the file
            
        Returns:
            True if format is supported, False otherwise
        """
        return Path(filename).suffix.lower() in self.supported_extensions
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported file formats."""
        return sorted(list(self.supported_extensions))
    
    def cleanup_old_files(self, days_old: int = 30) -> int:
        """
        Clean up files older than specified days.
        
        Args:
            days_old: Files older than this many days will be deleted
            
        Returns:
            Number of files deleted
        """
        if not self.upload_dir.exists():
            return 0
        
        deleted_count = 0
        cutoff_time = datetime.now().timestamp() - (days_old * 24 * 60 * 60)
        
        for file_path in self.upload_dir.iterdir():
            if file_path.is_file():
                try:
                    if file_path.stat().st_mtime < cutoff_time:
                        file_path.unlink()
                        deleted_count += 1
                except Exception as e:
                    print(f"Error deleting old file {file_path}: {e}")
        
        return deleted_count
    
    def get_storage_info(self) -> Dict[str, Any]:
        """
        Get storage information for the uploads directory.
        
        Returns:
            Dictionary with storage statistics
        """
        if not self.upload_dir.exists():
            return {
                'total_files': 0,
                'total_size': 0,
                'total_size_mb': 0,
                'upload_dir': str(self.upload_dir)
            }
        
        total_files = 0
        total_size = 0
        
        for file_path in self.upload_dir.iterdir():
            if file_path.is_file():
                total_files += 1
                try:
                    total_size += file_path.stat().st_size
                except Exception:
                    pass
        
        return {
            'total_files': total_files,
            'total_size': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'upload_dir': str(self.upload_dir)
        }