use anyhow::Error as AnyError;
use darkdell::prelude::*;
use log::LevelFilter;
use pretty_env_logger::env_logger::builder as pretty_env_logger_builder;

fn main() -> Result<(), AnyError> {
  pretty_env_logger_builder().filter_level(LevelFilter::Trace).init();
  let settings = SettingsLoader::load().expect("Failed to load settings.");
  let generator = Generator::new(settings);
  generator.generate()?;
  Ok(())
}
