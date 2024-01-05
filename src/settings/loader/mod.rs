use anyhow::Error as AnyError;
use std::fs::File;
use std::io::prelude::*;
use std::path::PathBuf;

use crate::settings::Settings;

pub struct Loader {}

impl Loader {
  /// Get the settings path.
  pub fn get_settings_path() -> PathBuf {
    let mut path = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
    path.push("darkdell.yaml");
    path
  }

  /// Create a new, empty settings file.
  pub fn create_empty() {
    let path = Loader::get_settings_path();
    File::create(&path).expect("Failed to create settings file.");
    println!("Created settings file at {:?}", path);
  }

  /// Read a settings file from the specified path.
  pub fn read(path: &PathBuf) -> Result<Settings, AnyError> {
    let mut file = File::open(path).expect("Failed to open settings file.");
    let mut settings_string = String::new();
    file
      .read_to_string(&mut settings_string)
      .expect("Failed to read settings file.");
    let settings: Settings = serde_yaml::from_str(&settings_string)?;
    Ok(settings)
  }

  /// This function will load the settings from the expected location.
  /// If the file doesn't exist, it will create an empty file there.
  pub fn load() -> Result<Settings, AnyError> {
    let path = Loader::get_settings_path();

    // If the settings file doesn't exist, create it as an empty file.
    if !path.exists() {
      Loader::create_empty();
    }

    // Read the settings file.
    Loader::read(&path)
  }
}

#[cfg(test)]
pub mod test {

  #[allow(unused_imports)]
  use super::*;
  use crate::test::init;

  #[test]
  fn test_loader() {
    // Initialize the test module.
    init();

    // Load the settings.
    let settings = Loader::load();

    // Print the settings.
    println!("{:?}", settings);
  }
}
