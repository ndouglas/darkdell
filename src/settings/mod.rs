use anyhow::Error as AnyError;
use serde::{Deserialize, Serialize};
use std::fs::File;
use std::io::prelude::*;
use std::path::PathBuf;

/// The `Settings` struct will hold all of our settings.
/// It will be serialized/deserialized in YAML.
#[derive(Serialize, Deserialize, Debug, Default)]
pub struct Settings {
  #[serde(default)]
  output_dir: Option<String>,
}

impl Settings {

  /// Get the settings path.
  pub fn get_settings_path() -> PathBuf {
    let mut path = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
    path.push("darkdell.yaml");
    path
  }

  /// Create a new settings file with the default settings.
  pub fn create_default() {
    let path = Settings::get_settings_path();
    let mut file = File::create(&path).expect("Failed to create settings file.");
    let settings = Settings::default();
    let settings_string = serde_yaml::to_string(&settings).expect("Failed to serialize settings.");
    file
      .write_all(settings_string.as_bytes())
      .expect("Failed to write settings to file.");
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

  /// This function will load the settings from the specified file.
  /// If the file doesn't exist, it will create it and write the default settings to it.
  pub fn load() -> Result<Settings, AnyError> {
    let path = Settings::get_settings_path();

    // If the settings file doesn't exist, create it and write the default settings to it.
    if !path.exists() {
      Settings::create_default();
    }

    // Read the settings file.
    Settings::read(&path)
  }
}

#[cfg(test)]
pub mod test {

  #[allow(unused_imports)]
  use super::*;
  use crate::test::init;

  #[test]
  fn test_settings() {
    // Initialize the test module.
    init();

    // Load the settings.
    let settings = Settings::load();

    // Print the settings.
    println!("{:?}", settings);
  }
}
