use anyhow::Error as AnyError;
use comrak::{markdown_to_html, Options};
use maud::{html, Markup, PreEscaped};
use std::path::{Path, PathBuf};

use crate::content::Content;
use crate::settings::Settings;

/// Blogroll page.
pub struct Blogroll {}

impl Blogroll {
  /// Get the output path for this content type given the path to the content.
  pub fn get_output_path(&self, settings: &Settings, content_file_path: &Path) -> Result<PathBuf, AnyError> {
    let content_path = settings.get_absolute_content_path();
    let relative_path = content_file_path.strip_prefix(&content_path)?;
    let file_name = relative_path.to_str().unwrap().to_string().replace(".md", ".html");
    let mut output_path = settings.get_absolute_output_path();
    output_path.push(file_name);
    Ok(output_path)
  }

  /// Render the body.
  pub fn render_body(&self, _settings: &Settings, options: &Options, content: &Content) -> Result<Markup, AnyError> {
    let content_html = markdown_to_html(&content.raw_content, options);
    let result = html! {
      div class="content" {
        (PreEscaped(content_html))
      }
    };
    Ok(result)
  }
}
