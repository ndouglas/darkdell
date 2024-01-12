use anyhow::Error as AnyError;
use log::{debug, trace};
use std::fs::{create_dir_all, remove_dir_all};
use std::path::{Path, PathBuf};

use crate::parser::Parser;
use crate::settings::Settings;
use crate::site::Site;

/// The generator handles the actual generation of the site.
/// It will use the settings to determine where to look for content, where to
/// look for templates, and where to output the generated site.
pub struct Generator {
  /// The settings.
  settings: Settings,
  /// The parser.
  parser: Parser,
}

impl Generator {
  /// Create a new generator.
  pub fn new(settings: Settings) -> Self {
    Self {
      settings: settings.clone(),
      parser: Parser::new(settings.clone()),
    }
  }

  /// Calculate the paths to the content files that need to be generated.
  #[allow(clippy::only_used_in_recursion)]
  pub fn calculate_content_files(&self, content_path: &Path) -> Result<Vec<PathBuf>, AnyError> {
    debug!("Calculating content files at {:?}", content_path);
    let mut content_files = Vec::new();
    for entry in content_path.read_dir()? {
      let entry = entry?;
      let path = entry.path();
      trace!("Found content file at path: {:?}", path);
      if path.is_dir() {
        let mut sub_content_files = self.calculate_content_files(&path)?;
        content_files.append(&mut sub_content_files);
      } else {
        content_files.push(path);
      }
    }
    Ok(content_files)
  }

  /// Clean the output directory.
  pub fn clean_output_directory(&self) -> Result<(), AnyError> {
    trace!("Cleaning output directory...");
    let output_path = self.settings.get_absolute_output_path();
    trace!("Output path: {:?}", output_path);
    if output_path.exists() {
      debug!("Removing output directory...");
      remove_dir_all(&output_path)?;
    }
    create_dir_all(&output_path)?;
    Ok(())
  }

  /// Generate the site.
  pub fn generate(&self) -> Result<(), AnyError> {
    trace!("Generating site...");
    debug!("Settings: {:#?}", self.settings);
    let content_path = self.settings.get_absolute_content_path();
    trace!("Content path: {:?}", content_path);
    let content_files = self.calculate_content_files(&content_path)?;
    debug!("Content files: {:#?}", content_files);
    let content = self.parser.parse_all(&content_files)?;
    debug!("Content: {:#?}", content);
    self.clean_output_directory()?;
    let site = Site::new(content, self.settings.clone());
    site.build()?;
    Ok(())
  }
}
