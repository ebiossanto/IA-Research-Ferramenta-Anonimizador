#![forbid(unsafe_code)]
use p0_certificate::{Certificate,Counterexample}; use p0_obligation::Obligation; pub enum SynthesisResult{Candidate(Certificate),Counterexample(Counterexample),NoResult(String),Failure(String)} pub trait Synthesizer{fn synthesize(&mut self,o:&Obligation)->SynthesisResult;}
