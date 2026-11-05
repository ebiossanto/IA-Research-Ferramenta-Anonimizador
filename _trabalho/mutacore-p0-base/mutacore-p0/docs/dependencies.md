# Diagrama de dependências

```mermaid
graph TD
  domain[p0-domain]
  policy[p0-policy] --> domain
  obligation[p0-obligation] --> domain
  obligation --> policy
  certificate[p0-certificate] --> domain
  verifier[p0-verifier] --> domain
  verifier --> policy
  verifier --> obligation
  verifier --> certificate
  recovery[p0-recovery] --> domain
  recovery --> policy
  decision[p0-decision] --> verifier
  decision --> recovery
  capability[p0-capability] --> decision
  capability --> domain
  gateway[p0-gateway] --> capability
  gateway --> decision
  gateway --> simulator[p0-simulator]
  simulator --> domain
  observer[p0-observer] --> domain
  agent[p0-agent] --> domain
  synthesizer[p0-synthesizer] --> obligation
  synthesizer --> certificate
  runtime[p0-runtime] --> agent
  runtime --> observer
  runtime --> obligation
  runtime --> synthesizer
  runtime --> verifier
  runtime --> decision
  runtime --> gateway
  runtime --> ledger[p0-ledger]
  cli[p0-cli] --> runtime
```

## Dependências proibidas

- `p0-agent -> p0-gateway`
- `p0-agent -> p0-capability`
- `p0-synthesizer -> p0-gateway`
- `p0-ledger -> p0-decision`
- `p0-cli -> p0-simulator`
