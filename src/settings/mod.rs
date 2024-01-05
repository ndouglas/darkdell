use serde::{Deserialize, Serialize};
use std::path::PathBuf;

pub mod loader;

/// The `Settings` struct will hold all of our settings.
/// It will be serialized/deserialized in YAML.
#[derive(Serialize, Deserialize, Debug, Default)]
pub struct Settings {
  #[serde(default = "Settings::get_default_output_path")]
  pub output_path: Option<String>,
  #[serde(default = "Settings::get_default_content_path")]
  pub content_path: Option<String>,
  #[serde(default = "Settings::get_default_template_path")]
  pub template_path: Option<String>,
  #[serde(default = "Settings::get_default_base_path")]
  pub base_path: Option<String>,
}

impl Settings {
  /// Get the default output path.
  pub fn get_default_output_path() -> Option<String> {
    Some("output".to_string())
  }

  /// Get the default content path.
  pub fn get_default_content_path() -> Option<String> {
    Some("content".to_string())
  }

  /// Get the default template path.
  pub fn get_default_template_path() -> Option<String> {
    Some("templates".to_string())
  }

  /// Get the default base path.
  pub fn get_default_base_path() -> Option<String> {
    let path = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
    Some(path.to_str().unwrap().to_string())
  }

  /// Get the absolute output path.
  pub fn get_absolute_output_path(&self) -> PathBuf {
    let mut path = PathBuf::from(self.base_path.as_ref().unwrap());
    path.push(self.output_path.as_ref().unwrap());
    path
  }

  /// Get the absolute content path.
  pub fn get_absolute_content_path(&self) -> PathBuf {
    let mut path = PathBuf::from(self.base_path.as_ref().unwrap());
    path.push(self.content_path.as_ref().unwrap());
    path
  }

  /// Get the absolute template path.
  pub fn get_absolute_template_path(&self) -> PathBuf {
    let mut path = PathBuf::from(self.base_path.as_ref().unwrap());
    path.push(self.template_path.as_ref().unwrap());
    path
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

    // (This test is not yet implemented.)
  }
}
