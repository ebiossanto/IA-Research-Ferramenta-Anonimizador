# Manual simples para acompanhar a construção da MUTA

## 1. O que a próxima IA deve fazer

A próxima IA deve transformar a ideia da MUTA em um programa que permita a um robô de Inteligência Artificial executar tarefas com limites claros. O robô não deve falar diretamente com o computador. Ele deve pedir uma ação, a MUTA deve verificar se a ação é permitida, executar a tarefa em um ambiente isolado e registrar o resultado.

O objetivo não é prometer segurança absoluta. O objetivo é reduzir riscos, bloquear ações perigosas, registrar o que aconteceu e facilitar a recuperação de um estado seguro.

## 2. O que já existe

Já foram preparados quatro elementos importantes:

| Elemento | Situação atual |
|---|---|
| Manual técnico para a IA programadora | Criado e validado. |
| Verificador de logs | Criado e testado com um log correto e outro adulterado. |
| Diagrama de arquitetura | Criado em formato editável e PNG. |
| Plano de testes de escape | Criado com 22 testes de segurança. |

Esses materiais ajudam a construir o produto, mas não significam que todos os componentes da MUTA já estejam funcionando. A próxima IA precisa verificar o código real antes de afirmar que algo está pronto.

## 3. Como saber em que etapa estamos

Acompanhe o projeto nesta ordem:

| Etapa | Pergunta simples | O que deve ser mostrado |
|---|---|---|
| 1. Diagnóstico | A IA encontrou e entendeu o código existente? | Lista de arquivos, funcionamento atual e problemas. |
| 2. Sandbox | O robô está realmente isolado? | Demonstração de que não acessa host, segredos ou Docker socket. |
| 3. Regras | A MUTA bloqueia ações proibidas? | Exemplos de ações permitidas e bloqueadas. |
| 4. Logs | É possível provar o que aconteceu? | Log estruturado e verificação de integridade. |
| 5. Chaves | Os segredos estão protegidos? | Onde ficam, como são rotacionados e quem pode usá-los. |
| 6. Snapshots | É possível voltar a um estado seguro? | Teste de restauração bem-sucedido. |
| 7. Interface | O painel é seguro? | Login, permissões e ausência de comandos diretos. |
| 8. Testes | A proteção foi atacada de forma controlada? | Relatório dos testes de escape e falhas corrigidas. |
| 9. Eficiência | O programa funciona sem desperdiçar recursos? | Tempos, limites, concorrência e custo por execução. |
| 10. Prontidão | Está pronto para uso? | Decisão: desenvolvimento, beta ou produção. |

## 4. Perguntas para fazer à próxima IA

Use perguntas curtas e peça respostas com evidências:

1. **O que você encontrou no código atual?** Peça os nomes dos arquivos e uma explicação simples.
2. **O que já funciona de verdade?** Peça um comando de teste reproduzível.
3. **O que ainda é simulação?** Peça uma lista clara.
4. **A sandbox é real?** Pergunte qual tecnologia faz o isolamento e quais testes provaram isso.
5. **O que acontece quando a política falha?** A resposta correta deve ser “a ação é bloqueada”.
6. **Um agente consegue apagar o log?** Peça um teste de tentativa e verificação.
7. **Onde ficam as chaves?** Nunca aceite chaves gravadas no código, no Git ou na interface.
8. **O rollback desfaz o quê?** A IA deve explicar que efeitos externos, como mensagens ou chamadas de API, podem não ser desfeitos.
9. **Quais testes de escape passaram?** Peça a tabela de resultados, não apenas a frase “está seguro”.
10. **O que falta para produção?** Peça riscos residuais e um próximo passo priorizado.

## 5. Como interpretar as respostas

Considere uma tarefa **concluída** somente quando houver código, teste e evidência. Uma explicação ou um gráfico sozinho não comprova segurança.

Considere uma tarefa **parcial** quando existir código, mas faltar teste, autenticação, isolamento, documentação ou tratamento de falhas.

Considere uma tarefa **bloqueada** quando a IA disser que não tem mecanismo de isolamento, credencial necessária, decisão de arquitetura ou ambiente seguro para testar. Nesse caso, não peça para ela ignorar o problema.

Considere o produto **não pronto para produção** se a sandbox for apenas uma pasta ou subprocesso, se o agente puder alterar a política, se os logs puderem ser apagados sem detecção, se chaves aparecerem no código, se snapshots não forem validados ou se testes importantes estiverem inconclusivos.

## 6. Relatório que a IA deve entregar ao final de cada etapa

Peça sempre um relatório com este formato:

```text
Etapa:
Objetivo:
O que foi alterado:
Arquivos alterados:
O que funciona:
Comandos de teste:
Resultado dos testes:
O que ainda não funciona:
Riscos restantes:
Próximo passo recomendado:
Status: desenvolvimento / beta / não pronto para produção
```

Não aceite “tudo certo” sem comandos, resultados e riscos restantes.

## 7. Sinais de alerta

Interrompa a tarefa e peça explicação se a IA disser que a MUTA é “100% segura”, remover testes para fazer o programa passar, desativar logs, usar `shell=True` ou concatenar comandos, executar como administrador sem necessidade, montar o Docker socket, colocar chaves no código, liberar a rede por padrão, ignorar erro do policy engine ou chamar uma pasta de sandbox.

Também peça esclarecimento se o painel mostrar “seguro” enquanto os testes de escape ainda não foram executados. O painel deve mostrar a diferença entre **não verificado**, **bloqueado**, **controlado** e **inconclusivo**.

## 8. Ordem recomendada para o projeto

A ordem mais segura é: primeiro entender o código; depois construir o isolamento; em seguida implementar regras e autorização; depois logs; então chaves e snapshots; depois interface; por fim otimização, recursos avançados e aparência visual.

Não comece pelos gráficos. Um painel bonito não protege arquivos. Primeiro devem funcionar as barreiras, os registros e os testes.

## 9. Resultado esperado

Ao final, a MUTA deve conseguir receber uma ação estruturada, decidir com uma política versionada, executar em sandbox real, impedir acesso indevido ao host, registrar a execução com integridade verificável, impedir replay e restaurar um snapshot validado. A documentação deve informar claramente o que a MUTA protege e o que ela não consegue desfazer.

## Referências do projeto

- [Skill técnica para a próxima IA](../skills/muta-secure-builder/SKILL.md)
- [Plano de testes de escape](SECURITY_TEST_PLAN.md)
- [Verificador de integridade dos logs](verify_muta_audit_log.py)
- [Diagrama editável](muta-secure-architecture.mmd)

