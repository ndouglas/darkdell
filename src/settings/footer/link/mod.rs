use anyhow::Error as AnyError;
use maud::{html, Markup};
use serde::{Deserialize, Serialize};

/// Footer links.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FooterLink {
  /// Link title.
  pub title: String,
  /// Link href.
  pub href: String,
}

impl FooterLink {
  /// Get the formatted link.
  pub fn get_formatted_link(&self) -> Result<Markup, AnyError> {
    let result = html! {
      li style="display: inline-block;" {
        a href=(self.href) {
          (self.title)
        }
      }
    };
    Ok(result)
  }
}
