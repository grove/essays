# Continuous cultivation of software

*Why we need software farms in the age of AI*

We have learned to build, test and deliver software continuously. We are less systematic about investigating the software we already have.

Consider a storage engine that promises not to lose acknowledged writes when a process crashes. It has tests for writing data, creating checkpoints and recovering after a restart. All of them pass. But what happens if the process crashes during checkpointing, shortly after a write has been acknowledged? Unless somebody has thought to test that particular sequence, we may know surprisingly little about whether the engine keeps its promise.

There is no failing build to investigate and probably no issue on the backlog. The problem, if there is one, is waiting for somebody to ask a good question.

Most maintainers have a feature to finish or a known bug to fix. Spending an afternoon investigating a problem that may not exist is difficult to justify. AI gives us a chance to make proactive investigation, along with the verification, simplification and maintenance of rationale that follow from it, a routine part of tending existing software. I call this broader practice **continuous cultivation of software**.

## When code becomes cheaper

Much of the discussion about AI in software development concerns how much more code we can produce. A feature that should never have been built still has a maintenance cost, however little it cost to implement. Somebody will have to understand it, test it and account for it when changing other parts of the system.

Our capacity to introduce changes can grow much faster than our capacity to understand their consequences.

Many of the things that make agents useful for implementation also make them useful for investigation. An agent can trace an unfamiliar code path, compare it with a documented guarantee, examine the existing tests and construct an experiment. If it can do enough of that work well, we can afford to ask questions we would previously have left alone. The cost of reviewing the answers is part of that calculation.

## Software farms

Continuous integration did not invent compilation or testing. It made integration and verification routine. Continuous delivery extended that discipline to preparing software for release.

We can do something similar with proactive investigation. We already have the methods: exploratory testing, fuzzing, fault injection, architectural review and performance analysis, among others. What is missing in many projects is a regular process for deciding where to apply them, carrying out the investigations and making use of what is learned.

A software farm is a way of organizing the investigative side of continuous cultivation. It complements the software factory, which organizes the implementation and delivery of changes.

**A software factory starts with work to be done. A software farm starts with a question worth investigating.**

The same people and tools can serve both purposes. The distinction matters because it changes what counts as success. An investigation that establishes a good reason to keep the existing design has accomplished something, even though no change has been made.

Even when development is quiet, workloads and dependencies change, and the reasons for old design decisions can cease to apply.

## A farm at work

Imagine a team maintaining the storage engine. Ordinary development continues as before. Alongside it, the team runs one bounded investigation a week into durability and recovery, with a fixed budget for compute and maintainer time. Agents use approved tools in an isolated environment and have no authority to change production code.

During one run, an agent reads the durability contract, follows the commit, checkpoint and recovery paths, and examines the tests and previous investigations. It finds tests for checkpointing and recovery separately, but finds none that exercise recovery after an interruption during a checkpoint. That is a reason to investigate, not evidence of a defect.

A farm should make use of the verification tools we already have, whether that means a fuzzer, a fault-injection harness, Jepsen or Antithesis. The agent’s contribution here is to connect a promise in the documentation with the code responsible for keeping it, identify a property or workload that existing verification overlooks and prepare an experiment. The investigative work matters more than whether a separate agent or the verification tool itself does it.

For the checkpoint question, the agent interrupts the process at a particular point. It independently records which writes were acknowledged before the interruption and checks whether the recovered data contains them.

A failure may reveal a defect, or it may reveal a flaw in the experiment. A passing test is just as deserving of scrutiny. Did it exercise the actual recovery path? Did the interruption occur during checkpointing? One way to challenge the test is to introduce a deliberate fault in an isolated copy of the engine and check that the test detects the resulting loss of acknowledged data. Catching that fault gives us some confidence in the experiment without establishing that it covers every possible failure.

A passing result is meaningful only within the limits of the experiment. A process interruption tells us little about how the engine handles power loss.

Choosing good questions is difficult. Start with guarantees the maintainers consider important and let agents propose investigations within that scope. Recent changes, incidents and weak evidence provide clues about where to look next. Greater autonomy has to be earned through experience.

## Proof before interruption

Nobody wants another source of automated bug reports. A maintainer should not have to repeat an investigation from scratch. For a suspected durability defect, require the applicable guarantee, tested revision, runnable reproduction, actual results and an account of which alternative causes have been ruled out. Evidence should be proportionate to the claim. A performance problem calls for a repeatable benchmark; an ambiguous contract calls for the conflicting sources and an explanation of why the ambiguity matters.

Check whether a finding is already known. If there is nothing consequential and sufficiently supported to report, leave a brief record of the investigation and stay quiet.

