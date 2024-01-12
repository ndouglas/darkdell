use anyhow::Error as AnyError;
use comrak::{markdown_to_html, Options};
use log::trace;
use maud::{html, Markup, PreEscaped, DOCTYPE};

use crate::content::Content;
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

  /// Render some markdown.
  pub fn render(&self, content: &Content) -> Result<String, AnyError> {
    trace!("Rendering content: {:#?}", content);
    let content_html = markdown_to_html(&content.content, &self.options);
    let rendered_html = html! {
      (DOCTYPE)
      html lang="en" {
        (self.render_header(&content.front_matter))
        body {
          @match content.front_matter.r#type.as_str() {
            "index" => {
              div class="container" {
                div class="row" {
                  div class="col-md-12" {
                    (PreEscaped(content_html))
                  }
                }
              }
            },
            "post" => {
              div class="container" {
                div class="row" {
                  div class="col-md-12" {
                    (PreEscaped(content_html))
                  }
                }
              }
            },
            _ => {
              div class="container" {
                div class="row" {
                  div class="col-md-12" {
                    (PreEscaped(content_html))
                  }
                }
              }
            },
          }
          (self.render_footer(&content.front_matter))
        }
      }
    };
    Ok(rendered_html.into_string())
  }

  /// Render the header.
  pub fn render_header(&self, front_matter: &FrontMatter) -> Markup {
    let title = front_matter.title.clone().unwrap_or("Untitled".to_string());
    let author = front_matter
      .author
      .clone()
      .unwrap_or(self.settings.author.clone().unwrap());
    let description = front_matter
      .description
      .clone()
      .unwrap_or(self.settings.description.clone().unwrap());
    html! {
      head {
        meta charset="utf-8";
        meta name="viewport" content="width=device-width, initial-scale=1";
        meta name="description" content=(description);
        meta name="author" content=(author);
        meta name="generator" content="Darkdell";
        title {
          (title)
        }
      }
    }
  }

  /// Render the footer.
  pub fn render_footer(&self, _front_matter: &FrontMatter) -> Markup {
    html! {
      footer class="footer" {
      }
    }
  }
}
