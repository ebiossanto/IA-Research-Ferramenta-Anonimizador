#![forbid(unsafe_code)]
use p0_domain::{Hash32,LogicalTime}; use serde::{Deserialize,Serialize}; #[derive(Clone,Debug,Serialize,Deserialize)] pub struct AuditRecord{pub sequence:u64,pub previous_hash:Hash32,pub logical_time:LogicalTime,pub event:String,pub record_hash:Hash32} pub trait Ledger{fn append(&mut self,event:String,time:LogicalTime);}
