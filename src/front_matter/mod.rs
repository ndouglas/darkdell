use serde::Deserialize;

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
}
