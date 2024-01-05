use anyhow::Error as AnyError;
use darkdell::settings::loader::Loader as SettingsLoader;

fn main() -> Result<(), AnyError> {
  let _settings = SettingsLoader::load().expect("Failed to load settings.");
  Ok(())
}
