---
# A Hugo template for documents about personal programming projects.
#
# The title should be the name of a castle from the continent of Westeros, from
# George R. R. Martin's _A Song of Ice and Fire_ books.
title: "{{ replace .Name "-" " " | title }}"
date: {{ .Date }}
draft: true
# Categories:
# - Games
# - Apps
# - Libraries
# - ???
categories: []
# Languages:
# - CSS
# - Gherkin
# - Go
# - Go-Templates
# - HTML
# - JavaScript
# - Rust
# - SCSS
# - YAML
languages: []
# Tags:
# - Cloud
# - Design
# - Graphics
# - Hugo
# - Jamstack
# - Ray-Tracing
tags: []
# Keywords for search engines.
keywords: []
# Other paths that should also be routed to this content.  Normally not needed.
aliases: []
# ndouglas is my GitHub username.
# All three of the following fields should always be filled out.
repo_url: "https://github.com/ndouglas/{{ .Name | lower }}/"
# Where a live demo of this project is made available.
demo_url: "https://ndouglas.github.io/{{ .Name | lower }}/demo/"
# Where project documentation is made available.
docs_url: "https://ndouglas.github.io/{{ .Name | lower }}/"
# A percentage figure indicating my progress on the project.
progress: 0
# A very short subtitle with a phrase summarizing the goal of the project and
# the primary language or languages.
subtitle: 'A brief subtitle of the project.  This should be about ten words long and describe the project function and include the language in which it is programmed.'
---
A longer introduction to the project, from 2-3 short paragraphs.  This will appear "above the fold" and in listings of the project.

<!--more-->

## Summary

*Provide a brief summary of the project, including what it does and what technologies or tools you used to build it.*

### Naming

*Choose a castle from Westeros whose name has some synergy with what you are trying to accomplish with this project. Explain why you chose that name.*

## Motivations

*Explain what motivated you to pursue this project. This could include personal interests, career goals, or something else entirely.*

## Challenges

*Anticipate the challenges you will face over the course of the project. This could include technical hurdles, time constraints, or other obstacles. Be sure to outline a plan for how you will tackle these challenges.*

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
