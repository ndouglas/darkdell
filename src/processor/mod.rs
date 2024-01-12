use anyhow::Error as AnyError;
use log::trace;
use std::fs::{create_dir_all, write};
use std::path::Path;

use crate::content::Content;
use crate::renderer::Renderer;
use crate::settings::Settings;

/// The Processor struct will handle the processing of each individual page.
/// It is passed a path to a content file, and it will read the file, parse it,
/// render it, and write it to the output directory.
pub struct Processor {
  /// The settings.
  pub settings: Settings,
  /// The renderer.
  pub renderer: Renderer,
}

impl Processor {
  /// Create a new processor.
  pub fn new(settings: Settings) -> Self {
    Self {
      settings: settings.clone(),
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

  /// Process the content file.
  pub fn process(&self, content: &Content) -> Result<(), AnyError> {
    // This process will consist of rendering the content file and writing the
    // rendered content file to the output directory.
    trace!("Content: {:#?}", content);
    let file_name = content.get_output_path(&self.settings)?;
    trace!("File name: {:?}", file_name);
    let rendered_page = self.renderer.render(content)?;
    trace!("Rendered page: {:#?}", rendered_page);
    self.write(&file_name, &rendered_page)?;
    Ok(())
  }
}
