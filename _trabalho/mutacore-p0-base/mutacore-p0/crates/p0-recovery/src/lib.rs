#![forbid(unsafe_code)]
use p0_domain::{Acceleration, Action, Observation}; use p0_policy::VehiclePolicy;
#[derive(Clone,Debug)] pub enum RecoveryReason { Refuted, Unknown, Invalid, Timeout }
#[derive(Clone,Debug)] pub struct RecoveryAction { action: Action, pub reason: RecoveryReason }
impl RecoveryAction { pub fn action(&self)->&Action{&self.action} }
pub trait RecoveryController { fn recovery_action(&self,o:&Observation,p:&VehiclePolicy,r:RecoveryReason)->RecoveryAction; }
pub struct BrakeController;
impl RecoveryController for BrakeController { fn recovery_action(&self,_:&Observation,p:&VehiclePolicy,r:RecoveryReason)->RecoveryAction { RecoveryAction{action:Action::new(Acceleration::new(-p.max_braking).expect("política validada")),reason:r} } }
