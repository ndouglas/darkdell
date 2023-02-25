---
title: "Crow's Nest"
date: 2023-02-21T12:00:00-07:00
draft: true
categories: 
  - Libraries
languages:
  - Rust
tags:
  - Parsing
keywords: 
  - Crow's Nest
  - text adventure
  - interactive fiction
  - MUD
  - input parsing
  - Rust
aliases: []
repo_url: "https://github.com/ndouglas/crows_nest/"
demo_url: "https://ndouglas.github.io/crows_nest/demo/"
docs_url: "https://ndouglas.github.io/crows_nest/"
progress: 0
subtitle: 'An input parser for standard text adventure games, built in Rust.'
---
"Crow's Nest" is an input parser for standard text adventure games (e.g. interactive fiction, like Infocom's _Zork_ games, or MUDs). The project is an application library built in Rust.

The project should accept input of reasonable complexity, e.g. `go north`, `kill troll with sword`, `put the gold piece in the moneybag under the table`, and translates that input into actions that can be translated into modifications of the game world.

### Naming

The name "Crow's Nest" comes from a castle in Westeros, in _A Song of Ice and Fire_. I chose this name because a crow's nest is a lookout point on a ship, and in text adventures, players need to pay close attention to their surroundings to succeed.  The name "Crow's Nest" suggests a world that is full of observation and analysis, where the player must carefully observe their surroundings and make sense of the information they receive. It also implies a sense of strategy and planning, as the player must be able to use their knowledge to anticipate future events and make the best decisions.

## Motivations

I was motivated to pursue this project because I've always been a fan of interactive fiction and wanted to try my hand at building an input parser for these types of games. I also wanted to improve my skills with Rust, a language I find particularly interesting.

## Challenges

One of the biggest challenges I anticipate facing with this project is handling input that is both complex and ambiguous, which is common in text adventure games. To tackle this, I plan to implement a robust set of rules to handle different types of input and provide helpful error messages when input is unclear.

<!--

*Leave these sections commented out until the project is complete.*

*The project is not complete yet!  Do not fill this part out!*

## Postmortem

*After completing the project, provide a postmortem that includes a retrospective on how the project went. This should include any lessons learned, successes, and failures.*

### Successes

*Highlight the things that went well during the project.*

### Failures

*Identify the things that didn't go as planned, and explain why.*

### Lessons Learned

*Summarize the key takeaways from the project, including what you learned and what you would do differently next time.*

## Conclusion

*Wrap up the post with a brief conclusion, summarizing the key points of the project and what you achieved. Also, provide links to the project's code repository or live demo, if available.*

-->
