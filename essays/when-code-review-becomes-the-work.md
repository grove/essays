# When code review becomes the work

An AI agent can produce a change in minutes that takes an engineer much of an afternoon to review. We can run several agents concurrently, but our capacity to review their work does not increase in the same way.

I also find this division of work unattractive. Much of what makes software engineering enjoyable is investigating a problem, exploring possible solutions and arriving at a design that one is pleased with. If we delegate these activities to agents and retain responsibility for reviewing their output, we risk automating much of the work we enjoy while keeping much of the work we don't.

Our development practices evolved when implementation was expensive. As the relative costs of implementation and verification change, so should our way of working.

## The changing nature of code review

When reviewing a colleague's implementation, we could traditionally assume that the author had spent time understanding the problem, considering alternatives and working through difficulties. If we questioned a design decision, we could discuss it with someone who had developed an informed opinion. Some of the most interesting engineering discussions arise during code review.

When an agent implements a feature, the person submitting the change may know little more about it than the reviewer. Someone still needs to understand the problem, evaluate the design and establish confidence in the implementation. Much of that work now falls to the reviewer.

This is an awkward way of acquiring understanding. When implementing something ourselves, we develop our understanding incrementally as we encounter problems and work through them. When reviewing a finished implementation, we have to work backwards from the result. An agent can explain the decisions it made, but reading such an explanation is a different experience from participating in the work.

Working closely with an agent during implementation avoids much of this problem. Staying involved as the code takes shape lets us question choices as they arise rather than reconstructing them afterwards. That kind of collaboration is genuinely useful, though it still binds an engineer's attention to one task at a time. As soon as teams also want agents working concurrently in the background, the review bottleneck returns.

## Where humans participate

Suppose we want to change when a storage engine can reclaim old log segments. Rather than asking an agent to implement the change and subsequently reviewing its work, I would prefer to investigate the problem with the help of an agent.

We can examine the relationship between checkpointing and recovery, explore what happens when a checkpoint is interrupted and consider whether we need to retain enough log data to recover from certain kinds of corruption. We can conduct experiments and explore alternative designs before deciding what to implement.

Much of the implementation work can then be delegated. We already understand the problem, know why we chose a particular design and have some idea of how to verify it.

This does not mean that engineers should design every change in advance. That would simply move the bottleneck. Implementation is itself a form of investigation, and some of what we discover during implementation gives us reason to reconsider earlier decisions.

Agents do not reliably recognize when such reconsideration is warranted. An agent encountering an unexpected dependency might introduce a special case rather than investigate why the dependency exists. The tests pass, and we never learn that there was an interesting problem in the first place. Asking agents to record unexpected discoveries and abandoned approaches helps, but we also need investigations that are independent of the implementation task.

This way of working has implications for how we develop engineering expertise. Sometimes it makes sense to have a less experienced engineer implement something themselves, even when an agent could do it faster. Giving them responsibility for a small subsystem allows them to experience the consequences of their own decisions. As I argued in [Implementation and understanding](./implementation-and-understanding.md), we need to become more deliberate about how engineers acquire understanding as we increasingly delegate implementation.

## Establishing confidence

Consider whether a change to a storage engine preserves its durability guarantees. We can spend hours examining the implementation and still overlook a sequence of events that results in data loss. A deterministic simulation that introduces failures at different points during execution can provide stronger evidence about crash recovery than code inspection alone.

The same principle applies to ordinary application development. In an order management system, repeated payment notifications must not result in duplicate fulfillment, and refunds must not exceed the amount collected. We can test these properties by delivering notifications late, out of order or more than once, and by interrupting the application at various points during processing. Reconciling our transaction records with those of the payment provider gives us further evidence about the behavior of the system in practice.

Whether the checkout experience is any good requires a different kind of evaluation. The fact that something requires human judgment does not mean that reading source code is the best way to exercise that judgment.

These verification techniques already exist. AI reduces the effort involved in developing and applying them.

The harder problem is knowing what constitutes convincing evidence.

An agent modifying a recovery protocol and an agent constructing a simulation to verify it could both rely on the same mistaken assumption about the guarantees provided by the filesystem. The implementation might pass every simulated failure while remaining unsafe in practice. We need to examine our verification instruments, deliberately introduce defects they ought to detect and compare their behavior with observations of the actual system.

Reviewing verification code is not inherently easier than reviewing an implementation. Its advantage is that the results of the work can remain useful across many subsequent implementations. A good simulation of a storage engine's operating environment allows us to investigate different recovery protocols without having to substantially change the simulation itself.

Tests that need extensive modification whenever the implementation changes offer little of this advantage. For a straightforward, isolated change, reading the code can still be the most economical approach.

## Making autonomous development possible

A mechanical refactoring and a modification of a persistence protocol have quite different consequences. We should be able to delegate routine refactorings while retaining human involvement in changes to the guarantees provided by the storage engine.

Where changes are sufficiently constrained and independently verifiable, agents should be able to make them without individual human approval. This requires independently enforced rules about what agents can modify and what evidence is required before accepting a change. An agent authorized to change an implementation should not also be authorized to weaken the requirements against which it is evaluated.

The engineers responsible for operating a system must have authority over these arrangements, including how changes are deployed, monitored and audited. They must also be able to suspend autonomous development when they lose confidence in it.

One thing that strikes me about code review is how often we find ourselves checking the same kinds of things. In a web application, we might repeatedly check whether new endpoints enforce the appropriate authorization rules. Rather than continuing to do this manually, we can organize the software so that authorization is difficult to omit and attempts to bypass it are detectable.

This is an example of [continuous cultivation of software](./continuous-cultivation-of-software.md): systematically investigating and improving existing software to make its subsequent development easier.

The effort spent reviewing an individual change primarily benefits that change. The effort spent making an entire class of changes easier to verify benefits subsequent development as well.

As implementation becomes cheaper, the relative value of these investments changes. If a team already has more implementations awaiting review than its engineers can reasonably handle, producing additional implementations does little to accelerate development. Improving the team's ability to verify and accept changes may be a better way of getting features into production.

Convincing an organization to invest in this work is still difficult. Features are visible, whereas much of the value of better verification lies in work that no longer needs to be done. The benefits also extend beyond the planning horizons of many organizations.

Returning to the authorization example, a team could spend two weeks recording how much time its engineers spend checking authorization during code review. It could then set aside a few days to make authorization an explicit part of endpoint registration and introduce tests that exercise unauthorized access. By observing the review effort, defects and maintenance costs over subsequent changes, the team can establish whether the investment was worthwhile.

Over time, we can expand the kinds of changes that proceed without individual human approval. We do not need to wait for agents to become reliable enough to work autonomously on arbitrary software. We can improve our own software so that more of its development can be delegated with confidence.

## A different division of work

Much of the discussion about AI-assisted development concerns how much software an engineer can produce. We should give more attention to what engineers actually spend their time doing.

I would like to see projects in which much of the ordinary implementation and maintenance work proceeds autonomously. Engineers investigate the systems they maintain, explore alternative designs and decide how those systems ought to evolve. They develop better ways of establishing confidence in the software and intervene when the available evidence is insufficient.

Getting there requires substantial engineering work. But much of that work improves the conditions under which we will develop software for years to come, rather than helping us get another pull request merged.

If I have an afternoon to spend working on a storage engine, I would rather investigate whether its recovery protocol can be simplified than review three implementations of changes to that protocol.

AI makes the former increasingly practical. The way we currently organize software development is giving us more of the latter.