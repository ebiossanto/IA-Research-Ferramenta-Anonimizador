#![forbid(unsafe_code)]
use p0_domain::{Action,Observation}; pub trait Agent{fn propose(&mut self,o:&Observation)->Action;}
