# The economics of removing software

Four years ago, an order management system acquired a workaround for a warehouse partner that could only report dispatches in a nightly batch file. That partner was replaced two years ago. Yet the batch-reconciliation job, its retry tables, its special cases in the cancellation logic and its tests are still in the codebase.

Every time someone changes how orders are canceled or refunded, those paths have to be understood, preserved and worked around. Nobody removes them because no customer is asking for it, and nobody is entirely certain whether some obscure reporting script still reads the retry table.

When AI makes adding software cheap, the imbalance between what we add and what we remove grows much faster than most teams notice.

## The asymmetry of accumulation

Even before AI, software grew much more readily than it shrank.

Adding a feature or a special case is usually local and justified by an immediate customer request or bug report. Removing code requires a different kind of work: proving that nothing still depends on it, checking assumptions across integrations and accepting responsibility if a quiet consumer breaks.

In [Discovering what software should do](./discovering-what-software-should-do.md), I noted that the ongoing cost of having built something does not disappear just because it was cheap to build. Every feature, flag and fallback path remains part of the system that future engineers and agents have to take into account.

AI shifts the economics of that accumulation in two ways.

First, dead code costs more when agents work in the repository. An agent starting a fresh session does not know which parts of the codebase are relics of a retired partner and which represent current requirements. It searches the repository, gathers context and infers local conventions from what it finds. Obsolete branches, unused flags and retired tables show up in retrieval results, occupy context and become patterns that agents copy into new work.

Second, one of the oldest justifications for keeping dormant code around has weakened, though not disappeared. Teams used to hold on to unused features and fallback paths because rebuilding them later would be expensive if someone ever asked for them again. Cheap implementation lowers the cost of rewriting code, and the old code sits in version control anyway. It does not make reconstructing the domain knowledge, integration quirks or verification evidence behind that code free. Still, leaving dead paths alive inside active code rarely preserves that knowledge well; recording why a workaround existed before retiring it usually protects what matters at far lower ongoing cost.

Not all unused code imposes the same cost. An isolated export script sitting at the edge of a system can often be ignored cheaply. The warehouse batch path sits inside order cancellation and refund handling, where ordinary changes happen every week and have to work around it.

## Two kinds of subtraction

When we talk about removing software, it is worth distinguishing two different kinds of work.

The first is retiring code that is no longer used: the warehouse batch job, an old feature flag or a deprecated API path. Here the central question is whether anything still depends on it.

The second is simplifying code that is still active. In [Continuous cultivation of software](./continuous-cultivation-of-software.md), I gave the example of a storage engine tracking its latest completed checkpoint in two places, a persistent manifest and separate recovery metadata. Neither representation is dead. The question is whether a single authoritative representation can preserve every durability guarantee that the two of them currently provide.

Across both kinds of work, the distinction I drew in [Designing for delegation](./designing-for-delegation.md) between stateless logic and persistent state still holds. Deleting a dead branch in the cancellation code is easy to revert if we are wrong. Dropping the retry table is not. Treating both as a single cleanup is one reason obsolete workarounds survive for years: the risk of dropping the table keeps anyone from touching the code around it.

## What AI changes, and where it stops

The encouraging side of cheaper implementation is that many of the capabilities that make agents useful for adding code also lower the practical cost of removing it.

For active simplification, the change is substantial. Investigating whether the storage engine truly needs two checkpoint representations, testing a simpler design against a crash harness and migrating away from the redundant metadata used to be the kind of cleanup that stayed on a wish list for years. An agent can now do much of that investigative work and test whether the simpler design holds up before anyone commits to changing production code.

For retiring dead code, an agent can quickly map every internal caller, scheduled job, configuration flag and test connected to the warehouse batch workaround. Once a decision has been made, it can also handle the mechanical work of removing the cancellation special cases, cleaning up configuration and updating affected tests.

Where an agent's usefulness stops is at the boundary of the repository.

