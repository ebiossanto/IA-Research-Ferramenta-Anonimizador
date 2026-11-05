#![forbid(unsafe_code)]
use clap::{Parser,Subcommand};
#[derive(Parser)] struct Cli{#[command(subcommand)] command:Command}
#[derive(Subcommand)] enum Command{RunDemo,CheckArchitecture}
fn main(){match Cli::parse().command{Command::RunDemo=>println!("P0: demo será ligada ao runtime no próximo incremento"),Command::CheckArchitecture=>println!("Arquitetura carregada; execute cargo test --workspace")}}
