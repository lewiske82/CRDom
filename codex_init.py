#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unified Dev Core 3.0 – Hybrid Memory Edition
Mini CRM-alap + multi-agent vezérlő mag.
"""

import json
import os
import time
import threading
import logging
import socket
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List

CONFIG_FILE = "agents_config.json"
LOG_FILE = "codex_system.log"
MEMORY_LOG = "memory_log.jsonl"
PRIVACY_LOG = "privacy_log.jsonl"
CONSENT_RULES = "consent_rules.json"
AUDIT_LOG = "audit_log.jsonl"

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def now_iso() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def safe_json_dump(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))


def append_jsonl(path: str, record: Dict[str, Any]) -> None:
    with open(path, "a", encoding="utf-8") as f:
        f.write(safe_json_dump(record) + "\n")


def file_exists(path: str) -> bool:
    return Path(path).exists()


def ensure_file(path: str) -> None:
    if not file_exists(path):
        Path(path).touch()


def sha256(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def status_report(level: str, message: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    report = {
        "level": level,
        "message": message,
        "payload": payload or {},
        "timestamp": now_iso()
    }
    print(safe_json_dump(report))
    logging.info(safe_json_dump(report))
    return report


class Agent:
    def __init__(self, name: str, role: str, stack: List[str], responsibilities: List[str], reports_to: Optional[str]):
        self.name = name
        self.role = role
        self.stack = stack or []
        self.responsibilities = responsibilities or []
        self.reports_to = reports_to
        self.status = "initialized"
        logging.info("[%s] létrehozva: %s", self.name, self.role)

    def report_status(self, level: str = "info", message: str = "OK", payload: Optional[Dict[str, Any]] = None):
        report = {
            "agent": self.name,
            "role": self.role,
            "status": self.status,
            "message": message,
            "level": level,
            "payload": payload or {},
            "timestamp": now_iso()
        }
        CodexHub.broadcast(report)
        return report


class CodexHub:
    agents: Dict[str, Agent] = {}
    alerts: List[Dict[str, Any]] = []
    manager: Optional[Agent] = None
    config: Dict[str, Any] = {}

    @staticmethod
    def load_config() -> Dict[str, Any]:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    @classmethod
    def initialize_agents(cls):
        cls.config = cls.load_config()
        for name, data in cls.config["agents"].items():
            agent = Agent(
                name=name,
                role=data["role"],
                stack=data.get("primary_stack", []),
                responsibilities=data.get("responsibilities", []),
                reports_to=data.get("reports_to")
            )
            cls.agents[name] = agent
            if agent.role.lower().startswith("coordinator"):
                cls.manager = agent
        logging.info("Minden agent inicializálva.")

    @classmethod
    def broadcast(cls, report: Dict[str, Any]):
        line = f"[{report['agent']}] ({report['level'].upper()}) {report['message']}"
        print(line)
        logging.info(line)
        cls.alerts.append(report)


class AuditController:
    def __init__(self, tiers: Optional[List[str]] = None):
        self.tiers = tiers or ["app", "security", "compliance"]
        ensure_file(AUDIT_LOG)

    def record(self, tier: str, action: str, actor: str, detail: Dict[str, Any]):
        if tier not in self.tiers:
            tier = "app"
        event = {
            "t": now_iso(),
            "tier": tier,
            "action": action,
            "actor": actor,
            "detail": detail
        }
        append_jsonl(AUDIT_LOG, event)
        CodexHub.broadcast({
            "agent": "audit_controller",
            "level": "info",
            "message": f"Audit esemény rögzítve ({tier}).",
            "timestamp": now_iso(),
            "payload": event
        })


class PrivacyGuardian:
    def __init__(self, policies: Dict[str, Any], auditor: AuditController):
        self.policies = policies or {}
        self.auditor = auditor
        ensure_file(PRIVACY_LOG)
        ensure_file(CONSENT_RULES)
        if os.stat(CONSENT_RULES).st_size == 0:
            with open(CONSENT_RULES, "w", encoding="utf-8") as f:
                json.dump({"consents": {}, "denies": {}, "delete_requests": []}, f, ensure_ascii=False, indent=2)

    def _load_consent(self) -> Dict[str, Any]:
        with open(CONSENT_RULES, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save_consent(self, data: Dict[str, Any]) -> None:
        with open(CONSENT_RULES, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def allowed(self, action: str, key: Optional[str] = None, domain: Optional[str] = None) -> bool:
        if key and key.lower() in [k.lower() for k in self.policies.get("blocked_keys", [])]:
            append_jsonl(PRIVACY_LOG, {"t": now_iso(), "action": action, "key": key, "decision": "blocked"})
            self.auditor.record("compliance", "blocked_key", "privacy_guardian", {"action": action, "key": key})
            return False
        if domain and self.policies.get("allowlist_domains"):
            if domain not in self.policies["allowlist_domains"]:
                append_jsonl(PRIVACY_LOG, {"t": now_iso(), "action": action, "domain": domain, "decision": "denied"})
                self.auditor.record("security", "domain_denied", "privacy_guardian", {"action": action, "domain": domain})
                return False
        c = self._load_consent()
        consents = c.get("consents", {})
        if action in consents and consents[action] is True:
            return True
        denies = c.get("denies", {})
        if action in denies and denies[action] is True:
            return False
        return True

    def request_delete(self, key: str, reason: str = ""):
        c = self._load_consent()
        req = {"t": now_iso(), "key": key, "reason": reason}
        c.setdefault("delete_requests", []).append(req)
        self._save_consent(c)
        append_jsonl(PRIVACY_LOG, {"t": now_iso(), "event": "delete_request", "key": key, "reason": reason})
        self.auditor.record("compliance", "delete_request", "privacy_guardian", req)

    def confirm_delete(self, key: str):
        append_jsonl(PRIVACY_LOG, {"t": now_iso(), "event": "delete_confirmed", "key": key})
        self.auditor.record("compliance", "delete_confirmed", "privacy_guardian", {"key": key})


class MemoryCurator:
    def __init__(self, privacy: PrivacyGuardian, retention_days: int = 3650, auditor: Optional[AuditController] = None):
        self.privacy = privacy
        self.retention_days = retention_days
        self.auditor = auditor
        ensure_file(MEMORY_LOG)

    def log_event(self, user_id: str, namespace: str, data: Dict[str, Any]):
        if not self.privacy.allowed(action="memory_write"):
            CodexHub.broadcast({"agent": "memory_curator", "level": "warning",
                                "message": "Memóriaírás visszautasítva adatvédelmi szabály miatt.", "timestamp": now_iso()})
            return
        record = {"t": now_iso(), "user": user_id, "ns": namespace, "data": data}
        append_jsonl(MEMORY_LOG, record)
        if self.auditor:
            self.auditor.record("app", "memory_write", "memory_curator", {"user": user_id, "ns": namespace})
        CodexHub.broadcast({"agent": "memory_curator", "level": "info",
                            "message": f"Esemény mentve ({namespace}).", "timestamp": now_iso()})

    def delete_by_key(self, key_hash: str):
        if not file_exists(MEMORY_LOG):
            return
        with open(MEMORY_LOG, "r", encoding="utf-8") as f:
            lines = f.readlines()
        with open(MEMORY_LOG, "w", encoding="utf-8") as f:
            for line in lines:
                try:
                    rec = json.loads(line)
                    data = rec.get("data", {})
                    if data.get("_key_hash") == key_hash:
                        continue
                    f.write(line)
                except json.JSONDecodeError:
                    continue
        if self.auditor:
            self.auditor.record("compliance", "memory_delete", "memory_curator", {"key_hash": key_hash})
        CodexHub.broadcast({"agent": "memory_curator", "level": "info",
                            "message": f"Törlés végrehajtva key_hash={key_hash}.", "timestamp": now_iso()})


class ContextWeaver:
    def __init__(self):
        self.context_index: Dict[str, Dict[str, Any]] = {}

    def open_session(self, session_id: str, topic: str, tags: List[str]):
        self.context_index[session_id] = {"topic": topic, "tags": tags, "opened": now_iso()}
        CodexHub.broadcast({"agent": "context_weaver", "level": "info",
                            "message": f"Kontextus megnyitva: {session_id} ({topic}).", "timestamp": now_iso()})

    def attach_memory_excerpt(self, session_id: str, excerpt: Dict[str, Any]):
        CodexHub.broadcast({"agent": "context_weaver", "level": "info",
                            "message": f"Memória-kivonat csatolva: {session_id}.", "timestamp": now_iso(),
                            "payload": {"excerpt": excerpt}})


class SyncBridge:
    def __init__(self):
        self.online = True

    def check_online(self, host: str = "8.8.8.8", port: int = 53, timeout: float = 1.0) -> bool:
        try:
            with socket.create_connection((host, port), timeout=timeout):
                return True
        except OSError:
            return False

    def monitor(self):
        while True:
            online_now = self.check_online()
            if online_now != self.online:
                self.online = online_now
                state = "ONLINE" if self.online else "OFFLINE"
                CodexHub.broadcast({"agent": "sync_bridge", "level": "warning",
                                    "message": f"Hálózati állapot változott: {state}", "timestamp": now_iso()})
            time.sleep(5)


class VaultKeeper:
    def __init__(self, auditor: AuditController):
        self.secrets = {}
        self.auditor = auditor

    def put(self, name: str, value: str, approved: bool):
        if not approved:
            status_report("warning", "Érzékeny művelet: titok mentése jóváhagyás nélkül.", {"secret": name})
            return
        self.secrets[name] = value
        self.auditor.record("security", "secret_store", "vault_keeper", {"secret": name})
        CodexHub.broadcast({"agent": "vault_keeper", "level": "info",
                            "message": f"Titok elraktározva: {name} (hash={sha256(value)[:10]}…)", "timestamp": now_iso()})

    def get(self, name: str) -> Optional[str]:
        return self.secrets.get(name)


class ReflectionAgent:
    def tick(self):
        CodexHub.broadcast({"agent": "reflection_agent", "level": "info",
                            "message": "Napi önreflexió: válaszok tömörsége és hasznossága OK.", "timestamp": now_iso()})


class TrainingManager:
    required_params = ["api_key", "endpoint", "domain"]

    def check_missing(self, params: Dict[str, Optional[str]]) -> List[str]:
        return [p for p in self.required_params if not params.get(p)]

    def eli10_prompt(self, missing: List[str]) -> str:
        if not missing:
            return "Minden alap paraméter megvan. Mehetünk tovább!"
        missing_list = ", ".join(missing)
        return (
            "ELI10: Ahhoz, hogy biztonságosan tovább menjünk, meg kell adnod ezeket: "
            f"{missing_list}. Példa: API-kulcs = 'ABC', endpoint = 'https://...', domain = 'example.com'."
        )


def main():
    status_report("info", "Unified Dev Core 3.0 indítás.")
    CodexHub.initialize_agents()

    auditor = AuditController()
    policies = CodexHub.config.get("memory_policies", {})
    privacy = PrivacyGuardian(policies=policies, auditor=auditor)
    memory = MemoryCurator(privacy=privacy, retention_days=policies.get("default_retention_days", 3650), auditor=auditor)
    context = ContextWeaver()
    sync = SyncBridge()
    vault = VaultKeeper(auditor=auditor)
    reflect = ReflectionAgent()
    trainer = TrainingManager()

    for agent in CodexHub.agents.values():
        agent.report_status(level="info", message="Agent futásra kész.")

    threading.Thread(target=sync.monitor, daemon=True).start()

    session_id = "demo-session-001"
    context.open_session(session_id, topic="project_setup", tags=["init", "memory", "consent"])
    memory.log_event(
        user_id="user-001",
        namespace="onboarding",
        data={"msg": "Első indítás, projekt létrehozva.", "_key_hash": sha256("onboarding:001")}
    )

    missing = trainer.check_missing({"api_key": None, "endpoint": None, "domain": None})
    status_report("info", trainer.eli10_prompt(missing), {"missing": missing})

    if os.getenv("DUMMY_API_TOKEN"):
        vault.put("DUMMY_API_TOKEN", os.environ["DUMMY_API_TOKEN"], approved=False)

    def reflection_loop():
        while True:
            time.sleep(60)
            reflect.tick()

    threading.Thread(target=reflection_loop, daemon=True).start()

    status_report("info", "Rendszer készen áll. Memory/Privacy/Context aktív.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        status_report("warning", "Leállítás kérve.")


if __name__ == "__main__":
    main()
