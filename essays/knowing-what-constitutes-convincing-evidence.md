# Knowing what constitutes convincing evidence

Suppose an AI agent modifies how a storage engine writes checkpoint metadata and accompanies the change with a thorough suite of crash-recovery tests. Every test passes. A month later, under production load, an interrupted checkpoint leaves the engine unable to recover.

When we investigate, we discover that both the implementation and the tests relied on the same assumption: that renaming a metadata file makes it durable without syncing the parent directory. The tests exercised the code carefully, yet they could never have detected the defect because they shared the misunderstanding that produced it.

As AI makes it much cheaper to generate both code and tests, a passing test suite becomes an increasingly unreliable measure of confidence. The difficulty is no longer producing verification artifacts. It is knowing what constitutes convincing evidence.

## The limits of self-verification

When an engineer writes a piece of code and then writes unit tests for it, there has always been a risk of circular confirmation. The tests reflect the author's mental model of the problem, including its blind spots.

AI amplifies this tendency. An agent tasked with implementing a feature and making sure it is well tested can produce hundreds of lines of tests in seconds. The coverage metrics look impressive and the build is green. Yet many of those tests verify little more than that the code does what the code does.

Mocks make this problem worse. If an agent implements a payment handler in an order management system and writes tests using a mocked payment gateway, the tests confirm only how the handler behaves against the agent's model of the gateway. They tell us nothing about what happens when the real gateway delivers a webhook twice, sends events out of order or times out after charging the customer.

In [When code review becomes the work](./when-code-review-becomes-the-work.md), I argued that we should shift effort from inspecting individual implementations towards building durable verification instruments. That shift only helps if those instruments provide genuine, independent evidence rather than automated reassurance.

## What makes evidence independent

Evidence becomes more convincing when it is separated from the assumptions of the implementation under test.

One form of independence comes from testing external properties rather than internal mechanics. In the order management system, we care about invariants that hold regardless of how the code is structured: the total amount refunded on an order must never exceed the amount collected, and repeated payment notifications must never produce duplicate fulfillment. Checking these properties across randomized sequences of delayed, duplicated and interrupted requests tests the system's guarantees without mirroring its implementation.

Another form of independence comes from comparing the system against a different source of truth. Reconciling our transaction ledger against the payment provider's settlement records catches discrepancies that no isolated test suite would anticipate. For a storage engine, comparing the results of a sequence of operations against a simple, obviously correct in-memory reference model can reveal subtle edge cases in compaction or snapshot isolation.

Independence also matters organizationally. If the same agent prompt produces both the implementation and the tests in one pass, any ambiguity in our instructions is likely to be resolved consistently across both. Separating the definition of the guarantees we want to verify from the implementation that tries to satisfy them reduces the chance that both make the same mistake quietly.

## Testing the verification itself

A passing check tells us little until we know what it is capable of catching.

When an agent constructs a crash-recovery simulation or a property-based test, it is easy for a subtle bug in the harness to render the test toothless. The crash might happen before the interesting state transition rather than during it. A cleanup routine might hide a corrupted file. An assertion might check only that the process restarted, not that every acknowledged write survived.

As I noted in [Continuous cultivation of software](./continuous-cultivation-of-software.md), one practical way to challenge a verification instrument is to introduce deliberate faults into an isolated copy of the system and verify that the checks detect them. If we remove a durability sync or allow a duplicate refund and the suite remains green, we have learned something important about the limits of our evidence.

We also need to periodically check the fidelity of our models against the real environment. A deterministic filesystem simulator is enormously useful for exploring crash recovery, but only insofar as its model of reordering, torn writes and directory durability reflects the storage systems we actually run on. Comparing simulated assumptions against real operating environments, and against production incidents when they occur, keeps our verification grounded in reality.

## Proportionate evidence

Not every change warrants a deterministic simulation or a formal model. Demanding the same standard of proof for every modification would slow development to a halt for little benefit.

Evidence should be proportionate to the consequence of being wrong. A minor adjustment to an administrative display can be verified cheaply by inspection or a simple check. A change to the storage engine's durability protocol, or to the authorization rules protecting customer data, justifies far stronger scrutiny.

The advantage of investing in stronger verification instruments is that their cost is spread across many future changes. A well-tested crash harness for the storage engine, or a reconciliation check for payment processing, continues to provide independent evidence long after the original change has been forgotten. In contrast, brittle unit tests tied tightly to internal structure have to be rewritten whenever the implementation changes, offering weak evidence at a recurring cost.

Knowing where stronger evidence is needed, and where lighter checks suffice, is itself an engineering judgment that depends on understanding the system and its risks.

## Evidence as engineering work

For a long time, testing was treated as a supporting activity attached to implementation. When writing code was the dominant cost, that ordering made sense.

As implementation becomes cheaper, establishing justified confidence becomes one of the main contributions engineers make. Deciding which guarantees matter, designing independent ways to test them, challenging those tests with deliberate faults and being honest about what remains unproven are substantial technical problems.

Confidence in a storage engine does not come from the number of tests that pass after a change. It comes from knowing which failures our evidence can actually rule out, and where our certainty ends.
