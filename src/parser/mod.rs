use anyhow::Error as AnyError;
use gray_matter::engine::YAML;
use gray_matter::Matter;

use crate::front_matter::FrontMatter;
use crate::settings::Settings;

/// The `Parser` struct is responsible for parsing the content files.
pub struct Parser {
  /// The settings.
  settings: Settings,
}

impl Parser {
  /// Create a new parser.
  pub fn new(settings: Settings) -> Self {
    Self { settings }
  }

  /// Parse the content file.
  pub fn parse(&self, content_file: &str) -> Result<(FrontMatter, Option<String>, String), AnyError> {
    let mut matter = Matter::<YAML>::new();
    matter.excerpt_delimiter = self.settings.excerpt_delimiter.clone();
    let parsed_content = matter.parse(content_file);
    let front_matter: FrontMatter = parsed_content.data.unwrap().deserialize().unwrap();
    let result = (front_matter, parsed_content.excerpt, parsed_content.content);
    Ok(result)
  }
}
