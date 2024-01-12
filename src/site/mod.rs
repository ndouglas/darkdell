use anyhow::Error as AnyError;
use log::trace;

use crate::content::Content;
use crate::processor::Processor;
use crate::settings::Settings;

/// The Site contains all of the content for the site.
#[derive(Debug)]
pub struct Site {
  /// The content for the site.
  pub content: Vec<Content>,
  /// The settings for the site.
  pub settings: Settings,
}

impl Site {
  /// Create a new site.
  pub fn new(content: Vec<Content>, settings: Settings) -> Self {
    Self { content, settings }
  }

  /// Build the site.
  pub fn build(&self) -> Result<(), AnyError> {
    let processor = Processor::new(self.settings.clone());
    for content in self.content.iter() {
      trace!("Processing content: {:?}", content);
      processor.process(content)?;
    }
    Ok(())
  }

  /// Get a list of all posts.
  pub fn get_posts(&self) -> Vec<&Content> {
    self
      .content
      .iter()
      .filter(|content| content.front_matter.r#type == "post")
      .collect()
  }
}
