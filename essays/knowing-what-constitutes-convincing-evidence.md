# Knowing what constitutes convincing evidence

Suppose an AI agent changes how a storage engine writes checkpoint metadata and accompanies the pull request with a thorough suite of crash-recovery tests. Every test passes. A month later, under production load, a power loss during checkpointing leaves the engine unable to recover.

When we investigate, we find that both the implementation and the tests assumed renaming a metadata file makes it durable without calling `fsync` on the parent directory. The tests exercised the code carefully and simulated restarts at dozens of points, yet they could never have caught the bug. They were built on the same mistaken belief that produced it.

This is an old failure mode in software engineering, made much more common by AI. When writing tests took noticeable effort, a comprehensive test suite usually implied that someone had spent time thinking through the problem. Now an agent can produce hundreds of lines of tests alongside an implementation in a few seconds. Producing checks has become cheap; judging what a passing check actually proves has not.

## Why passing tests deceive

Anyone who has written a piece of code and then written unit tests for it knows how easy it is to confirm your own assumptions. You test the cases you thought of, through the interfaces you just designed, under the mental model that led you to write the code that way in the first place.

AI makes this circularity faster and harder to spot. Ask an agent to implement a feature and make sure it is well tested, and it will generate a large, tidy test suite with high line coverage and reassuring names. Look closer, though, and many of those tests simply mirror the implementation line by line. When an agent writes tests for existing code, it often asserts whatever the code happens to do today, turning incidental quirks and old workarounds into what looks like an intentional contract.

Mocks are often blamed for this, though the usual complaint misses the sharper point. A mocked payment gateway in an order management system can certainly simulate a duplicate webhook, an out-of-order event or a timeout after a charge succeeds, provided someone remembers to script those cases. The deeper problem is that a mock only ever exhibits the failure modes the author already imagined. It will never surprise your code with an undocumented status transition, an unusual retry cadence or a malformed payload that the real gateway only sends under load.

Splitting the work across separate prompts or sessions helps, because a single pass tends to resolve every ambiguity in our instructions the same way across both code and tests. Even that has limits. Two separate sessions using the same model often share the same training habits and blind spots; forgetting that POSIX `rename` needs a directory sync is exactly the sort of assumption two independent runs can make in parallel.

There is also a subtler problem once tests are genuinely separate. Agents are persistent about making checks turn green. Given a fixed suite of tests it did not write, an agent can still satisfy the literal assertions while violating the intent behind them: special-casing an input from a fixture, swallowing an exception so a retry loop finishes or loosening a timeout until a flaky check stops failing. Once a test suite becomes the main target an agent optimizes for, its value as evidence starts to erode unless the checks are hard to game.

## Different kinds of evidence

In [When code review becomes the work](./when-code-review-becomes-the-work.md), I argued that we should spend less time reading individual implementations and more time building durable verification instruments. That trade only pays off if we are clear about what different kinds of evidence can and cannot rule out.

The strongest evidence often does not look like a test at all. In [Designing for delegation](./designing-for-delegation.md), I wrote about enforcing core invariants structurally, through types, narrow choke points or database constraints. If an inventory table enforces at the database level that reserved stock can never go negative, we do not have to hope a test suite happened to hit the right concurrent cancellation sequence. An entire class of failure is ruled out by construction rather than by sampling.

Where structural guarantees stop, we fall back on dynamic checks, and independence from the implementation matters most. Instead of testing internal helper calls, we want to check external properties that must hold regardless of how the code is written. In the order management system, a customer who cancels an order while a shipment confirmation is in flight should never end up both charged and without an item, and reserved inventory should always return to available stock if fulfillment fails. Driving those properties with randomized sequences of retries, concurrent requests and interrupted handlers makes it much harder for an implementation to pass by accident or by fitting itself to a handful of fixed examples.

Comparing a complex implementation against a simpler source of truth gives another kind of leverage. For a storage engine, running the same randomized sequence of reads, writes and snapshots against both the real engine and a small, obviously simple in-memory reference model routinely uncovers edge cases in compaction or visibility rules that no example-based test would have checked. Because the reference model is written for clarity rather than throughput or disk layout, it is far less likely to share the bugs of the real engine.

Reconciliation against an external system belongs in a different category. Comparing our order ledger nightly against the payment provider's settlement files or the warehouse's dispatch records does not stop a bug from shipping. It is detective evidence rather than preventive evidence, and you would not rely on it alone for a change that can corrupt data irreversibly. Its value is that it draws from a system we did not write and cannot accidentally mock into agreeing with us.

