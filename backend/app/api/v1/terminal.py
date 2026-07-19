import asyncio
import logging
import shlex
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)
router = APIRouter()

ALLOWED_COMMANDS = {"ls", "dir", "pwd", "cd", "echo", "cat", "head", "tail", "wc", "grep",
                    "find", "tree", "date", "whoami", "hostname", "python", "python3",
                    "node", "npm", "pip", "git", "uname", "env"}

BLOCKED_PATTERNS = ["rm -rf", "mkfs", "dd if=", "> /dev/", "chmod 777", "shutdown",
                     "reboot", "halt", "init 0", "init 6", "format", ":(){ :|:& };:"]

SHELL_OPERATORS = ["&&", "||", "|", ";", "`", "$(", "${", ">>", "2>&1"]


def _is_safe_command(cmd: str) -> bool:
    cmd_lower = cmd.lower().strip()
    for pattern in BLOCKED_PATTERNS:
        if pattern in cmd_lower:
            return False
    for op in SHELL_OPERATORS:
        if op in cmd_lower:
            return False
    try:
        parts = shlex.split(cmd)
    except ValueError:
        return False
    if not parts:
        return False
    base = parts[0].split("/")[-1].split("\\")[-1]
    return base in ALLOWED_COMMANDS


@router.websocket("/ws")
async def terminal_ws(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            cmd = await websocket.receive_text()
            if not _is_safe_command(cmd):
                await websocket.send_text(f"Command not allowed: {cmd}\n")
                await websocket.send_text("EXIT:1\n")
                continue
            try:
                args = shlex.split(cmd)
                process = await asyncio.create_subprocess_exec(
                    *args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=30)
                if stdout:
                    output = stdout.decode(errors="replace")
                    if len(output) > 50000:
                        output = output[:50000] + "\n... (output truncated)"
                    await websocket.send_text(output)
                if stderr:
                    err_output = stderr.decode(errors="replace")
                    if len(err_output) > 10000:
                        err_output = err_output[:10000] + "\n... (output truncated)"
                    await websocket.send_text(err_output)
                await websocket.send_text(f"EXIT:{process.returncode}\n")
            except asyncio.TimeoutError:
                await websocket.send_text("Command timed out after 30 seconds\n")
                await websocket.send_text("EXIT:124\n")
            except Exception as e:
                await websocket.send_text(f"Error: {e}\n")
                await websocket.send_text("EXIT:1\n")
    except WebSocketDisconnect:
        logger.info("Terminal WebSocket disconnected")
