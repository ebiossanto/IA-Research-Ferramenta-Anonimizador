#![forbid(unsafe_code)]
use p0_domain::{Cycle, Hash32, LogicalTime, Nonce};
use serde::{Deserialize, Serialize};
#[derive(Clone, Debug, Serialize, Deserialize)] pub enum ProofArtifact { Interval { minimum_margin: f64 }, Unsupported }
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct Certificate {
 pub policy_id: Hash32, pub model_id: Hash32, pub obligation_id: Hash32,
 pub state_hash: Hash32, pub action_hash: Hash32, pub proof: ProofArtifact,
 pub issued_at: LogicalTime, pub valid_until: LogicalTime, pub cycle: Cycle, pub nonce: Nonce,
}
#[derive(Clone, Debug)] pub struct Counterexample { pub reason: String }
