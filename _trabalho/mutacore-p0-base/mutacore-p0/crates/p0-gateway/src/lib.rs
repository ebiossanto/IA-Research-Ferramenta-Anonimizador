#![forbid(unsafe_code)]
use p0_capability::{CapabilityIssuer,P0Issuer}; use p0_decision::Decision; use p0_domain::LogicalTime; use p0_simulator::{EffectReceipt,Simulator};
pub trait EffectGateway { fn execute(&mut self,d:Decision,now:LogicalTime,expires:LogicalTime)->Result<EffectReceipt,&'static str>; }
pub struct P0Gateway { simulator:Simulator, issuer:P0Issuer }
impl P0Gateway { pub fn new(simulator:Simulator)->Self{Self{simulator,issuer:P0Issuer}} pub fn simulator(&self)->&Simulator{&self.simulator} }
impl EffectGateway for P0Gateway { fn execute(&mut self,d:Decision,now:LogicalTime,expires:LogicalTime)->Result<EffectReceipt,&'static str>{let cap=self.issuer.issue(d,self.simulator.state(),expires); let consumed=cap.consume(self.simulator.state(),now)?; Ok(self.simulator.apply_authorized(consumed))} }
