use anyhow::Error as AnyError;
use std::path::{Path, PathBuf};

use crate::settings::Settings;

pub mod about;
pub mod index;
pub mod post;

pub use about::About;
pub use index::Index;
pub use post::Post;

/// A trait for content types.
pub trait ContentType {
  /// Get the output path for this content type given the path to the content.
  fn get_output_path(&self, settings: &Settings, content_file_path: &Path) -> Result<PathBuf, AnyError>;
}
