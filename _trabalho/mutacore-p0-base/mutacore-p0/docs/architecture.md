# Arquitetura P0

## Fluxo

`Observation -> Proposal -> Obligation -> CandidateEvidence -> Verdict -> Decision -> Capability -> Gateway -> Receipt`

## Invariantes arquiteturais

- Nenhum efeito protegido aceita `Action` diretamente.
- `ProvenAction` possui campos privados.
- Uma capability é consumida por valor e não implementa `Clone`.
- `Unknown`, `Refuted` e `Invalid` conduzem a recuperação.
- O estado é revalidado ao consumir a capability.
- Todos os crates proíbem `unsafe`.
