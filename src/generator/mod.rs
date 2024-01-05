use anyhow::Error as AnyError;
use maud::html;
use std::fs::write;

use crate::settings::Settings;

/// The generator handles the actual generation of the site.
/// It will use the settings to determine where to look for content, where to
/// look for templates, and where to output the generated site.
pub struct Generator {
  /// The settings.
  settings: Settings,
}

impl Generator {
  /// Create a new generator.
  pub fn new(settings: Settings) -> Self {
    Self { settings }
  }

  /// Generate the site.
  pub fn generate(&self) -> Result<(), AnyError> {
    println!("Generating site...");
    println!("Settings: {:#?}", self.settings);
    // For right now, we'll just write a "Hello world" file to the output path.
    let markup = html! {
      head {
        title { "Darkdell" }
      }
      p { 
        "Hello world!"
        br;
        "I'm apparently dumb enough to write my own SSG, so... watch this space. And don't expect much."
      }
    };
    let mut path = self.settings.get_absolute_output_path();
    path.push("index.html");
    write(path, markup.into_string())?;
    Ok(())
  }
}
