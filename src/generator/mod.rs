use anyhow::Error as AnyError;
use log::{debug, trace};
use std::path::{Path, PathBuf};

use crate::processor::Processor;
use crate::settings::Settings;

/// The generator handles the actual generation of the site.
/// It will use the settings to determine where to look for content, where to
/// look for templates, and where to output the generated site.
pub struct Generator {
  /// The settings.
  settings: Settings,
}

impl Generator {
  /// Create a new generator.
  pub fn new(settings: Settings) -> Self {
    Self { settings }
  }

  /// Calculate the paths to the content files that need to be generated.
  #[allow(clippy::only_used_in_recursion)]
  pub fn calculate_content_files(&self, content_path: &Path) -> Result<Vec<PathBuf>, AnyError> {
    debug!("Calculating content files...");
    let mut content_files = Vec::new();
    for entry in content_path.read_dir()? {
      let entry = entry?;
      let path = entry.path();
      trace!("Path: {:?}", path);
      if path.is_dir() {
        let mut sub_content_files = self.calculate_content_files(&path)?;
        content_files.append(&mut sub_content_files);
      } else {
        content_files.push(path);
      }
    }
    Ok(content_files)
  }

  /// Generate the site.
  pub fn generate(&self) -> Result<(), AnyError> {
    trace!("Generating site...");
    debug!("Settings: {:#?}", self.settings);
    let content_path = self.settings.get_absolute_content_path();
    trace!("Content path: {:?}", content_path);
    let content_files = self.calculate_content_files(&content_path)?;
    debug!("Content files: {:#?}", content_files);
    // For each file, we will instantiate a new Processor and process the file.
    for content_file in content_files {
      trace!("Content file: {:?}", content_file);
      let processor = Processor::new(self.settings.clone(), content_file);
      processor.process()?;
    }
    Ok(())
  }
}
