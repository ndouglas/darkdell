use anyhow::Error as AnyError;
use std::path::PathBuf;

use crate::front_matter::FrontMatter;
use crate::settings::Settings;

/// A struct representation of any content.
#[derive(Debug)]
pub struct Content {
  /// The content path.
  pub content_path: PathBuf,
  /// The front matter.
  pub front_matter: FrontMatter,
  /// The excerpt.
  pub excerpt: Option<String>,
  /// The content.
  pub content: String,
}

impl Content {
  /// Get the output path for this content.
  pub fn get_output_path(&self, settings: &Settings) -> Result<PathBuf, AnyError> {
    self.front_matter.get_output_path(settings, &self.content_path)
  }
}
