#!/usr/bin/env python3
"""MUTA Engine - Core state persistence manager with cryptographic verification.

Manages immutable state as a hash-linked chain (Merkle-like) of delta mutations.
Each mutation (side effect) is appended with a parent_hash linking to the previous
state, creating an auditable chain from GENESIS to current HEAD.
"""

import hashlib
import json
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from .audit import canonical_json, GENESIS


@dataclass
class VerifiedFilePatchStore:
    """Manages disk persistence validating node hashes in batch.

    Attributes:
        base_dir: Base storage directory (default: "muta_storage").
        versions_dir: Subdirectory for versioned node files.
        history_file: Path to the history JSON file tracking HEAD and count.
    """
    base_dir: str = "muta_storage"
    versions_dir: str = ""
    history_file: str = ""
    count: int = 0

    def __post_init__(self):
        self.base_dir = self.base_dir or "muta_storage"
        self.versions_dir = os.path.join(self.base_dir, "versions")
        os.makedirs(self.versions_dir, exist_ok=True)
        self.history_file = os.path.join(self.base_dir, "history.json")
        if not os.path.exists(self.history_file):
            self.save_history({"head": "", "count": 0})

    def load_history(self) -> Dict[str, Any]:
        """Load the history file tracking HEAD and mutation count."""
        try:
            with open(self.history_file, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"head": "", "count": 0}

    def save_history(self, data: Dict[str, Any]) -> None:
        """Atomically save the history file."""
        temp_file = self.history_file + ".tmp"
        with open(temp_file, "w") as f:
            json.dump(data, f, indent=2)
        os.replace(temp_file, self.history_file)

    def save_node(self, node_hash: str, node_data: Dict[str, Any]) -> None:
        """Persist a node (state delta) to disk with atomic write.

        Args:
            node_hash: SHA-256 hash identifying this node.
            node_data: Dict containing parent_hash, delta, and optional snapshot.
        """
        file_path = os.path.join(self.versions_dir, f"{node_hash}.json")
        temp_file = file_path + ".tmp"
        with open(temp_file, "w") as f:
            json.dump(node_data, f, indent=2)
        os.replace(temp_file, file_path)

    def load_node(self, node_hash: str) -> Dict[str, Any]:
        """Load a node and validate its cryptographic checksum (Anti-adulteration defense).

        Args:
            node_hash: The expected SHA-256 hash of the node.

        Returns:
            The node data dict.

        Raises:
            SecurityError: If the node hash doesn't match its content, or node is missing.
        """
        file_path = os.path.join(self.versions_dir, f"{node_hash}.json")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"[MUTA Crypto Error] Checkpoint missing: {node_hash}")

        with open(file_path, "r") as f:
            node_data = json.load(f)

        # Recalculate hash based on read data for integrity check (MUTA 4.4 priority)
        parent_hash = node_data.get("parent_hash", "")
        delta = node_data.get("delta", {})
        content = f"{parent_hash}:{json.dumps(delta, sort_keys=True)}"
        recalculated_hash = hashlib.sha256(content.encode()).hexdigest()

        if recalculated_hash != node_hash:
            raise SecurityError(
                f"\n[ALERTA DE SEGURANÇA MUTA] Quebra de integridade detectada!\n"
                f"The file '{node_hash}.json' was maliciously altered by an external agent.\n"
                f"Expected hash: {node_hash}\nCalculated hash: {recalculated_hash}"
            )

        return node_data


