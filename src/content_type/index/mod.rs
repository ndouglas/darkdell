use anyhow::Error as AnyError;
use std::path::{Path, PathBuf};

use crate::content_type::ContentType;
use crate::settings::Settings;

/// Index page.
pub struct Index {}

impl ContentType for Index {
  /// Get the output path for this content type given the path to the content.
  fn get_output_path(&self, settings: &Settings, content_file_path: &Path) -> Result<PathBuf, AnyError> {
    let content_path = settings.get_absolute_content_path();
    let relative_path = content_file_path.strip_prefix(&content_path)?;
    let file_name = relative_path.to_str().unwrap().to_string().replace(".md", ".html");
    let mut output_path = settings.get_absolute_output_path();
    output_path.push(file_name);
    Ok(output_path)
  }
}
