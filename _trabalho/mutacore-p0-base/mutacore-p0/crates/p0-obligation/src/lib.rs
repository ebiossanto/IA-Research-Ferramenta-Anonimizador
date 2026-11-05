#![forbid(unsafe_code)]
use p0_domain::{canonical_hash, Action, Hash32, Observation};
use p0_policy::VehiclePolicy;
use serde::{Deserialize, Serialize};
#[derive(Clone, Debug, Serialize, Deserialize)] pub struct Proposal { pub observation: Observation, pub action: Action, pub agent_id: Hash32 }
#[derive(Clone, Debug, Serialize, Deserialize)] pub struct Obligation { pub id: Hash32, pub state_hash: Hash32, pub action_hash: Hash32, pub policy_id: Hash32, pub model_id: Hash32, pub required_margin: f64 }
pub trait ObligationGenerator { fn generate(&self, proposal: &Proposal, policy: &VehiclePolicy) -> Obligation; }
pub struct P0ObligationGenerator { pub model_id: Hash32 }
impl ObligationGenerator for P0ObligationGenerator {
 fn generate(&self,p:&Proposal,policy:&VehiclePolicy)->Obligation {
  let state_hash=canonical_hash(&p.observation.estimated_state); let action_hash=canonical_hash(&p.action);
  let seed=(state_hash,action_hash,policy.id(),self.model_id);
  Obligation{id:canonical_hash(&seed),state_hash,action_hash,policy_id:policy.id(),model_id:self.model_id,required_margin:policy.safe_distance(&p.observation)}
 }
}
