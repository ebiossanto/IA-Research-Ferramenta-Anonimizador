#![forbid(unsafe_code)]
//! Orquestrador do ciclo: observar, propor, obrigar, sintetizar, verificar, decidir, executar e auditar.
pub enum RuntimePhase { Boot, Ready, Observe, Propose, BuildObligation, Synthesize, Verify, Execute, Recover, Fault, Audit }
