pub mod content;
pub mod content_type;
pub mod front_matter;
pub mod generator;
pub mod parser;
pub mod processor;
pub mod renderer;
pub mod settings;
pub mod site;

pub mod prelude {
  pub use crate::content::Content;
  pub use crate::content_type::{About, Index, Post};
  pub use crate::front_matter::FrontMatter;
  pub use crate::generator::Generator;
  pub use crate::parser::Parser;
  pub use crate::processor::Processor;
  pub use crate::renderer::Renderer;
  pub use crate::settings::loader::Loader as SettingsLoader;
  pub use crate::settings::Settings;
  pub use crate::site::Site;
}

#[cfg(test)]
pub mod test {

  use pretty_env_logger::env_logger::builder;
  use std::env::set_var;

  #[allow(unused_imports)]
  use super::*;

  // Call this function at the beginning of each test module.
  pub fn init() {
    // Enable logging for tests.
    let _ = builder().is_test(true).try_init();
    // Enable backtraces.
    set_var("RUST_BACKTRACE", "1");
  }
}
