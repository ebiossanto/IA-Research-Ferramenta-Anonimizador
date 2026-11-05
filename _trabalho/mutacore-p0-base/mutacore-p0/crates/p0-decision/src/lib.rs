#![forbid(unsafe_code)]
use p0_domain::Observation; use p0_policy::VehiclePolicy; use p0_recovery::{RecoveryAction,RecoveryController,RecoveryReason}; use p0_verifier::{ProvenAction,Verdict};
#[derive(Debug)] pub enum Decision { Execute(ProvenAction), Recover(RecoveryAction), EnterFault(String) }
pub fn decide(v:Verdict,o:&Observation,p:&VehiclePolicy,r:&impl RecoveryController)->Decision { match v { Verdict::Proven(x)=>Decision::Execute(x), Verdict::Refuted(_)=>Decision::Recover(r.recovery_action(o,p,RecoveryReason::Refuted)), Verdict::Unknown(_)=>Decision::Recover(r.recovery_action(o,p,RecoveryReason::Unknown)), Verdict::Invalid(_)=>Decision::Recover(r.recovery_action(o,p,RecoveryReason::Invalid)) } }
