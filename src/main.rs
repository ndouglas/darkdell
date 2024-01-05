use anyhow::Error as AnyError;
use darkdell::prelude::*;

fn main() -> Result<(), AnyError> {
  let settings = SettingsLoader::load().expect("Failed to load settings.");
  let generator = Generator::new(settings);
  generator.generate()?;
  Ok(())
}
