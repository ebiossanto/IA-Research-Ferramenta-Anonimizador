#![forbid(unsafe_code)]
use p0_domain::{canonical_hash, Action, Hash32, Observation, State};
use serde::{Deserialize, Serialize};

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct VehiclePolicy {
    pub max_velocity: f64, pub max_acceleration: f64, pub max_braking: f64,
    pub min_guaranteed_braking: f64, pub reaction_time_s: f64,
    pub cycle_time_s: f64, pub minimum_separation: f64, pub discretization_margin: f64,
    pub proof_budget_ns: u64,
}
impl VehiclePolicy {
    pub fn id(&self) -> Hash32 { canonical_hash(self) }
    pub fn validate(&self) -> Result<(), &'static str> {
        if self.min_guaranteed_braking <= 0.0 { return Err("min_guaranteed_braking deve ser positivo"); }
        if self.cycle_time_s <= 0.0 { return Err("cycle_time_s deve ser positivo"); }
        Ok(())
    }
    pub fn safe_distance(&self, o: &Observation) -> f64 {
        let s=&o.estimated_state;
        let rel=(s.vehicle_velocity.get()-s.obstacle_velocity.get()).max(0.0)+2.0*o.uncertainty.velocity_error;
        let margin=self.minimum_separation+self.discretization_margin+2.0*o.uncertainty.position_error;
        rel*self.reaction_time_s + rel*rel/(2.0*self.min_guaranteed_braking)+margin
    }
    pub fn invariant(&self, s: &State) -> bool {
        let d=s.obstacle_position.get()-s.vehicle_position.get();
        s.vehicle_velocity.get() >= 0.0 && s.vehicle_velocity.get() <= self.max_velocity && d >= self.minimum_separation
    }
    pub fn action_in_bounds(&self, a: &Action) -> bool { let x=a.acceleration().get(); x <= self.max_acceleration && x >= -self.max_braking }
    pub fn recoverable(&self, o: &Observation) -> bool {
        let d=o.estimated_state.obstacle_position.get()-o.estimated_state.vehicle_position.get();
        d >= self.safe_distance(o)
    }
}
