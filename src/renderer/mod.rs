use anyhow::Error as AnyError;
use comrak::nodes::{AstNode, NodeValue};
use comrak::{format_html, parse_document, Arena, Options};
use maud::{html, Markup, PreEscaped, DOCTYPE};
use std::mem::take;

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
    Self {
      settings,
      options: Options::default(),
    }
  }

  /// Render some markdown.
  pub fn render(&self, front_matter: &FrontMatter, content: &str) -> Result<String, AnyError> {
    let arena = Arena::new();
    let root = parse_document(&arena, content, &self.options);
    iter_nodes(root, &|node| {
      if let &mut NodeValue::Text(ref mut text) = &mut node.data.borrow_mut().value {
        let orig = take(text);
        *text = orig.replace("my", "your");
      }
    });
    let mut html = vec![];
    format_html(root, &self.options, &mut html)?;
    let content = String::from_utf8(html)?;
    let result = self.render_html(front_matter, &content);
    Ok(result.into_string())
  }

  /// Render the HTML.
  pub fn render_html(&self, front_matter: &FrontMatter, content: &str) -> Markup {
    html! {
      (DOCTYPE)
      html lang="en" {
        head {
          meta charset="utf-8";
          meta name="viewport" content="width=device-width, initial-scale=1";
          meta name="description" content=(front_matter.description.clone().unwrap_or(self.settings.description.clone().unwrap()));
          meta name="author" content=(front_matter.author.clone().unwrap_or(self.settings.author.clone().unwrap()));
          meta name="generator" content="Darkdell";
          //title (title)
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

/// Iterate over the nodes.
fn iter_nodes<'a, F>(node: &'a AstNode<'a>, f: &F)
where
  F: Fn(&'a AstNode<'a>),
{
  f(node);
  for c in node.children() {
    iter_nodes(c, f);
  }
}
