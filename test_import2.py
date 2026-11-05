import importlib
import sys

# Force clean import
if 'muta_package' in sys.modules:
    del sys.modules['muta_package']
if 'muta_package.muta' in sys.modules:
    del sys.modules['muta_package.muta']

sys.path.insert(0, r'D:\Atrator compactador residual')

# Try step-by-step imports
from muta_package.muta.engine import VerifiedFilePatchStore, PersistentDeltaStateManager, SecurityError
print('engine import OK')

from muta_package.muta.crypto import MutaCryptoEngine, sign_payload, verify_signature
print('crypto import OK')

from muta_package.muta.audit import calculate_event_hash, load_events, validate
print('audit import OK')

from muta_package.muta.snapshots import reconstruct_state_at, get_current_head, take_snapshot
print('snapshots import OK')

from muta_package.muta.cli import MutaNativeCLI
print('cli import OK')

from muta_package.muta.rpc import MutaRPCServer, MutaRPCClient
print('rpc import OK')

print('All imports successful!')