class PersistentDeltaStateManager:
    """Manages contextual persistent state with snapshot-based checkpointing.

    Maintains a hash-linked chain of state deltas. Snapshots are created at
    configurable frequency to accelerate state reconstruction after poda (pruning).

    Attributes:
        store: The VerifiedFilePatchStore for disk persistence.
        frequencia_snapshot: Create a consolidated snapshot every N mutations (default: 3).
        root_hash: The genesis root hash (MUTA_GENESIS).
        current_head: The current chain head (latest node hash).
        contador_passos: Step counter for snapshot frequency.
    """

    def __init__(self, store: VerifiedFilePatchStore, frequencia_snapshot: int = 3):
        self.store = store
        self.frequencia_snapshot = frequencia_snapshot
        self.root_hash = hashlib.sha256(b"MUTA_GENESIS").hexdigest()

        history = self.store.load_history()
        self.current_head = history["head"] if history["head"] else self.root_hash
        self.contador_passos = history.get("count", 0)

    def append_mutation(self, delta: Dict[str, Any]) -> str:
        """Commit an atomic mutation to disk.

        Each mutation creates a new node linked by parent_hash to the previous HEAD.
        The delta represents the side effect recorded in the book of side effects.

        Args:
            delta: The side effect/state change dict to persist.

        Returns:
            The new HEAD hash after this mutation.
        """
        if not delta:
            return self.current_head

        self.contador_passos += 1
        snapshot_a_salvar = None

        if self.contador_passos % self.frequencia_snapshot == 0:
            snapshot_a_salvar = self.reconstruct_state_at(self.current_head)
            # snapshot_a_salvar.update(delta)  # Snapshot absorve delta por cima

        content = f"{self.current_head}:{json.dumps(delta, sort_keys=True)}"
        new_hash = hashlib.sha256(content.encode()).hexdigest()

        node_data = {
            "parent_hash": self.current_head,
            "delta": delta,
            "snapshot_consolidado": snapshot_a_salvar
        }

        self.store.save_node(new_hash, node_data)
        self.current_head = new_hash
        self.save_history({"head": self.current_head, "count": self.contador_passos})
        return self.current_head

    def reconstruct_state_at(self, target_hash: str) -> Dict[str, Any]:
        """Reconstruct the state at a given point in the chain.

        Walks the chain from target_hash back to root, collecting deltas,
        then applies them in reverse order. If a consolidated snapshot is found
        along the path, it's used as a base to accelerate reconstruction.

        Args:
            target_hash: The hash of the state to reconstruct.

        Returns:
            The reconstructed state dict.
        """
        state: Dict[str, Any] = {}
        path_deltas = []
        cursor = target_hash

        while cursor != self.root_hash:
            node_data = self.store.load_node(cursor)
            if node_data.get("snapshot_consolidado") is not None:
                state.update(node_data["snapshot_consolidado"])
                break
            path_deltas.append(node_data["delta"])
            cursor = node_data["parent_hash"]

        for delta in reversed(path_deltas):
            state.update(delta)
        return state

    def audit_entire_chain(self) -> Tuple[bool, str]:
        """Audit the entire chain of state blocks from HEAD.

        Recursively validates every node's cryptographic integrity from current HEAD
        back to the GENESIS root. Raises SecurityError on first inconsistency.

        Returns:
            (True, "success message") if the entire chain is valid.
            (False, error_message) if any inconsistency is found.
        """
        history = self.store.load_history()
        cursor = history.get("head", self.current_head or self.root_hash)

        if not cursor:
            return True, "Chain empty (Intact Genesis)."

        try:
            while cursor != self.root_hash:
                # The load_node method will raise SecurityError if inconsistency found
                node = self.store.load_node(cursor)
                cursor = node["parent_hash"]
            return True, "Entire persistence chain validated successfully. Integrity 100%."
        except SecurityError as e:
            return False, str(e)


class SecurityError(Exception):
    """Exception for violations of digital signatures or hashes."""
    pass


class NetworkDeltaStateManager:
    """Distributed state manager with agent authentication.

    Extends PersistentDeltaStateManager to add cryptographic authentication
    of mutations via digital signatures, enabling multi-agent operation.
    """

    def __init__(self, store: VerifiedFilePatchStore, authorized_agents: dict[str, str] | None = None):
        # Reuse the base store and state
        self.store = store
        self.root_hash = hashlib.sha256(b"MUTA_GENESIS").hexdigest()
        history = store.load_history()
        self.current_head = history["head"] if history["head"] else self.root_hash
        self.contador_passos = history.get("count", 0)
        # Local database of authorized public keys in the VM
        self.authorized_agents: dict[str, str] = authorized_agents if authorized_agents else {}

    def register_authorized_agent(self, name: str, pub_key: str) -> None:
        """Register an agent as authorized to perform mutations.

        Args:
            name: Agent identifier.
            pub_key: The agent's public key (hex-encoded SHA-256).
        """
        self.authorized_agents[name] = pub_key

    def append_authenticated_mutation(self, delta: dict[str, Any], agent_name: str, signature: str) -> str:
        """Validate the agent's digital signature before advancing HEAD.

        BARRIER 1: Digital signature verification of the payload.
        If the signature doesn't match, the mutation is rejected.

        Args:
            delta: The state delta (side effect) to persist.
            agent_name: The name of the agent initiating the mutation.
            signature: The digital signature produced by the agent's private key.

        Returns:
            The new HEAD hash after this authenticated mutation.

        Raises:
            PermissionError: If the agent is not authorized.
            SecurityError: If the digital signature is invalid.
        """
        if agent_name not in self.authorized_agents:
            raise PermissionError(f"[MUTA Auth Error] Agent '{agent_name}' not authorized in the system.")

        pub_key = self.authorized_agents[agent_name]

        # BARRIER 1: Digital signature verification of the payload
        if not MutaCryptoEngine.verify_signature(delta, signature, pub_key):
            raise SecurityError(f"[MUTA Cryptographic Error] Invalid digital signature for agent '{agent_name}'.")

        self.contador_passos += 1
        content = f"{self.current_head}:{json.dumps(delta, sort_keys=True)}"
        new_hash = hashlib.sha256(content.encode()).hexdigest()

        node_data = {
            "parent_hash": self.current_head,
            "delta": delta,
            "provenance": {
                "agent": agent_name,
                "public_key": pub_key,
                "signature": signature
            }
        }

        self.store.save_node(new_hash, node_data)
        self.current_head = new_hash
        self.save_history({"head": self.current_head, "count": self.contador_passos})
        return self.current_head

    def reconstruct_state(self) -> dict[str, Any]:
        """Reconstruct the full state from the chain.

        Walks the chain from current HEAD back to GENESIS, collecting deltas,
        then applies them in reverse order.

        Returns:
            The complete reconstructed state dict.
        """
        state: dict[str, Any] = {}
        path = []
        cursor = self.current_head
        while cursor != self.root_hash:
            node = self.store.load_node(cursor)
            path.append(node["delta"])
            cursor = node["parent_hash"]
        for delta in reversed(path):
            state.update(delta)
        return state

    def save_history(self, data: dict[str, Any]) -> None:
        """Save history atomically via the store."""
        self.store.save_history(data)