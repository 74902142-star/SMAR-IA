import httpx
import logging
import os
import asyncio
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger("smar-ia-alerts")

# ── Configuración desde variables de entorno ──────────────
SLACK_WEBHOOK_URL = os.getenv("SMAR_IA_SLACK_WEBHOOK_URL", "")
DISCORD_WEBHOOK_URL = os.getenv("SMAR_IA_DISCORD_WEBHOOK_URL", "")
GENERIC_WEBHOOK_URL = os.getenv("SMAR_IA_WEBHOOK_URL", "")

SMTP_HOST = os.getenv("SMAR_IA_SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMAR_IA_SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMAR_IA_SMTP_USER", "")
SMTP_PASS = os.getenv("SMAR_IA_SMTP_PASS", "")
SMTP_FROM = os.getenv("SMAR_IA_SMTP_FROM", "smar-ia@localhost")
EMAIL_TO = os.getenv("SMAR_IA_EMAIL_TO", "")


def _build_emoji(action: str) -> str:
    if "BLOCK" in action:
        return "🛑"
    elif "ALERT" in action:
        return "⚠️"
    return "🚨"


def _format_slack(ip: str, attack_type: str, confidence: float, action: str) -> dict:
    return {
        "blocks": [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": f"🚨 SMAR-IA: Amenaza detectada", "emoji": True},
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*IP:* `{ip}`"},
                    {"type": "mrkdwn", "text": f"*Ataque:* `{attack_type}`"},
                    {"type": "mrkdwn", "text": f"*Confianza:* `{confidence:.2%}`"},
                    {"type": "mrkdwn", "text": f"*Acción:* `{action}`"},
                ],
            },
            {"type": "divider"},
            {
                "type": "context",
                "elements": [{"type": "mrkdwn", "text": "SMAR-IA IDS · Sistema de Detección de Intrusiones"}],
            },
        ]
    }


def _format_discord(ip: str, attack_type: str, confidence: float, action: str) -> dict:
    emoji = _build_emoji(action)
    return {
        "content": None,
        "embeds": [
            {
                "title": f"{emoji} SMAR-IA: Amenaza detectada",
                "color": 15548997 if "BLOCK" in action else 16776960,
                "fields": [
                    {"name": "IP", "value": f"`{ip}`", "inline": True},
                    {"name": "Ataque", "value": f"`{attack_type}`", "inline": True},
                    {"name": "Confianza", "value": f"{confidence:.2%}", "inline": True},
                    {"name": "Acción", "value": f"`{action}`", "inline": False},
                ],
                "footer": {"text": "SMAR-IA IDS · Sistema de Detección de Intrusiones"},
            }
        ],
    }


def _format_generic(ip: str, attack_type: str, confidence: float, action: str) -> dict:
    emoji = _build_emoji(action)
    return {
        "text": f"{emoji} *AMENAZA DETECTADA*\n"
                f"*IP:* `{ip}`\n"
                f"*Ataque:* {attack_type}\n"
                f"*Confianza:* {confidence:.2%}\n"
                f"*Acción:* {action}\n"
                f"SMAR-IA IDS",
    }


async def _send_slack(ip: str, attack_type: str, confidence: float, action: str):
    if not SLACK_WEBHOOK_URL:
        return
    payload = _format_slack(ip, attack_type, confidence, action)
    try:
        async with httpx.AsyncClient() as client:
            r = await client.post(SLACK_WEBHOOK_URL, json=payload)
            if r.status_code != 200:
                logger.error(f"Slack error: {r.status_code} {r.text}")
    except Exception as e:
        logger.error(f"Slack falló: {e}")


async def _send_discord(ip: str, attack_type: str, confidence: float, action: str):
    if not DISCORD_WEBHOOK_URL:
        return
    payload = _format_discord(ip, attack_type, confidence, action)
    try:
        async with httpx.AsyncClient() as client:
            r = await client.post(DISCORD_WEBHOOK_URL, json=payload)
            if r.status_code != 204:
                logger.error(f"Discord error: {r.status_code} {r.text}")
    except Exception as e:
        logger.error(f"Discord falló: {e}")


