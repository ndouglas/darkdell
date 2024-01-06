use anyhow::Error as AnyError;
use log::trace;
use std::fs::{create_dir_all, read_to_string, write};
use std::path::{Path, PathBuf};

use crate::parser::Parser;
use crate::renderer::Renderer;
use crate::settings::Settings;

/// The Processor struct will handle the processing of each individual page.
/// It is passed a path to a content file, and it will read the file, parse it,
/// render it, and write it to the output directory.
pub struct Processor {
  /// The settings.
  pub settings: Settings,
  /// The parser.
  pub parser: Parser,
  /// The renderer.
  pub renderer: Renderer,
}

impl Processor {
  /// Create a new processor.
  pub fn new(settings: Settings) -> Self {
    Self {
      settings: settings.clone(),
      parser: Parser::new(settings.clone()),
      renderer: Renderer::new(settings.clone()),
    }
  }

  /// Write the rendered content to the output directory.
  pub fn write(&self, file_name: &Path, rendered_content: &str) -> Result<(), AnyError> {
    trace!("Writing file: {:?}", file_name);
    create_dir_all(file_name.parent().unwrap())?;
    write(file_name, rendered_content)?;
    Ok(())
  }

  /// Get the file name relative to the content directory, then append the
  /// HTML extension and prepend the output directory.
  pub fn get_file_name(&self, content_file_path: &Path) -> Result<PathBuf, AnyError> {
    let content_path = self.settings.get_absolute_content_path();
    let relative_path = content_file_path.strip_prefix(&content_path)?;
    let mut file_name = relative_path.to_str().unwrap().to_string().replace(".md", "");
    file_name.push_str(".html");
    let mut output_path = self.settings.get_absolute_output_path();
    output_path.push(file_name);
    Ok(output_path)
  }

  /// Process the content file.
  pub fn process(&self, content_file_path: &Path) -> Result<(), AnyError> {
    // This process will consist of:
    // 1. Reading the content file.
    // 2. Parsing the content file.
    // 3. Rendering the content file.
    // 4. Writing the rendered content file to the output directory.
    let content_file = read_to_string(content_file_path)?;
    trace!("Content file: {:?}", content_file);
    let (front_matter, excerpt, content) = self.parser.parse(&content_file)?;
    trace!("Front matter: {:#?}", front_matter);
    trace!("Excerpt: {:#?}", excerpt);
    trace!("Content: {:#?}", content);
    let file_name = self.get_file_name(content_file_path)?;
    trace!("File name: {:?}", file_name);
    let rendered_page = self.renderer.render(&front_matter, &content)?;
    trace!("Rendered page: {:#?}", rendered_page);
    self.write(&file_name, &rendered_page)?;
    Ok(())
  }
}
