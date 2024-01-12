use anyhow::Error as AnyError;
use gray_matter::engine::YAML;
use gray_matter::Matter;
use std::fs::read_to_string;
use std::path::{Path, PathBuf};

use crate::content::Content;
use crate::front_matter::FrontMatter;
use crate::settings::Settings;

/// The `Parser` struct is responsible for parsing the content files, yielding
/// a `Content` struct.
pub struct Parser {
  /// The settings.
  settings: Settings,
}

impl Parser {
  /// Create a new parser.
  pub fn new(settings: Settings) -> Self {
    Self { settings }
  }

  /// Parse all of some content files.
  pub fn parse_all(&self, content_file_paths: &[PathBuf]) -> Result<Vec<Content>, AnyError> {
    let mut parsed_content_files = Vec::new();
    for content_file_path in content_file_paths {
      let raw_content = read_to_string(content_file_path)?;
      let content = self.parse(content_file_path, &raw_content)?;
      parsed_content_files.push(content);
    }
    Ok(parsed_content_files)
  }

  /// Parse the content file.
  pub fn parse(&self, content_path: &Path, raw_content: &str) -> Result<Content, AnyError> {
    let mut matter = Matter::<YAML>::new();
    matter.excerpt_delimiter = self.settings.excerpt_delimiter.clone();
    let parsed_content = matter.parse(raw_content);
    let front_matter: FrontMatter = parsed_content.data.unwrap().deserialize()?;
    let excerpt = parsed_content.excerpt;
    let content = parsed_content.content;
    let result = Content {
      content_path: content_path.to_path_buf(),
      front_matter,
      excerpt,
      raw_content: content.to_string(),
    };
    Ok(result)
  }
}
