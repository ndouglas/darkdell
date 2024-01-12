use anyhow::Error as AnyError;
use std::path::{Path, PathBuf};

use crate::content_type::ContentType;
use crate::settings::Settings;

/// Individual post.
pub struct Post {}

impl ContentType for Post {
  /// Get the output path for this content type given the path to the content.
  fn get_output_path(&self, settings: &Settings, content_file_path: &Path) -> Result<PathBuf, AnyError> {
    let content_path = settings.get_absolute_content_path();
    let relative_path = content_file_path.strip_prefix(&content_path)?;
    let mut file_name = relative_path.to_str().unwrap().to_string().replace(".md", "/");
    file_name.push_str("index.html");
    let mut output_path = settings.get_absolute_output_path();
    output_path.push(file_name);
    Ok(output_path)
  }
}
