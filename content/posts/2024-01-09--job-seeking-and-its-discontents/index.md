---
title: "Job-Seeking and Its Discontents"
date: 2024-01-09T14:33:59-05:00
draft: false
type: 'post'
---
So I'm once more looking for a job, and something just keeps sucking all of the joy and hope and optimism right out of me. It's not so much that I might submit a résumé and not hear back, or eventually be rejected. It's the process of actually crafting a résumé and a cover letter.
<!-- more -->
It occurred to me recently that every time I've been hired, I believe I got my résumé directly into the hands of a lead engineer on the project I ended up on. I've never successfully gone through HR or a hiring manager or "People Ops."

## Backstory

Last year, I started to feel a bit tired at my current role. I applied to two positions, at companies that are not household names _per se_ but would be immediately recognized by anyone in a DevOps/PE/SRE role. I was rejected fairly quickly. I was a bit hurt. Not at the rejection itself, but the speed of it. They seemed to know immediately, just from a casual glance at my résumé, that I would not be a good fit.

I've led hiring efforts before; I've read thousands of résumés. I've had those days where I read so many résumés that I had to consciously develop coping strategies in order not to shortchange candidates. 

I had crafted my résumé with that experience in mind. I kept it brief; I listed 3-4 job duties and accomplishments for each of my roles. I had an odds-and-ends section at the end for things that spanned my career (Linux, Bash) or things that I love but have no professional experience with (Rust).

This, according to everything I've read, was A Bad Move™. And indeed, I was rejected quickly, almost immediately.

It stung a bit, but I didn't think much more about it. After all, I was very happy with my employer (although past tired of my specific project and my role on it). I was promoted to Tech Lead. Things went about as well as they could have for six months.

## Oh, Just Quantify _Everything_

In December, though, we lost our recompete and the future seemed very uncertain. Remembering those rejections, I immediately purchased The Whole Shebang™ from a résumé-writing service that will remain nameless here but seems to be well-known and decently well-regarded. My résumé, rewritten by someone with knowledge of and experience in the field, with a consultation, a cover letter, etc.

At first, it was kind of exciting; now I'm in good hands, someone knows what they're doing, maybe I can increase my earning power, etc. And after a consultation and a couple drafts, I was left with something that seemed more marketable. "Marketable" is a loaded term here. It felt a bit disingenuous.

I uploaded the résumé to another site, which does some sort of AI-based critique, and it received a fairly wretched score. Some of its critiques were valid and insightful.

The main thrust, though, seemed to be that _not every_ impact I made was quantified. I didn't have a "reduced by 30%" or "increased by 30%" or a dollar amount or a solid number of hours on _everything_. And this was where I started to feel discouraged and disgusted by the whole thing. I continued and refined a third version of my résumé until the AI said it was near-perfect, and by the end I found the whole process repulsive.

The core problem I see is the need to quantify _everything_.

- Introduced _some process_, reducing CFR by 25%
- Spearheaded _some change_, shortening MTTR by 15 minutes
- Created _some tool_, improving team sprint velocity by 15%

It's all bullshit. If this were a clinical study, I would be Wakefielded out of the profession. I feel a normal, sane engineer would laugh in my face. 

- "You had a good measure of CFR when you had four teams touching the same code, not to mention third-party dependency updates, not to mention various elements of your infrastructure being managed by other teams? How exactly do you define CFR in your scenario? How do you measure it? Do you annotate individual failures and determine responsibility and disposition? Or did you just make up a number?"
- "Where did you get these MTTR figures? How do you know this change was responsible for the improvement, and not simply that you got good at out-of-band deploys because you were doing so damned many of them?"
- "Yeah? So you had a stable team sprint velocity for a few weeks to act as a control, right?"

This frustrates me. It's dishonest to pretend that there's any sort of valid basis for making these claims. And, to be clear, the AI service trying to quantify everything is just what pushed me over the edge a bit. The résumé-rewriting service, and the writer I partnered with, pushed hard for the same thing, despite being human. But that's not how, in my experience, things actually work. There are many engineers changing things at the same time. The control, the stability needed to make any sort of pronouncement is simply illusory.

Is this all just bullshit? Are we just agreeing to play a pointless little game? Is artifice a soft skill now? Or do people really believe that my project has its shit together to the extent where we're not just producing and delivering quality software in a timely fashion, but we're doing it so well that we're performing controlled experiments?

