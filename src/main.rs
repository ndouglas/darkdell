use anyhow::Error as AnyError;
use darkdell::prelude::*;

fn main() -> Result<(), AnyError> {
  let _settings = SettingsLoader::load().expect("Failed to load settings.");
  Ok(())
}
