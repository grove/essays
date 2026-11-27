# Software that improves with age

Five years into the life of an order management system, the team decides to support splitting a single order across multiple warehouses. The requirement is easy enough to explain. Yet everyone who has worked on the system knows what comes next: weeks of tracing assumptions scattered through checkout, invoicing, refunds, notifications and half-remembered workarounds for partners the company no longer uses.

By its fifth year, almost every successful software system feels heavier than it did in its first. Changes take longer to reason about, unintended side effects become harder to predict and experienced maintainers spend a growing share of their time protecting the system from its own history.

We have largely accepted this decline as an inevitable property of software, something closer to entropy than to a choice. It is worth asking how much of it is inherent to building software and how much is a consequence of how we have historically had to allocate engineering effort.

## Why software degrades

In his 1980 paper *Programs, Life Cycles, and Laws of Software Evolution*, Meir Lehman observed that a software system used in a real environment must continually adapt or grow progressively less useful, and that as it evolves its complexity increases unless deliberate work is done to maintain or reduce it.

For most of software engineering's history, that countervailing work has been hard to sustain. When writing code was the dominant cost of development, teams spent almost all of their capacity getting the next change into production. Boundaries were compromised to meet a deadline and rarely repaired afterwards. Tests verified the happy path of the feature just shipped rather than the invariants that mattered across the system. Obsolete code stayed in place because proving it safe to remove took effort nobody could spare. Design rationale lived in the heads of the people who wrote the code and walked out the door when they left.

Scarcity of implementation effort is only part of the explanation, however. Software also becomes harder to work with because the world it inhabits genuinely becomes more complicated. Over five years, the order management system acquires new tax jurisdictions, payment providers, fulfillment rules, regulatory audits and historical ledger records that cannot simply be rewritten. Cheaper implementation does not abolish that essential complexity.

What it changes is whether the accidental complexity layered on top of it has to grow unchecked alongside it.

## Two feedback loops

AI does not automatically make software age better. If anything, cheaper implementation acts as an amplifier on whichever feedback loop a team is already running.

Consider the decay loop first. When generating code becomes cheap and a team spends all of the time it saves moving faster down the feature backlog, accumulation speeds up. Half-understood requirements turn into production features before anyone has tested their assumptions. Agents faithfully preserve old partner workarounds during refactors and wrap them in tests that look thorough while merely mirroring the implementation. Feature flags, fallback paths and boilerplate pull requests pile up. Because nobody on the team wrote most of the recent changes, understanding erodes while the system's operational behavior drifts faster than an on-call rotation can track. Each month leaves both humans and agents working through thicker noise, which makes the next change slower to verify and riskier to delegate.

Now consider the opposite loop, where a team reinvests part of what cheaper implementation saves into the conditions under which future changes are made.

