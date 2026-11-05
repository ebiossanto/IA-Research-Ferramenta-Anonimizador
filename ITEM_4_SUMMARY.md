# MUTA Item 4 — Livro-Razão de Efeitos Colaterais

## Status: IMPLEMENTADO

### Código-fonte encontrado e organizado

O pacote `muta/` foi localizado e organizado em `D:\Atrator compactador residual\muta_package\muta\` com os seguintes módulos:

- `audit.py` - Sistema de auditoria de logs JSONL
- `crypto.py` - Motor criptográfico (assinaturas digitais)
- `engine.py` - Gerenciador de persistência de estado
- `snapshots.py` - Suporte a snapshots e poda
- `cli.py` - Interface de linha de comando
- `rpc.py` - Servidor/Cliente RPC via TCP
- `__init__.py` - Exportações do pacote

### Funcionalidades implementadas

| Capacidade | Descrição |
|---|---|
| **Hash-linkada chain** | Cada nó tem `parent_hash` → cadeia da HEAD ao Gênesis (estrutura Merkle-like) |
| **Efeitos colaterais (deltas)** | Parâmetro `delta` em `append_mutation()` registra cada efeito no livro-razão |
| **Livro-razão** | `audit_entire_chain()` valida integridade da cadeia completa; histórico imutável em disco |
| **Poda (prune)** | `frequencia_snapshot` (padrão 3) cria snapshots consolidados; `reconstruct_state_at()` recupera estado após poda |
| **Rollback** | Comando `rollback <hash>` rewind para qualquer ponto da cadeia |
| **Assinatura digital** | `MutaCryptoEngine` + `append_authenticated_mutation()` garante autoria e integridade |
| **Proveniência** | Cada nó traz `provenance: {agent, public_key, signature}` — responde "quem causou este efeito" |
| **Interface** | CLI (`mutate`, `rollback`, `verify`, `status`) e RPC remoto |

### Como usar

```python
from muta_package.muta import VerifiedFilePatchStore, PersistentDeltaStateManager, MutaCryptoEngine

# Inicializar store e manager
store = VerifiedFilePatchStore("muta_live_storage")
mgr = PersistentDeltaStateManager(store)

# Commitar uma mutação (efeito colateral)
delta = {"dispositivo": "turbina_01", "rpm": 3200}
new_hash = mgr.append_mutation(delta)
print(f"Nova HEAD: {new_hash}")

# Verificar integridade da cadeia
ok, msg = mgr.audit_entire_chain()
print(f"Chain valid: {ok}")

# Recuperar estado em qualquer ponto
state = mgr.reconstruct_state_at(new_hash)
print(f"Estado restaurado: {state}")

# Assinatura digital
pub, priv = MutaCryptoEngine.generate_keypair("agente_teste")
sig = MutaCryptoEngine.sign_payload({"acao": "abrir"}, priv)
valid = MutaCryptoEngine.verify_signature({"acao": "abrir"}, sig, pub)
```

### ZIP atualizado

`atrator-compactador-v0.3.zip` — 138 arquivos, 15,9 MB
inclui STATUS.md (atualizado) e o pacote `muta_package/`.