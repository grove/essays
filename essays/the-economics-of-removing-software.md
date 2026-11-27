# The economics of removing software

Four years ago, an order management system acquired a workaround for a warehouse partner that could only report dispatches in a nightly batch file. That partner was replaced two years ago. Yet the batch-reconciliation job, its retry tables, its special cases in the cancellation logic and its tests are still in the codebase.

Every time someone changes how orders are cancelled or refunded, those paths have to be understood, preserved and worked around. Nobody asks for them to be removed because removing them is not on the roadmap, and nobody is entirely certain whether some obscure reporting script still reads the retry table.

As AI makes adding software cheaper, the imbalance between what we add and what we remove becomes harder to ignore.

## The asymmetry of accumulation

Even before AI, software grew much more readily than it shrank.

Adding a feature or a special case is usually local and immediately justified by a customer request or a bug report. Removing code requires a different kind of work: proving that nothing still depends on it, checking edge cases across integrations and accepting responsibility if a quiet consumer breaks.

In [Discovering what software should do](./discovering-what-software-should-do.md), I noted that the ongoing cost of having built the wrong thing does not disappear just because it was cheap to build. Every feature, flag and fallback path remains part of the system that future engineers and agents have to take into account.

When implementation becomes dramatically faster, this asymmetry sharpens. Teams can add new capabilities, compatibility layers and defensive workarounds at a pace that quickly outstrips their habit of cleaning up what is no longer needed. Left unchecked, cheaper code produces larger, denser systems that become steadily harder to reason about and verify.

## What AI makes cheaper to remove

The encouraging side of this shift is that the same capabilities that make agents useful for adding code also lower the practical cost of removing it.

Much of what makes deletion laborious is investigative work. Before removing the nightly warehouse batch path, someone has to trace every caller, check database queries and scheduled jobs, inspect production logs to see whether the path has been executed in the past year and verify whether any downstream reports depend on its tables.

An agent can do much of this legwork quickly and produce a structured account of what depends on the code and what does not. It can also handle the mechanical work of migrating remaining callers to a cleaner interface, removing obsolete configuration and updating tests once a decision has been made.

The same applies to internal simplification. In [Continuous cultivation of software](./continuous-cultivation-of-software.md), I gave the example of a storage engine tracking its latest completed checkpoint in two places, a persistent manifest and separate recovery metadata. Investigating whether one authoritative representation suffices, testing the simpler design against a crash harness and migrating away from the redundant state used to be the kind of cleanup that stayed on a wish list for years. Now it is far easier to test whether a simpler design holds up.

## Why deletion remains hard

If the technical effort of removal is falling, why do obsolete paths still linger?

Most of the remaining obstacles are social and organizational rather than technical. Keeping an unused branch feels safe; deleting it feels risky. If an unused fallback stays in place for another three years, its cost is diffuse and largely invisible, spread across every future change as slightly slower reviews and slightly more complex tests. If deleting it breaks one forgotten script, the failure is immediate and attributable.

AI introduces a subtler obstacle as well. Agents are typically instructed to preserve existing behavior and keep all tests passing. When an agent refactors a subsystem or adds a feature, it tends to treat old workarounds as sacred requirements, faithfully migrating dead code, preserving obsolete flags and writing new tests to lock them in. Unless humans explicitly question whether old behavior is still wanted, agents will carefully maintain our past mistakes indefinitely.

## Practicing deliberate subtraction

Removing software reliably requires treating subtraction as regular engineering work rather than an occasional heroic cleanup.

Start by separating the investigation from the deletion. An agent can be assigned to establish whether an old restriction, compatibility layer or unused feature still earns its keep: where it is referenced, whether production telemetry shows any real usage and what would be involved in retiring it. As with other investigations, the outcome might be a documented reason to keep it. That too is useful, because it replaces superstition with evidence.

Where uncertainty remains, make removal reversible and observable. Add logging or metrics to a suspected dead path for a few weeks before removing it, retire it behind a switch or delete it in a small, isolated change that is easy to revert. Good verification instruments and clear module boundaries make subtraction much safer, because they let us confirm that core guarantees still hold after the code is gone.

Most importantly, measure and recognize simplification. If an organization only celebrates features shipped and lines added, engineers will rationally spend the time AI saves them adding more software rather than improving what they already maintain.

## Keeping software small enough to understand

Every piece of code we remove reduces the context that humans and agents must carry to work safely in the system. It eliminates states that no longer need to be tested, interactions that no longer need to be explained and assumptions that can no longer go stale.

When writing code was expensive, restraint came partly from friction: we simply could not build everything we thought of. As that friction fades, restraint has to become deliberate.

The nightly warehouse batch path in the order management system is rarely urgent on any given day. Yet regularly finding and removing code like it may do more to keep a system healthy, understandable and adaptable than any single feature we add.
