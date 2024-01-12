use anyhow::anyhow;
use anyhow::Error as AnyError;
use serde::Deserialize;
use std::path::{Path, PathBuf};

use crate::content_type::{About, ContentType, Index, Post};
use crate::settings::Settings;

/// The `FrontMatter` struct will hold all of our front matter.
/// It will be deserialized in YAML.
#[derive(Deserialize, Debug)]
pub struct FrontMatter {
  #[serde(default)]
  pub title: Option<String>,
  #[serde(default)]
  pub author: Option<String>,
  #[serde(default)]
  pub date: Option<String>,
  #[serde(default)]
  pub draft: bool,
  #[serde(default = "FrontMatter::get_default_type")]
  pub r#type: String,
  #[serde(default = "Vec::new")]
  pub tags: Vec<String>,
  #[serde(default)]
  pub description: Option<String>,
}

impl FrontMatter {
  /// Get the default type.
  pub fn get_default_type() -> String {
    "index".to_string()
  }

  /// Get the output path for this content.
  pub fn get_output_path(&self, settings: &Settings, content_file_path: &Path) -> Result<PathBuf, AnyError> {
    match self.r#type.as_str() {
      "about" => About {}.get_output_path(settings, content_file_path),
      "index" => Index {}.get_output_path(settings, content_file_path),
      "post" => Post {}.get_output_path(settings, content_file_path),
      _ => Err(anyhow!("Unknown content type: {}", self.r#type)),
    }
  }
}
