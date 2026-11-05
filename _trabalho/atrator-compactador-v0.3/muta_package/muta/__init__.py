# MUTA Package - Core engine for immutable state persistence with cryptographic verification
# Book of side effects ledger (Item 4)

__version__ = "4.4"

from .engine import VerifiedFilePatchStore, PersistentDeltaStateManager, SecurityError, NetworkDeltaStateManager
from .audit import calculate_event_hash, load_events, validate
from .crypto import MutaCryptoEngine, sign_payload, verify_signature, generate_keypair
from .engine import (
    reconstruct_state_at,
    audit_entire_chain,
)
from .snapshots import reconstruct_state_at as reconstruct_snapshot_state, get_current_head, take_snapshot
from .cli import MutaNativeCLI
from .rpc import MutaRPCServer, MutaRPCClient

# Convenience re-exports for test compatibility (imports from Goedel tests)
from .audit import AuditStore, Redactor  # Alias for compatibility
from .broker import RateLimiter  # Minimal compatibility export

# Ensure backward-compatible names exist at package level
# Note: append_mutation is a method of PersistentDeltaStateManager, not a module-level function
# Users should: store = VerifiedFilePatchStore(...); mgr = PersistentDeltaStateManager(store); mgr.append_mutation(delta)
# Or use the convenience: from muta_package.muta import append_mutation as mgr_append (but needs manager)

# Backward-compatible: provide PersistentDeltaStateManager with its methods
# append_mutation is available as: muta.PersistentDeltaStateManager.append_mutation

# Ensure backward-compatible names exist at package level
__all__ = [
    "VerifiedFilePatchStore",
    "PersistentDeltaStateManager",
    "SecurityError",
    "MutaCryptoEngine",
    "MutaNativeCLI",
    "MutaRPCServer",
    "MutaRPCClient",
    "NetworkDeltaStateManager",
    "reconstruct_state_at",
    "audit_entire_chain",
    "calculate_event_hash",
    "load_events",
    "validate",
    "generate_keypair",
    "sign_payload",
    "verify_signature",
    "AuditStore",
    "RateLimiter",
]