use serde::{Deserialize, Serialize};

pub mod loader;

/// The `Settings` struct will hold all of our settings.
/// It will be serialized/deserialized in YAML.
#[derive(Serialize, Deserialize, Debug, Default)]
pub struct Settings {
  #[serde(default = "Settings::get_default_output_path")]
  pub output_path: Option<String>,
}

impl Settings {
  /// Get the default output path.
  pub fn get_default_output_path() -> Option<String> {
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
  }
}
