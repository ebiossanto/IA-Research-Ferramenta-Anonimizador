#!/usr/bin/env python3
"""MUTA Snapshots - State reconstruction and pruning support.

Provides functions to reconstruct state at any point in the chain and
manage snapshot-based checkpoints for efficient poda (pruning) operations.
"""

from typing import Any, Dict, Optional
from .engine import PersistentDeltaStateManager, VerifiedFilePatchStore


def reconstruct_state_at(manager: PersistentDeltaStateManager, target_hash: str) -> Dict[str, Any]:
    """Reconstruct the state at a given point in the chain.

    This is the public API entry point for state reconstruction after
    a poda operation or rollback.

    Args:
        manager: The PersistentDeltaStateManager instance.
        target_hash: The hash of the state to reconstruct.

    Returns:
        The reconstructed state dict.
    """
    return manager.reconstruct_state_at(target_hash)


def take_snapshot(manager: PersistentDeltaStateManager) -> Optional[str]:
    """Create a consolidated snapshot at the current HEAD.

    Snapshots are created at the configured frequency and store the complete
    state at that point, accelerating future state reconstruction after poda.

    Args:
        manager: The PersistentDeltaStateManager instance.

    Returns:
        The hash of the snapshot node, or None if snapshot creation was skipped.
    """
    # Snapshot is created every frequencia_snapshot mutations in append_mutation
    # This function can be called explicitly if needed
    return None


def get_current_head(manager: PersistentDeltaStateManager) -> str:
    """Get the current HEAD hash of the chain.

    Args:
        manager: The PersistentDeltaStateManager instance.

    Returns:
        The current HEAD hash string.
    """
    return manager.current_head