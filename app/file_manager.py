import logging
import os
import aiofiles
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import urllib.request

logger = logging.getLogger(__name__)

class FileManager:
    """
    Manages file uploads and storage from all channels
    Supports: PDF, DWG, DXF, STL, JPG, PNG, BMP, ZIP, MP4, MOV
    """

    # Allowed file extensions
    ALLOWED_EXTENSIONS = {
        # Documents
        ".pdf": "document",
        ".dwg": "drawing",
        ".dxf": "drawing",

        # 3D Models
        ".stl": "model",
        ".step": "model",
        ".stp": "model",

        # Images
        ".jpg": "image",
        ".jpeg": "image",
        ".png": "image",
        ".bmp": "image",
        ".gif": "image",

        # Archives
        ".zip": "archive",
        ".rar": "archive",
        ".7z": "archive",

        # Video
        ".mp4": "video",
        ".mov": "video",
        ".avi": "video",
        ".mkv": "video",
    }

    # Max file size (100MB)
    MAX_FILE_SIZE = 100 * 1024 * 1024

    def __init__(self, storage_path: str = "./files"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"File storage initialized at {storage_path}")

    def is_allowed_file(self, filename: str) -> bool:
        """Check if file extension is allowed"""
        ext = Path(filename).suffix.lower()
        return ext in self.ALLOWED_EXTENSIONS

    def get_file_type(self, filename: str) -> Optional[str]:
        """Get file type category"""
        ext = Path(filename).suffix.lower()
        return self.ALLOWED_EXTENSIONS.get(ext)

    async def save_file_from_url(self, url: str, lead_id: str,
                                 original_filename: str = None) -> Optional[Dict]:
        """
        Download and save file from URL (Instagram, etc.)
        """
        try:
            # Generate safe filename
            filename = original_filename or Path(url.split("/")[-1]).name
            if not filename:
                filename = f"attachment_{datetime.now().timestamp()}"

            # Check file type
            if not self.is_allowed_file(filename):
                logger.warning(f"File type not allowed: {filename}")
                return None

            # Create lead directory
            lead_dir = self.storage_path / lead_id
            lead_dir.mkdir(parents=True, exist_ok=True)

            file_path = lead_dir / filename

            # Download file
            logger.info(f"Downloading file from {url}")
            urllib.request.urlretrieve(url, str(file_path))

            # Check file size
            file_size = os.path.getsize(file_path)
            if file_size > self.MAX_FILE_SIZE:
                os.remove(file_path)
                logger.error(f"File too large: {filename}")
                return None

            return {
                "filename": filename,
                "file_type": self.get_file_type(filename),
                "file_size": file_size,
                "stored_path": str(file_path),
                "url": url,
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error saving file from URL: {e}")
            return None

    async def save_file_content(self, content: bytes, lead_id: str,
                               filename: str) -> Optional[Dict]:
        """
        Save file content directly
        """
        try:
            # Check file type
            if not self.is_allowed_file(filename):
                logger.warning(f"File type not allowed: {filename}")
                return None

            # Check size
            if len(content) > self.MAX_FILE_SIZE:
                logger.error(f"File too large: {filename}")
                return None

            # Create lead directory
            lead_dir = self.storage_path / lead_id
            lead_dir.mkdir(parents=True, exist_ok=True)

            file_path = lead_dir / filename

            # Save file
            async with aiofiles.open(file_path, mode="wb") as f:
                await f.write(content)

            logger.info(f"File saved: {file_path}")

            return {
                "filename": filename,
                "file_type": self.get_file_type(filename),
                "file_size": len(content),
                "stored_path": str(file_path),
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error saving file content: {e}")
            return None

    async def get_files_for_lead(self, lead_id: str) -> List[Dict]:
        """Get all files for a lead"""
        try:
            lead_dir = self.storage_path / lead_id

            if not lead_dir.exists():
                return []

            files = []
            for file_path in lead_dir.iterdir():
                if file_path.is_file():
                    files.append({
                        "filename": file_path.name,
                        "file_type": self.get_file_type(file_path.name),
                        "file_size": os.path.getsize(file_path),
                        "stored_path": str(file_path),
                        "timestamp": datetime.fromtimestamp(
                            file_path.stat().st_mtime
                        ).isoformat()
                    })

            return files

        except Exception as e:
            logger.error(f"Error getting files for lead: {e}")
            return []

    async def delete_file(self, lead_id: str, filename: str) -> bool:
        """Delete a file"""
        try:
            file_path = self.storage_path / lead_id / filename

            if file_path.exists():
                os.remove(file_path)
                logger.info(f"File deleted: {file_path}")
                return True

            return False

        except Exception as e:
            logger.error(f"Error deleting file: {e}")
            return False

    async def get_file_content(self, lead_id: str, filename: str) -> Optional[bytes]:
        """Read file content"""
        try:
            file_path = self.storage_path / lead_id / filename

            if not file_path.exists():
                return None

            async with aiofiles.open(file_path, mode="rb") as f:
                return await f.read()

        except Exception as e:
            logger.error(f"Error reading file: {e}")
            return None

    def format_attachment_info(self, file_info: Dict) -> str:
        """Format file info for Telegram"""
        emoji = self._get_file_emoji(file_info.get("file_type"))
        size_mb = file_info.get("file_size", 0) / (1024 * 1024)

        return f"{emoji} {file_info.get('filename')} ({size_mb:.1f} MB)"

    @staticmethod
    def _get_file_emoji(file_type: str) -> str:
        """Get emoji for file type"""
        emojis = {
            "document": "📄",
            "drawing": "📐",
            "model": "🔧",
            "image": "🖼️",
            "archive": "📦",
            "video": "🎬"
        }
        return emojis.get(file_type, "📎")

    async def cleanup_old_files(self, days: int = 30) -> int:
        """Delete files older than specified days"""
        try:
            from datetime import timedelta
            import time

            cutoff_time = time.time() - (days * 24 * 3600)
            deleted_count = 0

            for lead_dir in self.storage_path.iterdir():
                if lead_dir.is_dir():
                    for file_path in lead_dir.iterdir():
                        if file_path.is_file():
                            if file_path.stat().st_mtime < cutoff_time:
                                os.remove(file_path)
                                deleted_count += 1

            logger.info(f"Cleaned up {deleted_count} old files")
            return deleted_count

        except Exception as e:
            logger.error(f"Error cleaning up old files: {e}")
            return 0

    def get_storage_stats(self) -> Dict:
        """Get storage statistics"""
        try:
            total_size = 0
            file_count = 0
            type_counts = {}

            for lead_dir in self.storage_path.iterdir():
                if lead_dir.is_dir():
                    for file_path in lead_dir.iterdir():
                        if file_path.is_file():
                            file_count += 1
                            total_size += os.path.getsize(file_path)

                            file_type = self.get_file_type(file_path.name)
                            type_counts[file_type] = type_counts.get(file_type, 0) + 1

            return {
                "total_size": total_size,
                "total_size_mb": total_size / (1024 * 1024),
                "file_count": file_count,
                "type_counts": type_counts
            }

        except Exception as e:
            logger.error(f"Error getting storage stats: {e}")
            return {}

    def format_storage_info(self) -> str:
        """Format storage info for Telegram"""
        stats = self.get_storage_stats()

        return f"""💾 <b>Хранилище файлов</b>

📊 <b>Статистика:</b>
📂 Файлов: {stats.get('file_count', 0)}
💽 Размер: {stats.get('total_size_mb', 0):.1f} MB

📋 <b>По типам:</b>
📄 Документы: {stats.get('type_counts', {}).get('document', 0)}
📐 Чертежи: {stats.get('type_counts', {}).get('drawing', 0)}
🔧 Модели: {stats.get('type_counts', {}).get('model', 0)}
🖼️ Изображения: {stats.get('type_counts', {}).get('image', 0)}
📦 Архивы: {stats.get('type_counts', {}).get('archive', 0)}
🎬 Видео: {stats.get('type_counts', {}).get('video', 0)}
"""
