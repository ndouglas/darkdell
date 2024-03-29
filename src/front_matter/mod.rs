use anyhow::Error as AnyError;
use iso8601::{datetime, DateTime};
use serde::Deserialize;
use std::str::FromStr;

use crate::content_type::ContentType;

/// The `FrontMatter` struct will hold all of our front matter.
/// It will be deserialized in YAML.
#[derive(Deserialize, Debug)]
pub struct FrontMatter {
  #[serde(default)]
  pub title: Option<String>,
  #[serde(default)]
  pub author: Option<String>,
  #[serde(default)]
  pub date: Option<String>,
  #[serde(default)]
  pub draft: bool,
  #[serde(default = "FrontMatter::get_default_type")]
  pub r#type: String,
  #[serde(default = "Vec::new")]
  pub tags: Vec<String>,
  #[serde(default)]
  pub description: Option<String>,
}

impl FrontMatter {
  /// Get the default type.
  pub fn get_default_type() -> String {
    "index".to_string()
  }

  /// Get the default datetime.
  pub fn get_default_datetime() -> DateTime {
    datetime("1970-01-01T00:00:00Z").unwrap()
  }

  /// Get the output path for this content.
  pub fn get_content_type(&self) -> Result<ContentType, AnyError> {
    ContentType::from_str(&self.r#type)
  }

  /// Get the date, formatted as a string.
  pub fn get_datetime(&self) -> Result<DateTime, AnyError> {
    match datetime(&self.date.clone().unwrap()) {
      Ok(datetime) => Ok(datetime),
      Err(_) => Ok(FrontMatter::get_default_datetime()),
    }
  }
}
