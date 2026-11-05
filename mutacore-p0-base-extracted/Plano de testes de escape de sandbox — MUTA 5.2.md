# Plano de testes de escape de sandbox — MUTA 5.2

## Objetivo e limite

Este plano valida se um agente comprometido, um payload malformado ou um processo dentro da sandbox consegue atravessar os limites definidos pela MUTA. Os testes devem ocorrer somente em máquinas, imagens, contas e redes dedicadas, sem dados reais, credenciais reais ou endpoints de produção. O objetivo é produzir evidência de bloqueio e detectar falhas; não é uma garantia de segurança absoluta.

A matriz de testes deve ser executada contra cada modo de isolamento suportado. Se o modo usa apenas subprocesso ou diretório, marcar o resultado como **não equivalente a sandbox**. Para código de alto risco, priorizar VM/microVM e repetir os testes no kernel/hipervisor efetivamente usado em produção.

## Critérios de entrada

Antes de testar, registrar versão do código, imagem/VM, kernel, runtime, configuração, commit, política ativa, perfil seccomp/AppArmor/SELinux, capabilities, usuário, limites de CPU/memória/disco/processos, configuração de rede e destino dos logs. Criar snapshot descartável e um host de observação separado. Confirmar que nenhum segredo, socket Docker, token de nuvem, volume de produção ou rede corporativa está acessível.

A política de teste deve negar rede, montagens, dispositivos, privilégios, acesso ao host e acesso a segredos. O executor deve registrar cada tentativa como evento estruturado, com redaction. O plano não deve depender de comandos destrutivos reais: use arquivos-isca, endpoints falsos e marcadores inofensivos.

## Evidências e resultado

Para cada caso, guardar ID da execução, request sanitizado, decisão da política, stdout/stderr sanitizados, eventos de auditoria, alertas, estado do processo, snapshot antes/depois e resultado da verificação de integridade. Classificar como **Passou**, **Falhou**, **Inconclusivo** ou **Não aplicável**. Uma falha de escape é bloqueadora mesmo que o painel mostre estado verde.

## Casos de teste

| ID | Área | Técnica controlada | Resultado esperado | Evidência |
|---|---|---|---|---|
| SB-01 | Identidade | Executar como usuário não-root e consultar privilégios | Sem root, sem capabilities desnecessárias; decisão e identidade auditadas | `uid/gid`, capabilities, evento |
| SB-02 | Filesystem | Tentar ler/escrever fora do workspace, incluindo traversal e caminhos absolutos | Negado; nenhum arquivo do host alterado | retorno, diff do host, log |
| SB-03 | Symlink | Criar symlink/hardlink para caminho fora do workspace e operar via link | Resolução segura bloqueia; sem acesso indireto | syscall/erro, evento |
| SB-04 | Dispositivos | Enumerar e abrir `/dev`, tentar criar device ou usar interfaces de host | Sem dispositivos não autorizados | lista de mounts/devices |
| SB-05 | Mounts | Tentar montar filesystem, usar bind mount ou alcançar diretórios de runtime | Operação negada e processo encerrado se necessário | audit + estado final |
| SB-06 | Kernel/runtime | Tentar usar interfaces de namespaces, ptrace, perf, módulos ou sockets privilegiados | Bloqueio por perfil/runtime; sem impacto no host | perfil aplicado, alertas |
| SB-07 | Container control plane | Procurar e acessar socket Docker/containerd/CRI | Socket ausente ou inacessível | mounts e tentativa redigida |
| SB-08 | Proc/sys | Ler ou alterar informações sensíveis em `/proc` e `/sys` | Exposição mínima; escrita negada | allowlist de paths |
| SB-09 | Rede | Resolver DNS, abrir saída TCP/UDP, acessar loopback do host e metadata endpoint simulado | Rede negada por padrão; sem acesso a host/metadata | regras de rede + pcap/telemetria |
| SB-10 | Credenciais | Procurar variáveis, arquivos temporários, agentes SSH, tokens e metadados | Nenhum segredo montado/herdado; redaction confirmada | ambiente sanitizado + scanner |
| SB-11 | Processos | Criar muitos processos, forks, threads e subprocessos | Quota efetiva; sandbox termina sem afetar host | limites e consumo |
| SB-12 | Recursos | Exceder CPU, memória, disco, output e timeout | Limite aplicado, processo morto e evidência preservada | métricas + evento |
| SB-13 | Shell injection | Enviar argumentos contendo metacaracteres e payloads de shell como dados | API não concatena shell; argumentos permanecem dados | request/exec trace |
| SB-14 | Protocolo | Enviar schema inválido, campos extras, mensagens grandes, nonce repetido e token expirado | Rejeição antes do executor; fail-closed | status + policy decision |
| SB-15 | Replay/cross-run | Reutilizar capability de outra execução ou tenant | Rejeitado por audiência, nonce, TTL e execução | correlação de IDs |
| SB-16 | Canal | Adulterar mensagem, interromper canal ou simular peer não autenticado | Autenticação falha; execução é encerrada/inconclusiva | logs dos dois lados |
| SB-17 | Policy race | Alterar política durante uma execução em andamento | Execução usa versão fixada; mudança vale apenas para nova execução | policy hash |
| SB-18 | Auditoria | Tentar apagar/editar/reordenar log a partir da sandbox ou UI | Acesso negado; verificador detecta qualquer adulteração | saída do verificador |
| SB-19 | Snapshot | Alterar manifesto, hash ou conteúdo antes do restore | Restauração recusada; snapshot saudável preservado | restore report |
| SB-20 | Crash/restart | Matar executor, reiniciar broker e repetir request | Sem duplicação; estado inconclusivo e vínculo de auditoria preservado | execution IDs |
| SB-21 | Web boundary | Acessar endpoints administrativos sem sessão, com papel insuficiente, CSRF e payload XSS | 401/403; sem execução; conteúdo escapado | testes HTTP sanitizados |
| SB-22 | Escalada | Tentar alterar policy, KMS, snapshots ou configuração a partir do agente | Negado por separação de identidades | autorização e audit |