No amount of reading the order management codebase can prove that an obscure reporting script in a separate analytics tool, another team's repository or a forgotten cron job is no longer querying the retry table. Static analysis can establish that a code path is unreachable inside the service; it cannot prove the absence of an external consumer.

There are also two ways agents can make subtraction harder rather than easier.

During ordinary development, agents tend to preserve past mistakes and harden them into permanent requirements. Instructed to keep existing behavior intact and all tests passing, an agent refactoring order cancellation will faithfully migrate the dead warehouse branch, carry its flags into the new design and write fresh tests asserting how it behaves. As I noted in [Knowing what constitutes convincing evidence](./knowing-what-constitutes-convincing-evidence.md), tests generated from existing code can easily turn incidental behavior into something that looks like an intentional contract. Unless humans ask whether old behavior is still wanted, agents will maintain our past workarounds indefinitely.

The opposite mistake happens when we simply ask an agent to find and delete unused code. Finding zero references in the repository does not establish that a table is unread, that a handler is never reached through dynamic configuration or that a job does not run only once a year during financial close. An agent can produce a confident report recommending deletion while overlooking usage that never appears in the repository or in a short window of recent logs.

## Why obsolete code still stays

Even as the technical effort of removal falls, obsolete paths will not disappear on their own.

Most of the remaining obstacles are social and organizational rather than technical. Keeping an unused branch feels safe; deleting it feels risky. If the warehouse workaround stays in place for another three years, its cost is diffuse and largely invisible, spread across every future change as slightly slower reviews, noisier context and slightly more convoluted tests. If deleting it breaks one forgotten report, the failure is immediate and attributable.

Roadmaps reinforce this imbalance. Product plans and stakeholder reviews naturally reward visible new capabilities, whereas much of the value of removing code lies in friction that no longer occurs: changes that go smoothly next quarter, defects that do not happen and confusion a new engineer or agent never runs into. If an organization spends all the time AI saves moving faster down the feature backlog, teams will rationally keep adding software while leaving yesterday's workarounds untouched.

## Practicing deliberate subtraction

Removing software reliably requires treating subtraction as regular engineering work rather than an occasional cleanup.

Separating the investigation from the deletion is a practical place to begin. Rather than asking an agent to delete the warehouse workaround, assign it to produce an account of what the workaround actually does: every place it touches cancellation and refund logic, which tables it reads or writes, what production logs show over the past year and which pieces can be retired independently. As with any other investigation, the outcome might be a documented reason to keep part of it. That too is useful, because it replaces superstition with evidence.

Where the repository cannot settle the question, removal has to be observable and staged. We do not need to delete the cancellation special cases and drop the retry table in the same change. We can instrument reads on the retry table and log any entry into the batch path, wait long enough to catch infrequent jobs, then remove the cancellation branches in a small, easily reverted change while leaving the table untouched until we are confident nothing queries it. Clear module boundaries and independent verification instruments make these steps much safer, because they let us confirm that core order and refund guarantees still hold once the workaround is gone.

It also pays to be selective about where to spend this effort. Counting lines deleted is no wiser than counting lines added. The best candidates for subtraction are the ones that repeatedly get in the way of active work: old workarounds tangled into code that changes often, flags that multiply test combinations and redundant state that forces every change to keep two stories straight.

The cheapest time to make temporary code removable is often when we write it. If cheap implementation leads teams to run more experiments, build more migration shims and add more partner-specific workarounds, we should write temporary code with its removal in mind: keeping a partner workaround behind a narrow boundary instead of threading it through core logic, keeping its tables separate and recording the condition under which it can be retired.

## Keeping software small enough to understand

Every piece of obsolete code we remove reduces what both humans and agents have to carry in order to work safely in a system. It removes states that no longer need to be tested, branches that no longer need to be explained and assumptions that can quietly go stale.

When writing code was expensive, restraint came partly from friction: we simply could not build everything we thought of. As that friction fades, restraint has to become deliberate.

Removing the nightly warehouse batch path is rarely urgent on any given day. Yet regularly finding and retiring code like it, especially where it sits in the path of active work, may do more to keep a system understandable over time than most of the features we add.
