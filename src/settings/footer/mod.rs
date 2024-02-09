use anyhow::Error as AnyError;
use maud::{html, Markup, PreEscaped};
use serde::{Deserialize, Serialize};

pub mod link;
use link::FooterLink;

/// Footer settings.
#[derive(Debug, Default, Clone, Serialize, Deserialize)]
pub struct FooterSettings {
  /// Footer links.
  #[serde(default = "FooterSettings::get_default_footer_links")]
  pub links: Option<Vec<FooterLink>>,
}

impl FooterSettings {
  /// Get the default footer links.
  pub fn get_default_footer_links() -> Option<Vec<FooterLink>> {
    Some(vec![
      FooterLink {
        title: "Home".to_string(),
        href: "/".to_string(),
      },
      FooterLink {
        title: "About".to_string(),
        href: "/about/".to_string(),
      },
      FooterLink {
        title: "Contact".to_string(),
        href: "/contact/".to_string(),
      },
    ])
  }

  /// Get formatted individual link items.
  pub fn get_link_items(&self) -> Result<Vec<Markup>, AnyError> {
    let link_items = self
      .links
      .clone()
      .unwrap_or_default()
      .iter()
      .map(|link| link.get_formatted_link().unwrap())
      .collect::<Vec<Markup>>();
    Ok(link_items)
  }

  /// Get formatted, separated link items.
  pub fn get_separated_link_items(&self, separator: Markup) -> Result<Vec<Markup>, AnyError> {
    let link_items = self.get_link_items()?;
    let first_link = [link_items.first().unwrap().clone()];
    let subsequent_links = link_items
      .iter()
      .skip(1)
      .flat_map(|link| vec![separator.clone(), link.clone()])
      .collect::<Vec<Markup>>();
    let result = first_link
      .iter()
      .chain(subsequent_links.iter())
      .cloned()
      .collect::<Vec<Markup>>();
    Ok(result)
  }

  /// Get the formatted link list.
  pub fn get_link_list(&self) -> Result<Markup, AnyError> {
    let link_items = self.get_separated_link_items(PreEscaped("&nbsp;&bull;&nbsp;".to_string()))?;
    let result = html! {
      ul style="margin: 0; padding: 0;" {
        @for link in link_items {
          (link)
        }
      }
    };
    Ok(result)
  }
}
