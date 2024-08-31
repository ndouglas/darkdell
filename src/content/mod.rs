use anyhow::Error as AnyError;
use comrak::Options;
use maud::Markup;
use std::fs::{copy, create_dir_all};
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

  /// Copy assets for this content.
  pub fn copy_assets(&self, settings: &Settings) -> Result<(), AnyError> {
    // Get a listing of non-markdown files in the same directory as the content file.
    let directory = &self.content_path.parent().unwrap();
    let files = directory.read_dir()?;
    for file in files {
      let file = file?;
      let file_path = file.path();
      if file_path.is_file() && file_path.extension().is_some() {
        let extension = file_path.extension().unwrap();
        if extension != "md" {
          let relative_path = file_path.strip_prefix(settings.get_absolute_content_path())?;
          let mut output_path = settings.get_absolute_output_path();
          output_path.push(relative_path);
          create_dir_all(output_path.parent().unwrap())?;
          copy(&file_path, &output_path)?;
        }
      }
    }
    Ok(())
  }

  /// Render the body for this content.
  pub fn render_body(&self, settings: &Settings, options: &Options) -> Result<Markup, AnyError> {
    self.get_content_type()?.render_body(settings, options, self)
  }
}
