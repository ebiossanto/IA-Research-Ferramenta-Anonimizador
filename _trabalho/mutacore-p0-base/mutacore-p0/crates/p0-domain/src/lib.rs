#![forbid(unsafe_code)]
use serde::{Deserialize, Serialize};
use sha2::{Digest, Sha256};
use thiserror::Error;

#[derive(Debug, Error)]
pub enum DomainError {
    #[error("valor não finito em {0}")]
    NonFinite(&'static str),
    #[error("valor fora do domínio em {0}")]
    OutOfRange(&'static str),
}

macro_rules! finite_unit {
    ($name:ident) => {
        #[derive(Clone, Copy, Debug, PartialEq, PartialOrd, Serialize, Deserialize)]
        pub struct $name(f64);
        impl $name {
            pub fn new(value: f64) -> Result<Self, DomainError> {
                if value.is_finite() { Ok(Self(value)) } else { Err(DomainError::NonFinite(stringify!($name))) }
            }
            pub fn get(self) -> f64 { self.0 }
        }
    };
}
finite_unit!(Position);
finite_unit!(Velocity);
finite_unit!(Acceleration);

#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize, Deserialize)] pub struct LogicalTime(pub u64);
#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize, Deserialize)] pub struct Cycle(pub u64);
#[derive(Clone, Copy, Debug, PartialEq, Eq, Hash, Serialize, Deserialize)] pub struct Nonce(pub u128);
#[derive(Clone, Copy, Debug, PartialEq, Eq, Serialize, Deserialize)] pub enum Mode { Advanced, Recovery, Stopped, Fault }

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct State {
    pub vehicle_position: Position,
    pub vehicle_velocity: Velocity,
    pub obstacle_position: Position,
    pub obstacle_velocity: Velocity,
    pub time: LogicalTime,
    pub cycle: Cycle,
    pub mode: Mode,
}

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct ObservationBounds { pub position_error: f64, pub velocity_error: f64, pub actuation_error: f64 }

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct Observation { pub estimated_state: State, pub uncertainty: ObservationBounds, pub observed_at: LogicalTime }

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub struct Action { acceleration: Acceleration }
impl Action { pub fn new(acceleration: Acceleration) -> Self { Self { acceleration } } pub fn acceleration(&self) -> Acceleration { self.acceleration } }

pub type Hash32 = [u8; 32];
pub fn canonical_hash<T: Serialize>(value: &T) -> Hash32 {
    let bytes = serde_json::to_vec(value).expect("tipos internos devem serializar");
    Sha256::digest(bytes).into()
}
