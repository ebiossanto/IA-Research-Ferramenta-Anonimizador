#![forbid(unsafe_code)]
use p0_decision::Decision; use p0_domain::{canonical_hash,Action,Cycle,Hash32,LogicalTime,State};
pub struct EffectCapability { action:Action, state_hash:Hash32, cycle:Cycle, expires:LogicalTime }
pub struct ConsumedCapability { pub action:Action }
pub trait CapabilityIssuer { fn issue(&self,d:Decision,s:&State,expires:LogicalTime)->EffectCapability; }
pub struct P0Issuer;
impl CapabilityIssuer for P0Issuer { fn issue(&self,d:Decision,s:&State,expires:LogicalTime)->EffectCapability { let action=match d { Decision::Execute(x)=>x.action().clone(), Decision::Recover(x)=>x.action().clone(), Decision::EnterFault(_)=>panic!("fault não emite capability")}; EffectCapability{action,state_hash:canonical_hash(s),cycle:s.cycle,expires} } }
impl EffectCapability { pub fn consume(self,s:&State,now:LogicalTime)->Result<ConsumedCapability,&'static str>{if canonical_hash(s)!=self.state_hash||s.cycle!=self.cycle{return Err("estado mudou")} if now.0>self.expires.0{return Err("capability expirou")} Ok(ConsumedCapability{action:self.action})} }
