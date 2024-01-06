use anyhow::Error as AnyError;
use comrak::{markdown_to_html, Options};
use gray_matter::engine::YAML;
use gray_matter::Matter;
use log::trace;
use maud::{html, Markup, PreEscaped, DOCTYPE};

use crate::front_matter::FrontMatter;
use crate::settings::Settings;

/// The `Renderer` struct is responsible for rendering the HTML.
pub struct Renderer {
  /// The settings.
  settings: Settings,
  /// The options.
  options: Options,
}

impl Renderer {
  /// Create a new renderer.
  pub fn new(settings: Settings) -> Self {
    let mut options = Options::default();
    options.extension.table = true;
    options.extension.strikethrough = true;
    options.extension.tasklist = true;
    options.extension.footnotes = true;
    options.extension.autolink = true;
    options.extension.description_lists = true;
    options.extension.superscript = true;
    options.extension.header_ids = Some("section-".to_string());
    options.extension.shortcodes = true;
    options.render.hardbreaks = true;
    // options.render.unsafe_ = true;
    Self { settings, options }
  }

  /// Get only the front matter for a content file.
  pub fn get_front_matter(&self, content_file: &str) -> Result<FrontMatter, AnyError> {
    let mut matter = Matter::<YAML>::new();
    matter.excerpt_delimiter = self.settings.excerpt_delimiter.clone();
    let parsed_content = matter.parse(content_file);
    trace!("Parsed content: {:#?}", parsed_content);
    let front_matter: FrontMatter = parsed_content.data.unwrap().deserialize().unwrap();
    Ok(front_matter)
  }

  /// Render some markdown.
  pub fn render(&self, front_matter: &FrontMatter, content: &str) -> Result<String, AnyError> {
    let content_html = markdown_to_html(content, &self.options);
    let rendered_html = self.render_html(front_matter, &content_html).into_string();
    Ok(rendered_html)
  }

  /// Render the HTML.
  pub fn render_html(&self, front_matter: &FrontMatter, content: &str) -> Markup {
    let description = front_matter
      .description
      .clone()
      .unwrap_or(self.settings.description.clone().unwrap());
    let author = front_matter
      .author
      .clone()
      .unwrap_or(self.settings.author.clone().unwrap());
    let title = front_matter.title.clone().unwrap_or("Untitled".to_string());
    html! {
      (DOCTYPE)
      html lang="en" {
        head {
          meta charset="utf-8";
          meta name="viewport" content="width=device-width, initial-scale=1";
          meta name="description" content=(description);
          meta name="author" content=(author);
          meta name="generator" content="Darkdell";
          title {
            (title)
          }
          link rel="stylesheet" href="/css/style.css";
        }
        body {
          @match front_matter.r#type.as_str() {
            "index" => {
              div class="container" {
                div class="row" {
                  div class="col-md-12" {
                    (PreEscaped(content))
                  }
                }
              }
            },
            "post" => {
              div class="container" {
                div class="row" {
                  div class="col-md-12" {
                    (PreEscaped(content))
                  }
                }
              }
            },
            _ => {
              div class="container" {
                div class="row" {
                  div class="col-md-12" {
                    (PreEscaped(content))
                  }
                }
              }
            },
          }
        }
      }
    }
  }
}
