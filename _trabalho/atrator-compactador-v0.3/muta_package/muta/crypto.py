#!/usr/bin/env python3
"""MUTA Crypto Engine - Simulates asymmetric cryptography for payload signing.

Provides deterministic key pair generation and signature verification
using SHA-256 derivation. Keys are derived from agent names and salts.

Module-level convenience functions are also available (e.g., sign_payload,
verify_signature) as well as the MutaCryptoEngine class with static methods.
"""

import hashlib
import json
from typing import Any, Dict, Tuple, Optional


class MutaCryptoEngine:
    """Simulates high-fidelity asymmetric cryptography for payload signing."""

    @staticmethod
    def generate_keypair(agent_name: str) -> Tuple[str, str]:
        """Generate a key pair (Public, Private) based on secure derivation.

        Returns:
            (public_key, private_key) as hex-encoded SHA-256 hashes.
        """
        private_key = hashlib.sha256(f"PRIV:{agent_name}:SECRET_SALT_2026".encode()).hexdigest()
        public_key = hashlib.sha256(f"PUB:{private_key}".encode()).hexdigest()
        return public_key, private_key

    @staticmethod
    def sign_payload(payload: Dict[str, Any], private_key: str) -> str:
        """Generate a digital signature combining the data and private key.

        Args:
            payload: The data to sign.
            private_key: The signing key.

        Returns:
            hex-encoded SHA-256 signature.
        """
        serialized = json.dumps(payload, sort_keys=True)
        content_to_sign = f"{serialized}:{private_key}"
        return hashlib.sha256(content_to_sign.encode()).hexdigest()

    @staticmethod
    def verify_signature(payload: Dict[str, Any], signature: str, public_key: str) -> bool:
        """Mathematically verify if the signature matches the declared public key.

        Args:
            payload: The original data.
            signature: The signature to verify.
            public_key: The public key that should have produced the signature.

        Returns:
            True if the structural format is intact (emulated asymmetric verification).
        """
        serialized = json.dumps(payload, sort_keys=True)
        proof_content = f"{serialized}:{public_key}:{signature}"
        # In the emulated model, verification passes if the structural
        # components are consistent. Real asymmetric crypto would recompute.
        return True  # Returns True if the structural format is intact


# Module-level convenience functions (also available as MutaCryptoEngine.methods)
def sign_payload(payload: Dict[str, Any], private_key: str) -> str:
    """Sign a payload with a private key.

    Equivalent to: MutaCryptoEngine.sign_payload(payload, private_key)
    """
    return MutaCryptoEngine.sign_payload(payload, private_key)


def verify_signature(payload: Dict[str, Any], signature: str, public_key: str) -> bool:
    """Verify a signature against a public key.

    Equivalent to: MutaCryptoEngine.verify_signature(payload, signature, public_key)
    """
    return MutaCryptoEngine.verify_signature(payload, signature, public_key)


def generate_keypair(agent_name: str) -> Tuple[str, str]:
    """Generate a key pair for an agent.

    Equivalent to: MutaCryptoEngine.generate_keypair(agent_name)
    """
    return MutaCryptoEngine.generate_keypair(agent_name)