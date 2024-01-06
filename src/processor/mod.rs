use anyhow::Error as AnyError;
use gray_matter::engine::YAML;
use gray_matter::Matter;
use log::trace;
use std::fs::read_to_string;
use std::path::PathBuf;

use crate::front_matter::FrontMatter;
use crate::settings::Settings;

/// The Processor struct will handle the processing of each individual page.
/// It is passed a path to a content file, and it will read the file, parse it,
/// render it, and write it to the output directory.
pub struct Processor {
  /// The settings.
  pub settings: Settings,
  /// The path to the content file.
  pub content_file_path: PathBuf,
}

impl Processor {
  /// Create a new processor.
  pub fn new(settings: Settings, content_file_path: PathBuf) -> Self {
    Self {
      settings,
      content_file_path,
    }
  }

  /// Parse the content file.
  pub fn parse(&self, content_file: &str) -> Result<(FrontMatter, Option<String>, String), AnyError> {
    let mut matter = Matter::<YAML>::new();
    matter.excerpt_delimiter = self.settings.excerpt_delimiter.clone();
    let parsed_content = matter.parse(content_file);
    let front_matter: FrontMatter = parsed_content.data.unwrap().deserialize().unwrap();
    let content = {
      if let Some(ref excerpt) = parsed_content.excerpt {
        parsed_content.content.replace(excerpt, "")
      } else {
        parsed_content.content
      }
    };
    let result = (front_matter, parsed_content.excerpt, content);
    Ok(result)
  }

  /// Process the content file.
  pub fn process(&self) -> Result<(), AnyError> {
    // This process will consist of:
    // 1. Reading the content file.
    // 2. Parsing the content file.
    // 3. Rendering the content file.
    // 4. Writing the rendered content file to the output directory.
    let content_file = read_to_string(&self.content_file_path)?;
    trace!("Content file: {:?}", content_file);
    let (front_matter, excerpt, content) = self.parse(&content_file)?;
    trace!("Front matter: {:#?}", front_matter);
    trace!("Excerpt: {:#?}", excerpt);
    trace!("Content: {:#?}", content);
    Ok(())
  }
}
