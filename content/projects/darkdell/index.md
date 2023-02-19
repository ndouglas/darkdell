---
title: "Darkdell"
date: 2023-02-18T10:38:27-05:00
draft: false
categories:
  - Websites
languages:
  - CSS
  - HTML
  - Go Templates
  - JavaScript
  - SCSS
  - YAML
tags:
  - Cloud
  - Design
  - Hugo
  - Jamstack
keywords: []
aliases: []
repo_url: "https://github.com/ndouglas/darkdell/"
demo_url: "/"
docs_url: "/projects/darkdell/"
progress: 0
subtitle: 'A statically-generated website built in Hugo.'
---
I started using HTML almost 30 years ago, but my interests drifted over time.  I didn't keep up with CSS and only used JS sporadically over the years until Node became a thing.  This website/blog/portfolio is an exercise in revisiting web technologies and exploring what I've missed.

Aside from the actual mechanics of generating the build products, I wanted to do as much as possible myself.  That means starting from a clean slate and writing all of the HTML, CSS, and JS myself.

So yes, the site is barebones and minimalist, but I have good odds on understanding what is happening at any point in time and how to accomplish the changes I want to make.
<!--more-->

## Motivation

### The VA.gov Content-Build Process and Its Discontents

My day job (as of February, 2023) is at [Agile Six](https://agile6.com/), working on the [VA.gov](https://www.va.gov/ "Department of Veterans Affairs") Modernization Project.  There's a lot of backstory going back several years, but the **TL;DR** is that we have a regular content build based on Node/Metalsmith/Liquid that retrieve content from a Drupal 9 backend via GraphQL and generate static HTML files that are then copied to and served from an AWS S3 bucket.

Again, there's a significant amount of backstory here, and the individual choices along the path have been made with good intentions and were probably the best available paths at the time.  We've also attempted to replace the frontend component of this solution on at least two occasions that I'm aware of in the time that I've been on the project, but various factors outside our control have prevented this.

But, ultimately, the issue remains that we have a 40+ minute build process.  It's fragile, breaking at least a couple times a week, generally due to infrastructural issues rather than inadequately tested code.  The CI test runs themselves take around 40-45 minutes because the site is built from scratch during tests, alongside the normal linting, unit/behavioral tests, etc.

The latest development that I'm aware of is that we're considering recoupling the site; disposing with the content build completely and exposing Drupal directly to the public Internet.  I'm not thrilled with this solution, but with the additional content burden of internationalization/localization on the horizon, I do think it's likely to be a massive improvement over the content-build system as it exists currently.

The fundamental problem, as I see it, is that we've "decoupled", but we've not actually moved away from the traditional LAMP application server model in any meaningful sense.  There's still a webserver, the most easily scaled component, serving all the requests, but the application server is pounded mercilessly every 30-45 minutes and its performance issues beget the performance issues of the process as a whole.

My inclination would be to have a system that renders HTML using Twig when a node or other entity is saved.  These would then be synchronized to S3 on a semi-continuous basis.  Of course, this incurs its own burdens; if a change affects all 300,000 pages (a casual estimate for the number of localized pages we're likely to have), then the entire site will effectively need to be rebuilt from scratch.

But if we were to do something like generate a Hugo template for the content on save, and then use Hugo to build the generated contents, and sync the results instead... that might be very fast indeed.  Even for a total rebuild.  I don't know how representative these results are, but [one discussion](https://discourse.gohugo.io/t/page-generation-performance-expectations/1335/7) mentioned a build time of 15 minutes for 600,000 pages.

And again, we would be generating the actual content on node save, so I think we could bypass the application server almost entirely during content build.  This is important, since content is actually changing almost continuously during business hours, whereas the pace of development on templates is considerably slower; only a few changes a day, most highly localized.

There are still some remaining questions, like partial builds and performance, etc.  I don't know that this is a viable solution for our current woes, and I'm not inclined to champion it until I have more in-depth knowledge of the system, but it seems tantalizing to me.

### Joomla, Wordpress, and Drupal: A History of Heartbreak

I made websites before CMSes were a thing -- before I knew much of anything about programming, really.  And -- disclosure time -- I have ADHD like whoa, so my interests and pursuits from day to day tend to follow a sort of binge-and-purge pattern.  The last thing I want is to have to do continuous security updates on my blog.  I do that at work, and it sucks.

(I'm actually trying to avoid the word "blog".  To me that implies some semi-regular ongoing post activity, and let's be honest, that's never happened in my life and is not going to start happening now.)

That said, I want _some_ sort of web presence.  I'm avoiding social media now, except for LinkedIn (which I loathe, but career).  I rely mostly on GitHub, but there's only so much I can do with my "[special repository](https://github.com/ndouglas/ndouglas/)".  I want to be able to meaningfully showcase my projects, my reading, etc.

I've actually been using Hugo on-and-off for a few years.  I've used it to plan out some writing projects (which never really materialized).  I've had my share of inefficient templates (to hack in a sort of relational database featureset).  While I always forget the fine points after a few months away, it's simple enough that I can jump right back in after a little reading.

So, basically, if you happen to read the source for any of my templates and they're _very_ heavily commented, it's because I _will_ forget what I was doing in that spot and need to marshall the full resources of the internet and shove them into a comment tag just to keep functioning.

And no database updates.  No separate assets to manage.  No usernames and passwords.  Just AWS credentials for deployment, which aren't kept in the repository and are managed through a separate system altogether.  It's thrilling :star_struck:

### Documenting What I Learn

I've forgotten more than I'll ever know about computing :weary:

I'd like to think I have a good few decades left in my career, but up until now I've relied on my memory and ability to learn quickly.  Realistically, I need to strategize for the years ahead, and build a solid system for referencing my own solutions.

A friend and coworker has mentioned that he uses the internet as a mind map, and I certainly find his notes to himself scattered around GitHub, Drupal.org, StackOverflow, etc more frequently than I'd expect.  I do that already, to some extent, but I also hate opening issues on GitHub to rubber-duck a problem.  I'm a little too hesitant to use the internet as my notepad.

Plus, the internet has a nasty habit of losing things you value.  "The internet is forever" only if it's something that you personally desperately want removed.  If it's a useful resource, its lifespan is very limited indeed.  And with (IMHO) Google search becoming dramatically less useful over the years, it's worth asking if it even _matters_ if it exists somewhere, if you can't find it.

## Challenges

### Time

Time is the biggest challenge in building this.  Not time for maintenance, of course, since this approach largley dispenses with maintenance.  But rather than starting with a theme developed by someone else, I have to build this thing from scratch.  I'm intimidated by design and accessibility concerns, but I also want to do this well.  So this involves a lot of research and learning new things in areas that I don't find intrinsically motivating.  And I frankly don't know if anyone else will ever see this, so just doing _anything_ is a little extra difficult.

## Approach

I guess I'm kicking it old-school here; just adding things as I think of them :shrug:.  I don't really have a grand vision of this thing other than that I'll be able to share some relatively meaningful summaries of the projects I'm working on as I start them.
