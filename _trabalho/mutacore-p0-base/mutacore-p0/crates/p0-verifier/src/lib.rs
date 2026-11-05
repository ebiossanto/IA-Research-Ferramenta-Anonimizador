#![forbid(unsafe_code)]
use p0_certificate::{Certificate, Counterexample, ProofArtifact};
use p0_domain::{Action, Hash32, LogicalTime, Nonce};
use p0_obligation::Obligation;
use p0_policy::VehiclePolicy;
use std::collections::HashSet;
use thiserror::Error;
#[derive(Debug,Error)] pub enum VerificationError { #[error("contexto incompatível")] Context, #[error("certificado expirado")] Expired, #[error("nonce reutilizado")] Replay, #[error("prova malformada")] Malformed }
#[derive(Debug)] pub struct Uncertainty { pub reason: String }
#[derive(Debug)] pub enum Verdict { Proven(ProvenAction), Refuted(Counterexample), Unknown(Uncertainty), Invalid(VerificationError) }
#[derive(Debug)] pub struct ProvenAction { action: Action, certificate_hash: Hash32, nonce: Nonce }
impl ProvenAction { pub fn action(&self)->&Action{&self.action} pub fn certificate_hash(&self)->Hash32{self.certificate_hash} pub fn nonce(&self)->Nonce{self.nonce} }
pub trait CertificateVerifier { fn verify(&mut self, c:&Certificate,o:&Obligation,a:&Action,p:&VehiclePolicy,now:LogicalTime)->Verdict; }
#[derive(Default)] pub struct P0Verifier { used: HashSet<Nonce> }
impl CertificateVerifier for P0Verifier {
 fn verify(&mut self,c:&Certificate,o:&Obligation,a:&Action,p:&VehiclePolicy,now:LogicalTime)->Verdict{
  if c.policy_id!=p.id()||c.model_id!=o.model_id||c.obligation_id!=o.id||c.state_hash!=o.state_hash||c.action_hash!=o.action_hash{return Verdict::Invalid(VerificationError::Context)}
  if now.0>c.valid_until.0{return Verdict::Invalid(VerificationError::Expired)}
  if self.used.contains(&c.nonce){return Verdict::Invalid(VerificationError::Replay)}
  match c.proof { ProofArtifact::Interval{minimum_margin} if minimum_margin>=o.required_margin => {self.used.insert(c.nonce); Verdict::Proven(ProvenAction{action:a.clone(),certificate_hash:p0_domain::canonical_hash(c),nonce:c.nonce})}, ProofArtifact::Interval{minimum_margin} => Verdict::Refuted(Counterexample{reason:format!("margem {minimum_margin} inferior à requerida")}), ProofArtifact::Unsupported => Verdict::Unknown(Uncertainty{reason:"artefato não suportado".into()}) }
 }
}
