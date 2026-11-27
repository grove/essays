# Software that improves with age

Five years into the life of an order management system, the team decides to support splitting a single order across multiple warehouses. The requirement takes two minutes to explain. Yet everyone who has worked on the codebase knows what the next few weeks will look like: tracing assumptions scattered through checkout, invoicing, refunds, notifications and old workarounds for fulfillment partners the company stopped using two years ago.

Almost every successful software system feels heavier in its fifth year than it did in its first. Small changes take longer to think through, side effects are harder to anticipate and the people who know the codebase best spend more of their time keeping old compromises from breaking.

Most of us treat that trajectory as a fact of life, like rust or wear. I think it is worth asking how much of it is inherent to software and how much is the result of what engineering teams could historically afford to do.

## Why software degrades

In his 1980 paper *Programs, Life Cycles, and Laws of Software Evolution*, Meir Lehman argued that a program in real use has to keep changing or grow progressively less useful, and that its complexity increases as it changes unless deliberate work is done to hold it back. Fourteen years later, in *Software Aging*, David Parnas described the same bind from two sides: software ages when it fails to keep up with a changing environment, and it also ages from the side effects of the changes made to keep it up to date. Parnas urged the profession to care more about long-term health than initial release, though he still treated aging as something to slow down or periodically repair rather than reverse.

In practice, the work that resists decay has always been hard to sustain. When implementation was expensive enough to consume most of a team's capacity, getting the next change into production won almost every argument. A boundary bent to meet a deadline stayed bent. Tests covered the paths the author had in mind when shipping the feature, not the invariants that mattered across the system. Old workarounds survived because proving them safe to delete took days nobody had. The reasoning behind hard decisions stayed in people's heads and disappeared when they moved on.

Implementation cost is not the whole story, of course. Software also gets harder with age because the world around it genuinely becomes more complicated. Over five years, an order management system picks up new tax rules, extra payment providers, regulatory audits and historical ledger records that cannot simply be rewritten. No tool is going to make that essential complexity disappear.

What can change is whether accidental complexity piles up alongside it, and whether five years of running a system makes the team more capable or merely more cautious.

## Two feedback loops

Cheaper code generation does not automatically give a team spare hours. Reviewing generated code, sorting out ambiguous requirements and verifying that changes actually behave as intended can easily absorb whatever time was saved writing lines of code.

What changes is which kinds of engineering work cross the line from impractical to routine. A disposable experiment comparing two designs, an independent crash harness or a systematic audit of a retired integration used to lose out to feature work because setting them up took days of manual coding. When that mechanical cost drops sharply, AI amplifies whichever feedback loop a team is already running.

When a team uses faster implementation mostly to push further down the feature backlog, decay speeds up. Half-understood requirements turn into production code before anyone tests the underlying assumptions. During refactors, agents faithfully carry old partner workarounds forward and generate tests that mirror whatever the code happens to do. Flags, fallback paths and verbose pull requests accumulate. Because nobody on the team wrote most of the recent changes, shared understanding thins out while the system's runtime behavior shifts faster than an on-call rotation can keep up. Each month leaves humans and agents working through thicker noise, which makes the next change harder to verify and riskier to delegate.

The alternative is a loop where improvements compound in the other direction.

Part of that work keeps unnecessary complexity out of the codebase in the first place. Running cheap throwaway experiments before committing to production code, as I argued in [Discovering what software should do](./discovering-what-software-should-do.md), lets a team find out which requirements actually matter before embedding early guesses into the system. Between feature requests, [continuous cultivation of software](./continuous-cultivation-of-software.md) puts agents to work probing guarantees that nobody has tested yet, while incidents feed back into permanent reproductions and clearer telemetry rather than stopping at a quick patch.

What turns these from a list of good habits into a genuine feedback loop is that each improvement lowers the cost of making the next one. Stronger independent verification makes deleting obsolete code and simplifying internals safe instead of frightening, shifting [the economics of removing software](./the-economics-of-removing-software.md). Removing dead workarounds and redundant state shrinks what humans and agents have to read, which makes the next investigation cheaper and less prone to error. Clearer, mechanically enforced boundaries keep routine edits local, reducing the review burden and making delegation safer. That leaves engineers with more room to investigate hard problems instead of spending their week inspecting diffs.

Go back to the five-year-old order management system, this time after five years in the second loop. Its business rules are just as intricate as before: multiple payment providers, regional tax laws, real accounting constraints. Yet pricing and fulfillment logic sit outside a narrow ledger interface whose checks they cannot bypass. Five years of edge cases have gone into randomized concurrency tests and nightly settlement reconciliations rather than into fragile special cases scattered across services. Retired partner code was instrumented, confirmed quiet and removed, with a short note explaining why it once existed.

When the split-shipment requirement arrives here, the team does not spend weeks excavating forgotten branches. It can prototype two ways of representing partial fulfillments against the existing ledger boundary and run both through the reconciliation and concurrency harnesses. If splitting a shipment across two warehouses breaks how partial refunds settle when one warehouse dispatches and the other cancels, the harness surfaces that interaction in an afternoon rather than in production.

The system has not merely accumulated features. It has accumulated clarity, evidence and restraint.

## What improving with age actually means