Yes, _of course_ I have a forthcoming whitepaper about each of the claims on my résumé :moyai:

## The Trifontic Man

So now I have three résumés:

- my initial, honest version, one page, which quantifies a couple of things that I actually had some clarity and insight into, and outlines some major impacts.
- my professionally-written version, two pages, which quantifies several things with questionable statistical validity and some fudging, and outlines more major impacts.
- my AI-judged and repetitively-tweaked version, two pages, which quantifies damn near everything, is statistically nonsense, and outlines the same impacts as the professionally-written version.

I haven't yet sent out my second or third versions. I'm not sure if I ever will. I spent hundreds of dollars because I was convinced that I needed to market myself better, and because I was afraid I wouldn't be able to find a new gig. 

But now I think that any place that would interview 2nd-Résumé Me or 3rd-Résumé Me, and pass on 1st-Résumé Me, is probably somewhere I don't want to go!

How do I determine which is the better résumé? Can I do A|B testing with résumés? Can I do A|B testing with the rest of my career?

## Unqualified Impact

I reviewed a coworker's résumé last year, after he'd moved to another position elsewhere. He had a quantified impact on one of his items. It was a significant impact. It looked great on paper. 

And I had to work several tickets to deal with the fallout from that item, to clean up after it after he had made his impact and left.

He had seen an opportunity and taken it. It seemed like an obvious way to make an improvement. And it was. By changing a couple of lines of YAML, tests were parallelized. The time taken to run the full battery of tests was diminished substantially. Most of the team rejoiced, and my explanation as to why we hadn't done this stupidly-simple thing before was not noted. It probably sounded a bit like sour grapes.

It had negative impacts that were far harder to quantify than a simple drop in test execution time:
- our tests had not been written to run in parallel, so flakiness and failures due to flakiness shot through the roof; instead of running a reliable battery of tests that took an hour to run, we now ran a battery of tests that took 40 minutes to run, but would fail half the time.
- our product was not configured to support this many operations in parallel, with caches being cleared and acted upon simultaneously, so we started seeing deadlocks, etc.
- our CI server was not sized to handle multiple test batteries running in parallel, so load and memory usage spiked, causing performance issues, causing test failures, causing engineers to angrily rerun tests, etc

Now, this isn't to say my coworker was wrong to do what he did. After all, I'd been wanting to do that thing for a year and hadn't accomplished it. Perhaps it would still be in limbo if he hadn't moved fast and broken things.

But the fact remains that these simple résumé items, like "parallelized tests, reducing test battery runtime by 33%" can be (and probably often are) incomplete, misleading. I wonder if they're followed up on.

## Perverse Incentives

At some point in my despair, I thought, "well, that should teach me. By $DEITY, I am going to seek out impactful tasks in my next job so that I can have a great résumé and get the jobs I want."

And this, uncomfortably, reminded me of an exchange I'd had with Tom, a graybeard at my current employer, in a hiring process. He was, I felt, discriminating against engineers with multiple two-year stints at their previous jobs. "What this tells me is that they make a lot of changes and they don't have to stick around and deal with the effects."

Outrageous! I don't fit this pattern (I've spent 4 years, ~5 years, and 3+ years at my respective employers), but I'm still aware of the reality of the marketplace. The only way most engineers – most workers – get a raise is by switching workplaces or at least job titles. And it seems that staying too long at a given workplace has its own stigma, an aura of complacency and narrowness and staleness.

But it seems to me that along with the risk of stagnation comes the likelihood of wisdom. With repeated brief tenures, and a "move fast and break things" mindset, you can avoid internalizing the wisdom of Chesterton's Fence – that you shouldn't make a disruptive change without fully understanding why things are the way they are, and why that change hasn't already been made. You may never reach second-order thinking, of thinking about not just the consequences but the consequences of the consequences.

## Conclusion

As is often the case, as will probably become increasingly apparent if there is more to this blog, I'm left confused, upset, hurt, even deeply bewildered.

I have two résumés that I don't want to use that I paid a decent chunk of money for. I suppose I could run them by companies that hire with hiring managers and internal recruiters, but it still feels dirty. I have a résumé that feels clean and honest to me, but that doesn't seem to get a whole lot of interest.

I should probably consult other DevOps engineers and steer clear of commercial services, but I feel like many or most of them are operating in the same fog that I am.
