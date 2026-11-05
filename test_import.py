import sys
sys.path.insert(0, r'D:\Atrator compactador residual')

from muta_package.muta import (
    VerifiedFilePatchStore, PersistentDeltaStateManager, SecurityError,
    MutaCryptoEngine, MutaNativeCLI, append_mutation, reconstruct_state_at,
    audit_entire_chain, generate_keypair, sign_payload, verify_signature
)
print('All imports successful')

# Test basic functionality
store = VerifiedFilePatchStore('muta_test_storage')
mgr = PersistentDeltaStateManager(store)

# Test mutate
delta = {'dispositivo': 'turbina_01', 'rpm': 3200}
new_hash = mgr.append_mutation(delta)
print(f'After first mutate: HEAD = {new_hash}')

# Test second mutate
delta2 = {'dispositivo': 'turbina_02', 'rpm': 4100}
new_hash2 = mgr.append_mutation(delta2)
print(f'After second mutate: HEAD = {new_hash2}')

# Test third mutate (should trigger snapshot at freq 3)
delta3 = {'dispositivo': 'turbina_03', 'rpm': 2800}
new_hash3 = mgr.append_mutation(delta3)
print(f'After third mutate: HEAD = {new_hash3}')

# Test verify
ok, msg = mgr.audit_entire_chain()
print(f'Chain audit: {ok} - {msg}')

# Test reconstruct state
state = mgr.reconstruct_state_at(new_hash)
print(f'Reconstructed state at new_hash: {state}')

# Test keypair
pub, priv = generate_keypair('test_agent')
print(f'Keypair generated - pub: {pub[:16]}..., priv: {priv[:16]}...')

# Test sign/verify
signature = sign_payload({'test': 'data'}, priv)
valid = verify_signature({'test': 'data'}, signature, pub)
print(f'Sign/verify valid: {valid}')