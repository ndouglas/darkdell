use anyhow::Error as AnyError;
use serde::{Deserialize, Serialize};
use std::fs::File;
use std::io::prelude::*;
use std::path::PathBuf;

/// The `Settings` struct will hold all of our settings.
/// It will be serialized/deserialized in YAML.
#[derive(Serialize, Deserialize, Debug, Default)]
pub struct Settings {
  #[serde(default = "Settings::get_default_output_dir")]
  pub output_dir: Option<String>,
}

impl Settings {
  /// Get the settings path.
  pub fn get_settings_path() -> PathBuf {
    let mut path = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
    path.push("darkdell.yaml");
    path
  }

  /// Create a new, empty settings file.
  pub fn create_empty() {
    let path = Settings::get_settings_path();
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

  /// This function will load the settings from the specified file.
  /// If the file doesn't exist, it will create it and write the default settings to it.
  pub fn load() -> Result<Settings, AnyError> {
    let path = Settings::get_settings_path();

    // If the settings file doesn't exist, create it as an empty file.
    if !path.exists() {
      Settings::create_empty();
    }

    // Read the settings file.
    Settings::read(&path)
  }

  /// Get the default output directory.
  pub fn get_default_output_dir() -> Option<String> {
    Some("output".to_string())
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