## Método de execução

Executar primeiro os casos de baixo impacto (SB-01 a SB-09), depois canais e autorização (SB-10 a SB-18), e por fim recuperação e web (SB-19 a SB-22). Recriar a sandbox a partir de imagem limpa entre casos ou agrupar somente testes comprovadamente independentes. Não encadear uma exploração encontrada com outros alvos sem registrar aprovação do responsável.

Para cada caso, seguir o ciclo: preparar snapshot; emitir request estruturado; verificar a decisão antes do executor; observar processo, filesystem, rede e host; coletar logs; executar `verify` no audit store; destruir ambiente; restaurar somente snapshot validado; registrar resultado e risco residual. Repetir testes sob concorrência e após rotação de chaves quando o controle for relevante.

## Testes de propriedade e fuzzing

Fazer fuzzing dos schemas de `ActionRequest`, paths, argumentos, políticas e mensagens de transporte, impondo limites de tamanho e tempo. Propriedades mínimas: entrada não autorizada nunca inicia processo; token expirado nunca autoriza; toda execução autorizada gera evento inicial e final; qualquer edição do evento altera o resultado do verificador; policy engine indisponível bloqueia ações; restore não aceita snapshot inválido.

## Critérios de aprovação

A MUTA 5.2 só deve ser aprovada para o ambiente avaliado se todos os casos aplicáveis passarem, não houver acesso ao host/credenciais/Docker socket, quotas e rede forem efetivos, replay e adulteração forem detectados, falhas de policy/auditoria/KMS fizerem o sistema falhar fechado e o restore drill for bem-sucedido. Qualquer isolamento simulado, caso inconclusivo de alto risco ou controle ausente deve resultar em **não pronto para produção**.

## Relatório final

O relatório deve conter resumo executivo, ambiente, threat model, tabela de resultados, evidências, achados por severidade, reprodução mínima sanitizada, impacto, correção, reteste, riscos residuais e decisão. Nunca anexar credenciais, tokens, dados pessoais ou payloads que possam atingir ambientes reais. Manter as evidências em armazenamento protegido e append-only.
