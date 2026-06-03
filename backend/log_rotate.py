"""
SMAR-IA — Política de retención de logs (ISO 27001 A.8.15, A.12.4.1)
===================================================================
Elimina los archivos de auditoría JSON más antiguos que RETENTION_DAYS.
Ejecutar como tarea programada (cron, systemd timer o Scheduled Tasks).
"""

import os
import re
import time
import argparse
from datetime import datetime, timezone, timedelta

LOGS_DIR = os.path.join(os.path.dirname(__file__), "logs")
RETENTION_DAYS = 90
LOG_PATTERN = re.compile(r"^audit_(\d{4}-\d{2}-\d{2})\.json$")


def rotate_logs(days: int = RETENTION_DAYS, dry_run: bool = False):
    """
    Elimina archivos audit_YYYY-MM-DD.json anteriores a N días.
    Si dry_run=True, solo lista los archivos que se eliminarían.
    """
    if not os.path.isdir(LOGS_DIR):
        print(f"[log_rotate] Directorio no encontrado: {LOGS_DIR}")
        return

    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    cutoff_str = cutoff.strftime("%Y-%m-%d")
    removed = 0

    for fname in os.listdir(LOGS_DIR):
        match = LOG_PATTERN.match(fname)
        if not match:
            continue
        file_date_str = match.group(1)
        if file_date_str < cutoff_str:
            fpath = os.path.join(LOGS_DIR, fname)
            if dry_run:
                print(f"[log_rotate] [DRY-RUN] Se eliminaría: {fpath}")
            else:
                try:
                    os.remove(fpath)
                    print(f"[log_rotate] Eliminado: {fpath}")
                    removed += 1
                except OSError as e:
                    print(f"[log_rotate] Error eliminando {fpath}: {e}")

    if dry_run:
        print(f"[log_rotate] [DRY-RUN] {removed} archivos candidatos a rotación (cutoff={cutoff_str})")
    else:
        print(f"[log_rotate] Rotación completada: {removed} archivos eliminados (retención={days} días)")


def main():
    parser = argparse.ArgumentParser(description="Rotación de logs de auditoría SMAR-IA")
    parser.add_argument("--days", type=int, default=RETENTION_DAYS,
                        help=f"Días de retención (default: {RETENTION_DAYS})")
    parser.add_argument("--dry-run", action="store_true",
                        help="Solo simular, no eliminar archivos")
    args = parser.parse_args()
    rotate_logs(days=args.days, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