A five-year-old order management system with ten payment providers and three years of historical ledger data will not be simpler in absolute terms than a first prototype with ten endpoints. It carries obligations its younger self never had. Improving with age does not mean every change becomes trivial; it means age begins to confer advantages a young system cannot have, so that five years of operating the software becomes an engineering asset rather than primarily a liability.

It is easy to mistake that for piling up artifacts: more documentation, more generated tests, more dashboards, more wiki pages. Every artifact we add can drift out of date and mislead whoever reads it next. What genuinely improves with age is narrower and harder to fake.

In a young codebase, module boundaries are guesses about which parts of the problem will change together. After five years of real requests and real incidents, the seams are no longer guesses. A team that reshapes its code where changes repeatedly collide, the approach I explored in [Designing for delegation](./designing-for-delegation.md), ends up with boundaries grounded in experience and with its hardest guarantees enforced by types, schemas and narrow interfaces rather than by tribal memory.

Verification matures in the same way. A new storage engine or order system only tests what its authors thought to worry about on day one. Five years in, a system whose outages and investigations have been folded back into crash harnesses, property checks and external reconciliations embodies the independent evidence I discussed in [Knowing what constitutes convincing evidence](./knowing-what-constitutes-convincing-evidence.md): hard-won knowledge about how disks, networks, payment gateways and real users actually misbehave. That body of evidence is far harder to recreate from scratch than the application code itself.

Operations mature alongside it. As I argued in [Operating software you didn't write](./operating-software-you-didnt-write.md), telemetry that reflects real guarantees, rehearsed rollbacks and clear boundaries around stateful changes turn midnight incidents from guesswork into manageable recovery. Just as important, the engineers responsible for the software keep a working grasp of it. Instead of losing their mental model as coding is delegated, the risk I examined in [Implementation and understanding](./implementation-and-understanding.md), or letting their job shrink to approving agent output as in [When code review becomes the work](./when-code-review-becomes-the-work.md), they spend more of their time exploring how the system behaves, questioning requirements and strengthening what protects it.

A greenfield rewrite looks clean mostly because it has not yet met reality. A well-cultivated system has met reality for years and absorbed those lessons into its structure and its checks without drowning in the residue of every past attempt.

## Where this breaks down

None of this is guaranteed, and some parts of software really do harden with age no matter how disciplined a team is.

On-disk storage formats, public APIs with outside consumers, historical financial records and regulatory commitments accumulate in one direction. You can rewrite a pricing engine behind a clean interface, but you cannot casually simplify away a file format or a billing contract that external systems depend on.

The machinery built to keep a system healthy can rot too. An overgrown crash simulator nobody fully understands, a generated knowledge base whose claims quietly contradict the code, an alert suite full of stale thresholds and brittle property tests that keep breaking on benign refactors all look like maturity while slowing every change down. Verification harnesses, specifications and boundaries need the same willingness to simplify and delete as production code.

The hardest obstacle, however, is organizational. Across every part of the lifecycle, the same imbalance shows up: new features are visible on a roadmap, whereas the return on tighter boundaries, stronger harnesses and deleted workarounds appears as delays that do not happen and outages that never wake anyone up. Investing in the conditions of future work competes directly with shipping the next visible request, and its payoff often arrives well after the current planning cycle ends.

Unless a team explicitly reserves effort for cultivation, verification and removal, cheaper implementation will not improve how its software ages. It will only accelerate the default.

## Telling which loop you are in

Because generated tests and tidy documentation can make a deteriorating codebase look healthy from a distance, the signs that matter are the ones observable in ordinary work. Look at comparable changes in volatile parts of the system over time: do they stay inside a single module, or do they still spill into core invariants? Look at how long verification takes for a routine change, and whether a failure class that caused an outage six months ago stays gone instead of reappearing in a slightly different guise. Pay attention to how quickly someone unfamiliar with a subsystem can trace a guarantee and run a meaningful experiment against it, and whether temporary flags and partner shims are retired at roughly the pace new ones go in.

These are useful as diagnostic evidence for the team, not as management targets. The moment "flags deleted per quarter" or "time to verify" turns into a performance metric, both people and agents will find ways to optimize the number while hollowing out the reality behind it.

Watch how the engineers spend their week, too. When a team is stuck in the decay loop, its senior people spend their days skimming oversized pull requests, nursing flaky tests and patching regressions in code nobody quite owns, even while merge counts climb. When the improvement loop is working, more of their time goes into investigating hard questions, testing competing designs, sharpening boundaries and clearing out old complexity.

Moving from one loop to the other does not require pausing feature work for a rewrite. Just as cultivation begins with a single guarantee and a modest weekly budget, changing a system's trajectory starts with setting aside a steady share of engineering effort for the work that makes next quarter's changes safer to verify, then checking those signals a few months later to see whether it is paying off.

## Better engineering, not just more software

Software that improves with age is rare, and nothing about better models will produce it on its own.

For decades, the cost of implementation set narrow boundaries on what most teams could practically do. We committed to designs before we could afford to test alternatives, settled for checks that mostly confirmed our own assumptions, left obsolete paths sitting in active code rather than proving them safe to remove and accepted steady deterioration as the unavoidable price of keeping software useful.

The most consequential opportunity AI presents to software engineering is not that we can afford to write more software, but that we can afford to practice better engineering. If we take that opportunity seriously, the real test of our work will not be how much code a team shipped this quarter, but whether the engineers who inherit a system five years from now benefit from its accumulated experience instead of fighting its accumulated history.

