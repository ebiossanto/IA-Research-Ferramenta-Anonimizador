# Matriz de controles de segurança da MUTA

Use esta matriz durante revisão de código e aceite. Cada linha deve apontar para código, configuração, teste e evidência de execução.

| Ativo | Controle mínimo | Evidência esperada | Falha crítica |
|---|---|---|---|
| Policy controller | deny-by-default, versões imutáveis, aprovação separada | testes de decisão, hash/versionamento, logs | agente consegue alterar política ou erro libera ação |
| Logs | append-only, cadeia de hashes, redaction, retenção | teste de adulteração e inspeção de eventos | executor ou UI edita/remove eventos |
| Chaves | KMS/secret store, separação por finalidade, rotação | teste de rotação/revogação, permissões | chave em Git, imagem, frontend ou log |
| Snapshots | criptografia, integridade, imutabilidade, restauração | restore drill, manifesto, RPO/RTO | snapshot corrompido é restaurado ou último backup é apagado |
| Web UI | TLS, autenticação, RBAC, CSRF/CSP, rate limit | testes de autorização e segurança web | endpoint administrativo sem auth ou segredo no browser |
| Agente–sandbox | protocolo estruturado, capability curta, anti-replay | testes de token, schema, timeout, adulteração | shell livre, canal sem autenticação ou replay aceito |
| Sandbox | não-root, quotas, rede negada, rootfs read-only, seccomp/VM | testes de escape e acesso a host | acesso a host, Docker socket, credenciais ou metadata |
| Falhas | fail-closed para policy/audit/KMS/canal | testes de indisponibilidade e crash | sistema continua em modo inseguro silenciosamente |

## Escala de decisão

- **Bloqueador:** qualquer falha crítica ou controle ausente.
- **Alta prioridade:** risco explorável com impacto relevante; corrigir antes de beta.
- **Aceitável com plano:** limitação documentada, mitigação ativa, responsável e prazo.
- **Informativo:** melhoria sem impacto imediato no boundary de segurança.

## Evidência mínima

Para cada controle, guardar: comando executado, versão do código, ambiente, resultado, artefato/log sanitizado e data UTC. Não anexar chaves, tokens ou dados pessoais.
