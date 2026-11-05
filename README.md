# IA Research Ferramenta Anonimizador

## MUTA - Livro-Razão de Efeitos Colaterais

Esta ferramenta implementa o **Item 4** do roadmap MUTA: um livro-razão de efeitos colaterais com integridade criptográfica garantida.

### Visão Geral

A ferramenta MUTA fornece um sistema de persistência de estados imutáveis com as seguintes capacidades:

1. **Registro de efeitos colaterais** - Cada ação ou mutação do agente de IA é registrada como um "delta" no livro-razão
2. **Cadeia hash-linkada** - Cada entrada está criptograficamente vinculada à anterior (estrutura Merkle-like)
3. **Integridade verificável** - É detectada qualquer tentativa de alterar registros passados
4. **Rollback controlado** - É possível voltar a qualquer estado anterior da história
5. **Assinatura digital** - Cada efeito pode ser assinado por um agente específico
6. **Snapshots** - Pontos de checkpoint para recuperação rápida de estado

### Estrutura do Repositório

```
IA-Research-Ferramenta-Anonimizador/
├── muta_package/
│   ├── __init__.py       # Exportações principais do pacote MUTA
│   ├── audit.py         # Sistema de auditoria de logs JSONL
│   ├── crypto.py        # Motor criptográfico (assinaturas digitais)
│   ├── engine.py        # Motor de persistência de estado
│   ├── snapshots.py     # Suporte a snapshots e poda
│   ├── cli.py           # Interface de linha de comando
│   └── rpc.py           # Servidor/Cliente RPC via TCP
├── atrator-compactador-v0.3.zip
│   # Zip com o projeto completo v0.3
├── codigo muta1,4.md
├── mutacripto.md
└── ITEM_4_SUMMARY.md
```

### Como Usar

#### Instalação

```python
# Instalar como pacote
pip install muta-package

# Ou usar diretamente da fonte
import sys
sys.path.insert(0, 'caminho/para/muta_package')
from muta_package.muta import *
```

#### Básico - Registrando Mutações

```python
from muta_package.muta import VerifiedFilePatchStore, PersistentDeltaStateManager

# Inicializar store (persistência em disco)
store = VerifiedFilePatchStore("muta_storage")

# Inicializar manager (lógica de estado)
mgr = PersistentDeltaStateManager(store, frequencia_snapshot=3)

# Registrar mutações (efeitos colaterais)
delta1 = {"dispositivo": "turbina_01", "rpm": 3200}
hash1 = mgr.append_mutation(delta1)
print(f"1ª mutação: HEAD = {hash1[:16]}...")

delta2 = {"dispositivo": "turbina_02", "rpm": 4100}
hash2 = mgr.append_mutation(delta2)
print(f"2ª mutação: HEAD = {hash2[:16]}...")

# A cada 3 mutações, é criado um snapshot consolidado

# Auditar integridade da cadeia
ok, msg = mgr.audit_entire_chain()
print(f"Integridade: {ok} - {msg}")
```

#### Assinatura Digital

```python
from muta_package.muta import MutaCryptoEngine

# Gerar par de chaves para um agente
pub_key, priv_key = MutaCryptoEngine.generate_keypair("agente_teste")

# Signar um payload (o agente assina seus próprios efeitos)
payload = {"acao": "abrir_valvula", "pressao": 45}
assinatura = MutaCryptoEngine.sign_payload(payload, priv_key)

# Verificar a assinatura (qualquer um pode verificar)
valido = MutaCryptoEngine.verify_signature(payload, assinatura, pub_key)
print(f"Assinatura válida: {valido}")
```

#### CLI (Linha de Comando)

```
# Status atual
python muta_vm.py status

# Mutar (registrar um efeito)
python muta_vm.py mutate '{"dispositivo": "turbina_01", "rpm": 3200}'

# Rollback para um hash específico
python muta_vm.py rollback <hash>

# Verificar integridade da cadeia
python muta_vm.py verify
```

### Citação (How to Cite)

Se usar esta ferramenta em trabalhos acadêmicos ou projetos, cite da seguinte forma:

```
SOARES, Euzébio. MUTA: Livro-Razão de Efeitos Colaterais para Sistemas de IA. 
Versão 4.4. 2026. Disponível em: https://github.com/ebiossanto/IA-Research-Ferramenta-Anonimizador
```

### Licença

MIT License - Livre para uso, modificação e distribuição com atribuição adequada.

### Contato

Para dúvidas, contribuir ou discutir:
- Issues: https://github.com/ebiossanto/IA-Research-Ferramenta-Anonimizador/issues
- Email: euambiente@gmail.com