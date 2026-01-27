"""System monitoring service - Backup and uptime tracking."""

import json
import logging
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Armazenar start time do servidor
SERVER_START_TIME = datetime.now(timezone.utc)


class SystemMonitor:
    """Serviço para monitorar uptime e gerenciar backups."""

    def __init__(self, backup_dir: str = "/tmp/charlee_backups"):
        """
        Inicializar monitor do sistema.

        Args:
            backup_dir: Diretório onde backups serão armazenados
        """
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.uptime_file = self.backup_dir / "uptime.json"

    def get_uptime_seconds(self) -> int:
        """
        Obter uptime do servidor em segundos.

        Returns:
            Uptime em segundos desde o start
        """
        delta = datetime.now(timezone.utc) - SERVER_START_TIME
        return int(delta.total_seconds())

    def get_uptime_formatted(self) -> str:
        """
        Obter uptime formatado como string legível.

        Returns:
            String formatada (e.g., "2d 5h 30m")
        """
        total_seconds = self.get_uptime_seconds()
        days = total_seconds // 86400
        hours = (total_seconds % 86400) // 3600
        minutes = (total_seconds % 3600) // 60

        parts = []
        if days > 0:
            parts.append(f"{days}d")
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")

        return " ".join(parts) if parts else "< 1m"

    def record_uptime(self) -> None:
        """Registrar uptime atual em arquivo."""
        try:
            uptime_data = {
                "last_update": datetime.now(timezone.utc).isoformat(),
                "server_start_time": SERVER_START_TIME.isoformat(),
                "uptime_seconds": self.get_uptime_seconds(),
                "uptime_formatted": self.get_uptime_formatted(),
            }

            with open(self.uptime_file, "w") as f:
                json.dump(uptime_data, f, indent=2)

            logger.info(f"Uptime recorded: {self.get_uptime_formatted()}")
        except Exception as e:
            logger.error(f"Failed to record uptime: {e}")

    def create_database_backup(
        self, db_url: str, backup_name: Optional[str] = None
    ) -> Optional[str]:
        """
        Criar backup do banco de dados PostgreSQL.

        Args:
            db_url: URL de conexão do database (postgres://user:pass@host:port/db)
            backup_name: Nome customizado para o backup (opcional)

        Returns:
            Caminho do arquivo de backup criado ou None se falhar
        """
        try:
            # Parse database URL
            # Format: postgresql://user:password@host:port/database
            if not db_url.startswith("postgresql://"):
                logger.error("Only PostgreSQL databases are supported for backup")
                return None

            # Extrair componentes da URL
            url_parts = db_url.replace("postgresql://", "").split("@")
            if len(url_parts) != 2:
                logger.error("Invalid database URL format")
                return None

            user_pass = url_parts[0].split(":")
            host_db = url_parts[1].split("/")

            if len(user_pass) != 2 or len(host_db) != 2:
                logger.error("Invalid database URL format")
                return None

            db_user = user_pass[0]
            db_password = user_pass[1]
            host_port = host_db[0].split(":")
            db_host = host_port[0]
            db_port = host_port[1] if len(host_port) > 1 else "5432"
            db_name = host_db[1]

            # Criar nome do backup
            if backup_name is None:
                timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
                backup_name = f"charlee_backup_{timestamp}.sql"

            backup_path = self.backup_dir / backup_name

            # Usar pg_dump para criar backup
            env = os.environ.copy()
            env["PGPASSWORD"] = db_password

            cmd = [
                "pg_dump",
                "-h",
                db_host,
                "-p",
                db_port,
                "-U",
                db_user,
                "-d",
                db_name,
                "-F",
                "c",  # Custom format (compressed)
                "-f",
                str(backup_path),
            ]

            result = subprocess.run(
                cmd, env=env, capture_output=True, text=True, timeout=300  # 5 min timeout
            )

            if result.returncode == 0:
                logger.info(f"Database backup created successfully: {backup_path}")
                return str(backup_path)
            else:
                logger.error(f"Database backup failed: {result.stderr}")
                return None

        except subprocess.TimeoutExpired:
            logger.error("Database backup timed out after 5 minutes")
            return None
        except FileNotFoundError:
            logger.error(
                "pg_dump command not found. Install PostgreSQL client tools (postgresql-client)"
            )
            return None
        except Exception as e:
            logger.error(f"Failed to create database backup: {e}", exc_info=True)
            return None

    def get_last_backup_info(self) -> Optional[dict]:
        """
        Obter informações sobre o último backup.

        Returns:
            Dicionário com info do último backup ou None
        """
        try:
            # Listar todos os backups
            backups = sorted(self.backup_dir.glob("charlee_backup_*.sql"), reverse=True)

            if not backups:
                return None

            last_backup = backups[0]
            stat = last_backup.stat()

            return {
                "filename": last_backup.name,
                "path": str(last_backup),
                "size_bytes": stat.st_size,
                "size_mb": round(stat.st_size / (1024 * 1024), 2),
                "created_at": datetime.fromtimestamp(stat.st_ctime, tz=timezone.utc).isoformat(),
            }

        except Exception as e:
            logger.error(f"Failed to get last backup info: {e}")
            return None

    def cleanup_old_backups(self, keep_last_n: int = 5) -> int:
        """
        Remover backups antigos, mantendo apenas os N mais recentes.

        Args:
            keep_last_n: Número de backups a manter

        Returns:
            Número de backups removidos
        """
        try:
            backups = sorted(self.backup_dir.glob("charlee_backup_*.sql"), reverse=True)

            if len(backups) <= keep_last_n:
                return 0

            backups_to_remove = backups[keep_last_n:]
            removed_count = 0

            for backup in backups_to_remove:
                backup.unlink()
                removed_count += 1
                logger.info(f"Removed old backup: {backup.name}")

            return removed_count

        except Exception as e:
            logger.error(f"Failed to cleanup old backups: {e}")
            return 0


# Instância global do monitor
system_monitor = SystemMonitor()