async def _send_generic(ip: str, attack_type: str, confidence: float, action: str):
    if not GENERIC_WEBHOOK_URL:
        return
    payload = _format_generic(ip, attack_type, confidence, action)
    try:
        async with httpx.AsyncClient() as client:
            r = await client.post(GENERIC_WEBHOOK_URL, json=payload)
            if r.status_code != 200:
                logger.error(f"Webhook error: {r.status_code} {r.text}")
    except Exception as e:
        logger.error(f"Webhook falló: {e}")


async def _send_email(ip: str, attack_type: str, confidence: float, action: str):
    if not SMTP_HOST or not EMAIL_TO:
        return
    try:
        import aiosmtplib
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"SMAR-IA: {attack_type} detectado desde {ip}"
        msg["From"] = SMTP_FROM
        msg["To"] = EMAIL_TO

        text = f"""
SMAR-IA - Alerta de Seguridad

IP: {ip}
Ataque: {attack_type}
Confianza: {confidence:.2%}
Acción: {action}

---
SMAR-IA IDS
"""
        msg.attach(MIMEText(text, "plain"))

        html = f"""
<html>
<body style="font-family: system-ui, sans-serif; background: #0a0a0f; color: #e2e8f0; padding: 24px;">
<div style="max-width: 600px; margin: 0 auto; border: 1px solid #1e293b; border-radius: 8px; overflow: hidden;">
<div style="background: linear-gradient(135deg, #7c3aed, #ec4899); padding: 16px 24px;">
<h1 style="margin: 0; font-size: 1.2rem;">🚨 SMAR-IA: Amenaza detectada</h1>
</div>
<div style="padding: 24px;">
<table style="width: 100%; border-collapse: collapse;">
<tr><td style="padding: 8px; color: #94a3b8;">IP</td><td style="padding: 8px; font-family: monospace;">{ip}</td></tr>
<tr><td style="padding: 8px; color: #94a3b8;">Ataque</td><td style="padding: 8px; font-family: monospace;">{attack_type}</td></tr>
<tr><td style="padding: 8px; color: #94a3b8;">Confianza</td><td style="padding: 8px;">{confidence:.2%}</td></tr>
<tr><td style="padding: 8px; color: #94a3b8;">Acción</td><td style="padding: 8px; font-family: monospace;">{action}</td></tr>
</table>
</div>
<div style="padding: 12px 24px; background: #0f172a; font-size: 0.75rem; color: #64748b; text-align: center;">
SMAR-IA IDS · Sistema de Detección de Intrusiones
</div>
</div>
</body>
</html>
"""
        msg.attach(MIMEText(html, "html"))

        await aiosmtplib.send(
            msg,
            hostname=SMTP_HOST,
            port=SMTP_PORT,
            username=SMTP_USER,
            password=SMTP_PASS,
            use_tls=SMTP_PORT == 465,
            start_tls=SMTP_PORT == 587,
        )
        logger.info(f"Email alert sent to {EMAIL_TO}")
    except ImportError:
        logger.warning("aiosmtplib no instalado. Email no enviado.")
    except Exception as e:
        logger.error(f"Email falló: {e}")


async def notify_threat(ip: str, attack_type: str, confidence: float, action: str):
    """
    Envía notificaciones a TODOS los canales configurados.
    Soporta: Slack, Discord, webhook genérico y email (SMTP).
    """
    if not any([SLACK_WEBHOOK_URL, DISCORD_WEBHOOK_URL, GENERIC_WEBHOOK_URL, (SMTP_HOST and EMAIL_TO)]):
        logger.debug("Ningún canal de alertas configurado.")
        return

    tasks = []
    if SLACK_WEBHOOK_URL:
        tasks.append(_send_slack(ip, attack_type, confidence, action))
    if DISCORD_WEBHOOK_URL:
        tasks.append(_send_discord(ip, attack_type, confidence, action))
    if GENERIC_WEBHOOK_URL:
        tasks.append(_send_generic(ip, attack_type, confidence, action))
    if SMTP_HOST and EMAIL_TO:
        tasks.append(_send_email(ip, attack_type, confidence, action))

    if tasks:
        await asyncio.gather(*tasks, return_exceptions=True)
