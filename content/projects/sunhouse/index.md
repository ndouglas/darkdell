---
title: "Sunhouse"
date: 2023-02-17T23:23:47-05:00
draft: false
categories:
  - Apps
languages:
  - Gherkin
  - Rust
tags:
  - Graphics
  - Ray-Tracing
keywords: []
aliases: []
repo_url: "https://github.com/ndouglas/sunhouse/"
demo_url: "https://ndouglas.github.io/sunhouse/demo/"
docs_url: "https://ndouglas.github.io/sunhouse/"
progress: 0
subtitle: 'A simple ray tracer built in Rust.'
---
Graphics programming, and especially 3-D rendering, has always been intimidating to me.  The math, the physics, the jargon, and the computational complexity were daunting.  I didn't have a powerful computer when I first became interested in programming; I limped through the '90's with a Packard Bell 486SX-33MHz with 4MB RAM.  I wasn't gaming on it, and I definitely wasn't going to trailblaze 3D graphics programming.

As the father of a child who loves computer gaming, though, I've regained a lot of the interest that I had when I was younger.  And because of the way my brain works, I really struggle to understand how something works unless I actually build it myself.
<!--more-->

## Summary

I'll be working through Jamis Buck's _The Ray Tracer Challenge: A Test-Driven Guide to Your First 3D Renderer_.  I'll use Rust, since that's my general choice for performance-intensive tasks.

The book provides test scenarios written in Cucumber, and I found [`cucumber-rs`](https://github.com/cucumber-rs/cucumber), so I think I'll be able to translate them.  I have some experience in Cucumber from work, where I use it extensively for writing behavioral tests and step definitions for Cypress.

## Naming

ChatGPT analyzed my naming as follows:

>"Sun" is a fitting word to include in the name of a ray tracer because it represents the source of light in a scene, and a ray tracer works by tracing the paths of rays of light as they bounce around a scene. Additionally, the word "sun" can connote warmth, energy, and brightness, which are all qualities that could be associated with a powerful and effective graphics library.

>"House" is also an interesting word to include in the name because it suggests stability, protection, and support. Just as a house provides shelter and a stable foundation, a graphics library provides a framework and structure for building complex visual experiences. A well-designed graphics library can offer stability, protection against common issues, and support for a wide range of use cases.

>Finally, the name "Sunhouse" specifically refers to the castle in the _A Song of Ice and Fire_ series, which was the ancestral seat of House Dayne[^1]. This connection could be meaningful for fans of the series who are also interested in computer graphics and programming, as it creates a connection between the fictional world of Westeros and the real-world tools used to create visual content.

>Overall, the name "Sunhouse" could be a fitting and meaningful choice for a ray tracer and graphics library, as it combines words that evoke qualities like warmth, energy, stability, and protection, while also nodding to a beloved fictional universe.

## Motivations

Weirdly, as I've grown older I find games _more_ interesting, not less.  I still never have time to play the damned things, and my Steam backlog is just getting longer over time, but I find the arts and sciences of game design and development very interesting.  I... I wanna make a game.  I just don't know what about.  I have ideas, but nothing concrete.

But I also really enjoy watching videos on YouTube that illustrate some idea or principle like natural selection and machine learning and do so with animations.  My kid and I love watching that stuff.  And... I can't really do that sort of thing yet.

Of course, it's absolutely _not_ necessary to write a ray tracer to do that sort of thing -- I could embark on the comparatively sane and fun-filled course of just making a lot of little gamelets in Unity.  But I think a lot of this is also about imposter syndrome, etc.  I want to think through this stuff from a fundamental level.

_That_ is probably inspired by my first experiences attempting to code a real application.  About twenty years ago, I tried to program a modern OS X app by opening Xcode and clicking around.  Of course, I felt like an idiot doing so.  I fundamentally did not understand the underlying reasons for what I was doing -- the underpinnings for things like bindings, observers, delegates, and so forth -- and I was painfully aware of that.  I was just clicking UI elements and trying to make an app.

So I think I have a deep suspicion of things like that: "Make an app with this GUI, it's so easy!"  Because when I want to do something new, and I don't understand the logic of the system, I feel like a pretender.  I'm building a house on a foundation of quicksand.

That's not to take a stab at any game developer or other engineer who doesn't have this hangup.  It's just my hangup.  I'm sure the vast majority of people who've made any of the games that my kid and I enjoy have never bothered making a ray tracer, and they're as good or better at the engineering game than I'll ever be.

## Challenges

I really struggle with math.  I had a fairly easy time with it as a child, then people said I was smart and naturally talented, so when I reached the point where it got challenging, I internalized the idea that I was dumb or didn't have a mind for it.  Shameful!  So I taught myself to avoid math.  

I only ended up getting through Calculus II, Discrete, and calc-based statistics, and that was at the age of 30 or so.  I never got to linear algebra, which is a fundamental building block of this technology.  I never took calc-based physics, either.  So I'm going in with a real gap in my fundamentals.

That said, I'm a human, and humans are learning creatures.  It'll be frustrating, but I think I have good resources at my disposal.  This book seems excellent from skimming the first couple of chapters, and I'm eager to dive in.

<!--
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

[^1]: This is incorrect; it is the seat of House Cuy, in the Reach.  I corrected it.  But holy crap, ChatGPT is amazing.
