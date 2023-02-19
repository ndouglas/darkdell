---
title: "{{ replace .Name "-" " " | title }}"
date: {{ .Date }}
draft: false
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
# - Go Templates
# - HTML
# - JavaScript
# - Rust
# - Sass
# - YAML
languages: []
# Tags:
# - Cloud
# - Design
# - Graphics
# - Hugo
# - Jamstack
# - Ray Tracing
tags: []
keywords: []
aliases: []
repo_url: "https://github.com/ndouglas/{{ .Name | lower }}/"
demo_url: "https://ndouglas.github.io/{{ .Name | lower }}/demo/"
docs_url: "https://ndouglas.github.io/{{ .Name | lower }}/"
progress: 0
subtitle: 'A brief subtitle of the project.'
---
A longer introduction to the project, about a paragraph.
<!--more-->