Before committing to a consequential requirement, the team runs cheap, throwaway experiments to discover what the software actually ought to do, as I described in [Discovering what software should do](./discovering-what-software-should-do.md), keeping speculative complexity out of the codebase in the first place. When routine changes repeatedly collide with high-consequence invariants, the team untangles the seam and enforces core guarantees mechanically ([Designing for delegation](./designing-for-delegation.md)). Instead of relying on unit tests generated alongside the code, it invests in independent properties, reference models and reconciliation checks ([Knowing what constitutes convincing evidence](./knowing-what-constitutes-convincing-evidence.md)). When production still surprises it, the incident is converted into a repeatable harness and clearer operational telemetry before the details fade ([Operating software you didn't write](./operating-software-you-didnt-write.md)). Obsolete workarounds and redundant state are investigated and staged out rather than left behind to confuse future sessions ([The economics of removing software](./the-economics-of-removing-software.md)). And between feature requests, bounded investigations examine guarantees that have never been tested under stress ([Continuous cultivation of software](./continuous-cultivation-of-software.md)).

Look again at the five-year-old order management system under this second loop. Its domain is no simpler than before; it still handles multiple payment providers, tax regimes and fulfillment rules. Yet its ledger invariants sit behind a narrow interface that pricing and promotion changes cannot bypass. Five years of real edge cases have hardened its reconciliation checks and concurrency harnesses rather than merely leaving scars in the code. Retired partner integrations have been removed once telemetry confirmed they were quiet, with brief notes recording why they once existed. When the split-shipment requirement arrives, the team can explore two candidate designs against realistic workloads before committing, and understand what it is changing without excavating four years of unrelated history.

The system has not merely accumulated features. It has accumulated clarity, evidence and restraint.

## What actually accumulates

It is tempting to imagine that software improves with age simply by accumulating more artifacts: more documentation, more tests, more dashboards, more generated summaries. Yet every artifact we add is also something that can drift out of sync with the system and mislead future work.

What actually makes a mature system easier to change than a young one is narrower and more durable.

First, structural fit improves. Early in a system's life, module boundaries are educated guesses about which decisions will change together. Over five years of real modifications and incidents, the real seams reveal themselves. A team that acts on those collisions ends up with boundaries shaped by actual pressure rather than speculation, and with its most consequential guarantees enforced by types, schemas and narrow choke points rather than tribal memory.

Second, verification grows closer to reality. A greenfield storage engine or order system has tests reflecting what its authors worried about on day one. A five-year-old system whose incidents and investigations have been folded back into crash harnesses, randomized property checks and external reconciliations embodies hard-won knowledge about how the real environment actually fails. That evidence is far harder to build from scratch than the production code itself.

Third, operational legibility deepens. The dashboards reflect the guarantees that matter, rollbacks have been rehearsed, stateful boundaries are clearly marked and the team knows how the system bends under real load.

Fourth, the engineers responsible for the system develop a sharper mental model of it. Rather than losing their grasp of the software as implementation is delegated ([Implementation and understanding](./implementation-and-understanding.md)) or spending their days reviewing agent diffs they had no hand in shaping ([When code review becomes the work](./when-code-review-becomes-the-work.md)), they spend more of their time investigating behavior, questioning requirements and strengthening guarantees.

A greenfield rewrite often looks cleaner than a five-year-old system only because it has not yet met reality. A well-cultivated mature system has met reality for years and absorbed those lessons into its structure and its checks without drowning in the residue of every past attempt.

## Where improvement with age breaks down

Calling this a positive feedback loop should not obscure how easily it stalls or reverses.

Some forms of complexity accumulate monotonically regardless of how well a team works. Persistent on-disk formats in a storage engine, historical financial records, external API contracts and regulatory obligations cannot be simplified away merely because writing code is cheap. A mature system will almost always carry durable commitments that a new one does not, and honoring them imposes real friction on change.

The machinery meant to sustain improvement can also become a new source of decay. A sprawling crash simulator that nobody understands, a generated knowledge base whose explanations quietly contradict the code, an alert suite full of stale thresholds and a stack of brittle property tests can all give a team the appearance of maturity while making ordinary changes harder. Verification instruments, specifications and boundaries need the same deliberate pruning as application code.

The deepest obstacle, though, is organizational rather than technical. Across every stage of the lifecycle, the same asymmetry shows up: new capabilities are visible on a roadmap, whereas the payoff from clearer boundaries, stronger verification and retired workarounds appears as delays that do not happen and outages that never wake anyone up. Improving the conditions of future work competes directly with shipping the next visible change, and its returns often arrive after the current planning cycle has ended.

Without an explicit decision to reserve effort for cultivation, simplification and verification, cheaper implementation will not bend a system's trajectory upward. It will simply let organizations hit the wall of accidental complexity sooner.

## Telling whether a system is getting better

Because accumulating tests and documents can easily look like progress even while a system is growing harder to change, teams need grounded ways to tell which loop they are actually in.

The most telling signals show up in ordinary work. When a team adds a routine rule in a volatile area of the codebase, does the change stay local, or does it still brush against core invariants? When an engineer or an agent investigates an unfamiliar subsystem, do they find explicit contracts and runnable checks, or a maze of undocumented special cases? When a production incident reveals a flawed assumption, does the system emerge a month later with a stronger check and clearer telemetry, or only with a narrow patch? Are retired flags and partner workarounds disappearing at roughly the pace new temporary code is introduced?

There is a human signal as well. Look at what the engineers responsible for the system spend their week doing. If cheaper implementation leaves them spending most of their time rubber-stamping large diffs, chasing flaky tests and untangling regressions in code nobody quite owns, the system is degrading regardless of how quickly pull requests are merging. If it leaves them spending more time investigating hard questions, testing competing designs, tightening boundaries and retiring complexity, the loop is working in the right direction.

Shifting from one trajectory to the other does not require halting feature development for a grand rewrite. Just as cultivation starts with one consequential guarantee and a modest weekly budget, improving a system's trajectory starts with dedicating a steady share of the time AI saves to the work that makes next quarter's changes calmer, clearer and easier to verify, and checking periodically whether ordinary development actually feels easier as a result.

## Better engineering, not just more software

Software that improves with age is neither automatic nor common. Nothing about faster code generation guarantees it, and a team that treats AI purely as a way to increase output should expect the opposite: systems that grow larger, noisier and harder to trust in a fraction of the time it used to take.

For decades, the cost of implementation set tight limits on how we practiced software engineering. We committed to designs before we could afford to test alternatives, settled for verification that confirmed our own assumptions, left obsolete paths in place rather than proving them safe to delete and treated growing complexity as the unavoidable price of keeping software useful.

Cheaper implementation gives us a chance to renegotiate that trade-off across the entire life of a system.

The most consequential opportunity AI presents to software engineering is not that we can afford to write more software, but that we can afford to practice better engineering. If we take that opportunity seriously, the measure of our success will not be how much code a team produced this quarter, but whether the engineers who inherit a system five years from now find it clearer, more trustworthy and easier to change than the day it first went into production.