Some of the things that matter most resist formal verification altogether. No invariant or reference model will tell you whether a revised checkout flow confuses customers, or whether a search ranking feels reasonable on messy real queries. Treating those questions as settled because the automated checks passed is its own kind of self-deception. They require watching real usage, rolling changes out gradually or trying the software yourself.

## Testing the check, and testing the model

A passing check tells us very little until we know what would make it fail.

When an agent writes a crash-recovery harness or a property-based test, it is easy for a small flaw in the harness to make the test look thorough while checking almost nothing. The simulated crash might fire before the interesting state transition rather than during it. A startup cleanup routine might quietly discard a corrupted metadata file and mask the loss. An assertion might verify that the engine restarted without error while never checking whether every acknowledged write survived.

As I described in [Continuous cultivation of software](./continuous-cultivation-of-software.md), a straightforward way to challenge a verification instrument is to introduce deliberate faults into an isolated copy of the system and see whether the checks catch them. Remove a flush, allow an inventory reservation to be released twice or skip a checksum check; if the suite stays green, you have learned something concrete about what your evidence does not cover.

Notice, though, what deliberate fault injection cannot do on its own. Return to the opening example: if neither the engineer nor the agent knew that renaming a checkpoint file requires syncing the parent directory, nobody would think to inject "omit the parent-directory `fsync`" as a fault either. Fault injection tests whether your harness catches failures inside the fault model you already have. It cannot reveal failures your model leaves out.

Every simulator, mock and test harness encodes assumptions about the environment it stands in for: how a filesystem reorders writes, how a kernel behaves on power loss and how a payment gateway times out under load. Testing the harness has to be paired with testing the model itself against reality. That means periodically exercising durability protocols on real filesystems and real crash mechanisms, running integration checks against actual partner sandboxes rather than local stubs and treating every production incident as evidence that some assumption in our verification model was wrong.

## Where verification breaks down

Treating independent verification as the answer to every review bottleneck creates its own traps.

Verification code is still code, and it is not inherently easier to review than production code. If an agent produces two thousand lines of custom crash simulator and property generators to validate a three-hundred-line change, an engineer who skims the harness and trusts the green checkmark has only moved the blind spot one layer up. Good verification usually has to be noticeably simpler than what it checks, or anchored to something outside our control. When the harness becomes as intricate as the system under test, we should be suspicious of both.

Evidence also decays. One appeal of investing in a crash harness or a reconciliation job is that its cost is spread across many future changes, unlike brittle unit tests that have to be rewritten whenever internals shift. That only stays true while the instrument remains connected to reality. Cloud storage semantics change, payment providers alter webhook behavior and refactors quietly reroute traffic around a path a harness still thinks it is exercising. Left unattended, yesterday's convincing evidence turns into today's false comfort.

Independent specifications and reference models also assume we already know what the software should do. In a part of the system where we are still figuring out the problem, as I discussed in [Discovering what software should do](./discovering-what-software-should-do.md), locking down elaborate verification too early mostly hardens our first guesses and slows down learning.

## Proportionate evidence

Not every change calls for a deterministic simulator or an in-memory reference model. Demanding the same standard of proof for every modification would grind ordinary work to a halt.

That much is easy to agree on when comparing extremes: a wording fix in an administrative tool does not need the same scrutiny as a change to checkpoint durability. The harder problem sits in the middle, where a change looks harmless and turns out not to be. An innocent adjustment to an administrative report adds an unindexed query that locks a hot table; a small helper tweak accidentally bypasses a tenant filter. Saying that evidence should match the consequence of being wrong only helps if we have some reliable way of knowing what a change can reach.

This is where architecture and verification meet. When high-consequence guarantees sit behind narrow, mechanically enforced boundaries, a routine change to an isolated display or formatting module genuinely cannot touch them, and light verification is safe. When everything is tangled together, there is no such thing as a low-risk edit, no matter how small the diff looks.

Cheaper implementation also shifts where the line sits. Writing a property-based test or a small reference model used to feel hard to justify for ordinary application logic, so teams reserved those tools for storage engines and compilers. When an agent can draft a working harness in an afternoon, stronger evidence becomes practical for far more of the codebase. Generating a check is rarely the hard part anymore. Deciding which guarantees are worth maintaining over time, and keeping the checks honest as the system changes, is where the real effort goes.

## Evidence as engineering judgment

When writing code was the dominant cost of software development, testing was naturally treated as an attachment to implementation: you built the feature, wrote tests to cover it and moved on.

As implementation grows cheaper, deciding what would actually convince us that a change is safe becomes a central part of the job. That means separating what a test proves from what it merely assumes, choosing evidence that fits the risk and staying honest about the gaps that remain.

A passing test suite is easy to obtain now. Knowing which failures it can genuinely rule out, and which ones could still wake us up a month from now, is much harder.
