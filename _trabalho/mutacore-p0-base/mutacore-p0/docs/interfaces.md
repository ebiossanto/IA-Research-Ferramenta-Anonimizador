# Interfaces principais

As interfaces executáveis encontram-se nos crates. A separação obrigatória é `propor != provar != executar`.

1. `Agent::propose` só produz `Action`.
2. `ObligationGenerator::generate` produz obrigação determinística.
3. `Synthesizer::synthesize` produz evidência candidata, nunca autorização.
4. `CertificateVerifier::verify` é o único produtor de `ProvenAction`.
5. `decide` converte qualquer resultado não provado em recuperação.
6. `CapabilityIssuer::issue` vincula decisão, estado, ciclo e expiração.
7. `EffectGateway::execute` é o único caminho público até a alteração do simulador.
