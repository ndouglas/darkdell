use anyhow::anyhow;
use anyhow::Error as AnyError;
use comrak::Options;
use std::path::{Path, PathBuf};
use std::str::FromStr;

use crate::content::Content;
use crate::settings::Settings;

pub mod about;
pub mod blogroll;
pub mod index;
pub mod post;

pub use about::About;
pub use blogroll::Blogroll;
pub use index::Index;
pub use post::Post;

/// An enum for content types.
pub enum ContentType {
  About(About),
  Blogroll(Blogroll),
  Index(Index),
  Post(Post),
}

impl ContentType {
  /// Get the output path for this content type given the path to the content.
  pub fn get_output_path(&self, settings: &Settings, content_file_path: &Path) -> Result<PathBuf, AnyError> {
    match self {
      ContentType::About(content_type) => content_type.get_output_path(settings, content_file_path),
      ContentType::Blogroll(content_type) => content_type.get_output_path(settings, content_file_path),
      ContentType::Index(content_type) => content_type.get_output_path(settings, content_file_path),
      ContentType::Post(content_type) => content_type.get_output_path(settings, content_file_path),
    }
  }

  /// Render the body for this content.
  pub fn render_body(
    &self,
    settings: &Settings,
    options: &Options,
    content: &Content,
  ) -> Result<maud::Markup, AnyError> {
    match self {
      ContentType::About(content_type) => content_type.render_body(settings, options, content),
      ContentType::Blogroll(content_type) => content_type.render_body(settings, options, content),
      ContentType::Index(content_type) => content_type.render_body(settings, options, content),
      ContentType::Post(content_type) => content_type.render_body(settings, options, content),
    }
  }
}

impl FromStr for ContentType {
  type Err = AnyError;

  fn from_str(s: &str) -> Result<Self, Self::Err> {
    match s {
      "about" => Ok(ContentType::About(About {})),
      "blogroll" => Ok(ContentType::Blogroll(Blogroll {})),
      "index" => Ok(ContentType::Index(Index {})),
      "post" => Ok(ContentType::Post(Post {})),
      _ => Err(anyhow!("Unknown content type: {}", s)),
    }
  }
}