Many teams already have more bugs and technical debt than they can address. A farm cannot fix their priorities, but a reproducible failure is considerably easier to act on than a suspicion. The team still needs time to review the evidence and deal with important findings. There is little point in investigating more than the team can make use of.

## Context is something we cultivate

When you join an established engineering team, reading the code tells you a great deal about what happens. Finding out whether it is supposed to happen, and why, often requires a conversation with a colleague who remembers a decision made several years ago.

An AI agent faces the same difficulty, sometimes afresh on every assignment. Context engineering aims to give an agent just enough trustworthy knowledge for the decision at hand. Clear module boundaries, searchable names and concise repository instructions help it find the relevant code, contracts, tests and design decisions. But better retrieval does not repair an ambiguous contract or an inadequate test.

This is where context engineering and software farming meet. Once the checkpoint experiment has been reviewed and retained as a regression test, an engineer changing the recovery protocol years later can benefit from it without ever reading the original investigation report.

Some of the best context is applied by the system itself, without having to be read at all. Types, assertions and automated checks can enforce rules. Where intent and rationale cannot adequately be expressed in code, they belong in maintained specifications or decision records. A generated wiki can make those sources easier to find, but the knowledge belongs to the project and should survive the replacement of the model, the wiki or the farm.

## Simplicity reduces the need for context

Suppose the storage engine keeps track of the latest completed checkpoint in two places, a persistent manifest and separate recovery metadata. To change the checkpoint protocol safely, an engineer needs to understand when each is updated, which takes precedence and what happens when the two disagree after a crash.

We could document these relationships more thoroughly. We could also investigate whether one authoritative representation would suffice. The crash harness we already have gives us a useful way to challenge a simpler design. If the alternative preserves the required behavior, there are fewer states to reason about and fewer interactions to test.

Sometimes the best way to make context cheaper to consume is to reduce the complexity that gives rise to it.

Perhaps the second representation is necessary to distinguish a completed checkpoint from one whose writes were interrupted. That, too, is useful to establish. Record the reason and future engineers will have one less thing to work out for themselves.

Good software design limits how much of a system we need to understand at once. Context engineering helps us find that knowledge. Software farming helps us discover and validate what is missing.

## Learning that compounds

Consider a later investigation into when the engine can safely reclaim old log segments. If a checkpoint is interrupted, is it possible for recovery to need a segment that has already been removed? The agent need not start from scratch. It has a reviewed durability contract, a crash harness and a way to check the acknowledged writes after recovery, perhaps also an explanation of how checkpoint state is represented and why.

Each useful investigation leaves the next one with a better starting point. The same knowledge helps an engineer implementing a new feature or an agent reviewing a change. This is the opportunity I find most interesting: using AI to make future engineering easier, for humans and agents alike.

Faulty tests and unsupported explanations can compound error instead. Observations about current behavior do not establish new requirements, and old evidence needs reconsidering when its assumptions change.

Even when done well, cultivation pays off where either a single failure would be costly or the returns have time to compound. A long-lived storage engine or billing system carries costly guarantees across years of change. A short-lived prototype, a disposable internal tool or software whose failures are cheap to notice and fix rarely justifies building durable investigation harnesses and maintained rationale. Every investigation costs compute, review attention and delayed feature work. Whether cultivation produces a compounding benefit at an acceptable cost is something we still need to demonstrate in practice.

## Start small

Try this with a system you already maintain. Pick one consequential guarantee, such as recovery after a crash. For four weeks, run one bounded investigation each week using the project's existing test tools. Set a compute budget and a ceiling on maintainer time for review and follow-up, perhaps two hours a week. If that is more time than the team can spare, start smaller.

Ask for a specific question, the reason it matters and evidence you can check yourself. Keep useful tests and explanations through the normal review process. At the end of the four weeks, look at what you learned beyond your ordinary verification, what you kept and how much effort it took, including the runs that yielded nothing. Decide whether another month is worth it.

There is no need for a new runtime or a comprehensive knowledge base to begin.

Years from now, the maintainers of a well-cultivated project should inherit software they can understand and change with confidence, along with the evidence that justifies that confidence. They should also know where that confidence ends.

---

*Author's note: This essay grew out of work on the [Context Constitution](https://gist.github.com/grove/d48a52bbb3c7e8e11bf21a8675f4506f), a proposal for managing trustworthy project knowledge, and [Farm](https://github.com/grove/farm), an experimental open-source project exploring continuous software investigation. The storage engine examples illustrate the proposed practice rather than report measured results from Farm.*