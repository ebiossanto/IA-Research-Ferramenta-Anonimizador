#!/usr/bin/env python3
"""MUTA CLI - Command-line interface for the MUTA Core engine.

Provides terminal commands for state management:
- status: Show current HEAD and step count
- mutate <json>: Commit an atomic mutation in disk
- rollback <hash>: Rewind physical state to target hash
- verify: Run batch cryptographic integrity verification

Usage: python muta_vm.py <command> [arguments]
"""

import sys
import json
from typing import List, Optional

from .engine import VerifiedFilePatchStore, PersistentDeltaStateManager, SecurityError
from .audit import validate as audit_validate


class MutaNativeCLI:
    """MUTA Native CLI Engine - Handles terminal sys.argv-based commands.

    Commands:
        status      - Display current HEAD and total steps
        mutate <json>  - Commit atomic mutation to disk
        rollback <hash>  - Rewind state to target hash
        verify  - Run batch cryptographic integrity verification
    """

    def __init__(self, store: VerifiedFilePatchStore, manager: PersistentDeltaStateManager):
        self.store = store
        self.manager = manager

    def execute_from_args(self, args: List[str]) -> int:
        """Execute a command from sys.argv list.

        Args:
            args: List of arguments (typically sys.argv).

        Returns:
            Exit code (0 for success, 1 for errors).
        """
        if len(args) < 2:
            self.print_help()
            return 1

        cmd = args[1].lower()

        if cmd == "status":
            self._cmd_status()

        elif cmd == "mutate":
            if len(args) < 3:
                print("[MUTA CLI Error] Usage: python muta_vm.py mutate '<json_delta>'")
                return 1
            try:
                delta_payload = json.loads(args[2])
                new_hash = self.manager.append_mutation(delta_payload)
                print(f"[MUTA SUCCESS] Mutação persistida. Nova HEAD: {new_hash}")
            except Exception as e:
                print(f"[MUTA CLI Error] Falha ao processar mutação: {e}")
                return 1

        elif cmd == "rollback":
            if len(args) < 3:
                print("[MUTA CLI Error] Usage: python muta_vm.py rollback <hash>")
                return 1
            target_hash = args[2]
            try:
                estado = self.manager.reconstruct_state_at(target_hash)
                self.manager.current_head = target_hash
                self.manager.save_history({"head": target_hash, "count": self.manager.contador_passos})
                print("[MUTA SUCCESS] Viagem no tempo realizada.")
                print(f"Estado restaurado: {estado}")
            except Exception as e:
                print(f"[MUTA CLI Error] Aborted: {e}")
                return 1

        elif cmd == "verify":
            print("[MUTA AUDITORIA] Starting batch integrity verification...")
            sucesso, msg = self.manager.audit_entire_chain()
            if sucesso:
                print(f"[MUTA OK] {msg}")
            else:
                print(f"[MUTA CRITICAL] REJECTED.\n{msg}")
            return 0 if sucesso else 1

        else:
            self.print_help()
            return 1

    def print_help(self) -> None:
        print("MUTA Language CLI - Engine Core 4.4")
        print("Usage: python muta_vm.py <command> [arguments]")
        print("\nCommands:")
        print("  status            - Display current HEAD metadata.")
        print("  mutate '<json>'   - Commit atomic mutation in disk.")
        print("  rollback <hash>   - Rewind physical state to target hash.")
        print("  verify            - Validate cryptographic checksums against adulteration.")

    def status(self) -> None:
        """Display current HEAD and total steps."""
        print("[MUTA STATUS]")
        print(f"  Current HEAD: {self.manager.current_head}")
        print(f"  Total steps: {self.manager.contador_passos}")


def main() -> None:
    """Entry point when called as script."""
    if len(sys.argv) > 1:
        storage = VerifiedFilePatchStore("muta_live_storage")
        state_mgr = PersistentDeltaStateManager(storage)
        native_cli = MutaNativeCLI(storage, state_mgr)
        native_cli.execute_from_args(sys.argv)
        sys.exit(0)

    # Controlled simulation to emulate terminal behavior
    print("=================================================================")
    print("🛡️ MUTA CORE 4.4: VALIDATING SYS.ARGV + ANTI-ADULTERATION AUDIT")
    print("=================================================================")

    storage_test = VerifiedFilePatchStore("muta_sandbox_storage")
    mgr_test = PersistentDeltaStateManager(storage_test)
    cli_test = MutaNativeCLI(storage_test, mgr_test)

    # Step 1: Simulate terminal input 'python muta_vm.py mutate'
    print("\n[Step 1] Emulating terminal command: mutate")
    simulated_args_1 = ["muta_vm.py", "mutate", '{"dispositivo": "turbina_01", "rpm": 3200}']
    cli_test.execute_from_args(simulated_args_1)