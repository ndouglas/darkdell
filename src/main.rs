use anyhow::Error as AnyError;
use darkdell::settings::Settings;

fn main() -> Result<(), AnyError> {
  let _settings = Settings::load().expect("Failed to load settings.");
  Ok(())
}
