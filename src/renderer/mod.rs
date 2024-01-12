use anyhow::Error as AnyError;
use comrak::Options;
use log::trace;
use maud::{html, Markup, PreEscaped, DOCTYPE};

use crate::content::Content;
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
    let rendered_html = html! {
      (DOCTYPE)
      html lang="en" {
        (self.render_header(content)?)
        body {
          (self.render_body(content)?)
          (self.render_footer(content)?)
        }
      }
    };
    Ok(rendered_html.into_string())
  }

  /// Render the header.
  pub fn render_header(&self, content: &Content) -> Result<Markup, AnyError> {
    let title = format!(
      "{} | {}",
      "Darkdell",
      content.front_matter.title.clone().unwrap_or("Untitled".to_string())
    );
    let author = content
      .front_matter
      .author
      .clone()
      .unwrap_or(self.settings.author.clone().unwrap());
    let description = content
      .front_matter
      .description
      .clone()
      .unwrap_or(self.settings.description.clone().unwrap());
    let result = html! {
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
    };
    Ok(result)
  }

  /// Render the body.
  pub fn render_body(&self, content: &Content) -> Result<Markup, AnyError> {
    content.render_body(&self.settings, &self.options)
  }

  /// Render the footer.
  pub fn render_footer(&self, _content: &Content) -> Result<Markup, AnyError> {
    let result = html! {
      footer class="footer" {
        ul style="list-style-type: none; margin: 0; padding: 0;" {
          li style="display: inline;" {
            a href="/" {
              "Darkdell"
            }
            (PreEscaped("&nbsp;&bull;&nbsp;"))
            a href="/about.html" {
              "About"
            }
            (PreEscaped("&nbsp;&bull;&nbsp;"))
            a href="/blogroll.html" {
              "Blogroll"
            }
            (PreEscaped("&nbsp;&bull;&nbsp;"))
            a href="https://github.com/ndouglas" {
              "GitHub"
            }
          }
        }
      }
    };
    Ok(result)
  }
}
