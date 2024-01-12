use anyhow::Error as AnyError;
use comrak::Options;
use maud::Markup;
use std::path::PathBuf;

use crate::content_type::ContentType;
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
  pub raw_content: String,
}

impl Content {
  /// Get the content type for this content.
  pub fn get_content_type(&self) -> Result<ContentType, AnyError> {
    self.front_matter.get_content_type()
  }

  /// Get the output path for this content.
  pub fn get_output_path(&self, settings: &Settings) -> Result<PathBuf, AnyError> {
    self.get_content_type()?.get_output_path(settings, &self.content_path)
  }

  /// Render the body for this content.
  pub fn render_body(&self, settings: &Settings, options: &Options) -> Result<Markup, AnyError> {
    self.get_content_type()?.render_body(settings, options, self)
  }
}
