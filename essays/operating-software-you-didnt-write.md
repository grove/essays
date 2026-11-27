# Operating software you didn't write

At three in the morning, a storage engine begins stalling writes shortly after a background compaction. Or an order management system starts reporting mismatches during nightly reconciliation with the payment provider.

The on-call engineer opens the deployment history and finds four changes released over the past week. Three were implemented by AI agents and reviewed briefly; one was merged autonomously after passing the test suite. Within minutes, the engineer has to decide whether to roll back a deployment, throttle incoming traffic or intervene manually to protect customer data.

Writing software is only part of the job. We also have to operate it when it misbehaves.

## Accountability cannot be delegated

Much of the discussion about autonomous development focuses on getting changes merged safely. Less attention is paid to what happens weeks later when those changes encounter real traffic, partial network failures or unexpected data in production.

We can delegate implementation, test generation and even initial alert triage to agents. We cannot delegate accountability. When customer data is at risk or orders fail to ship, the people responsible for the service still have to answer for its behavior and restore it safely.

In [Implementation and understanding](./implementation-and-understanding.md), I wrote about how AI separates producing code from building a mental model of the system. During ordinary development, that gap can feel easy to ignore, especially when tests are green and features are shipping quickly. During a production incident, the gap becomes immediately visible.

When you wrote a subsystem yourself, you often carry a rough intuition for where it is fragile, which queues can back up and what a particular error message implies. When you did not write it, and perhaps only glanced at the diff, you start the incident at a disadvantage.

## Understanding under pressure

Incident response is a poor time to build an understanding of a system from scratch.

Under normal circumstances, an engineer can pause, run an experiment and explore how a recovery protocol behaves. At three in the morning, with write latency climbing, the priority is stabilizing the service without making the situation worse. A mistaken intervention, such as restarting a storage engine node in the middle of a degraded recovery or rolling back a schema-dependent deployment, can turn a minor degradation into data loss.

AI agents can certainly help during an incident. They can correlate recent deployments with error spikes, search logs across services and trace unfamiliar code paths much faster than a tired human. Used well, they shorten the time it takes to form hypotheses.

Yet an agent's explanation during an incident is still only a hypothesis. It can sound fluent and confident while overlooking an operational detail that is not recorded in the repository, such as a saturated disk, a change in a warehouse partner's batch timing or an upstream rate limit. The engineer on call still needs enough grounding in the system's invariants and operational behavior to judge whether a proposed mitigation is safe.

## Making systems legible in operation

If teams will increasingly operate code they did not write line by line, operational legibility needs to become a deliberate design priority rather than an afterthought.

A system that is legible in operation exposes its core guarantees directly in its telemetry. For a storage engine, that means visibility into compaction backlog, checkpoint age, write amplification and recovery progress. For an order management system, it means monitoring unreconciled payments, stuck fulfillments and cancellation anomalies rather than only HTTP error rates.

Just as important are safe operational levers. Routine, rehearsed rollbacks, clear blast-radius limits, circuit breakers and feature flags allow an on-call engineer to return the system to a known-good state before fully diagnosing the root cause. When recovery depends on understanding every line of the latest release before taking action, the cost of delegating implementation rises sharply.

Change provenance matters too. Knowing what changed, which guarantee it touched, what verification evidence supported its release and which parts of the deployment can be reversed independently makes triage far calmer than sorting through a stream of opaque, high-volume commits.

## Closing the loop with cultivation

Production incidents are expensive, but they are also one of the clearest sources of truth we have. Every real failure reveals a gap between what we believed the system guaranteed and what it actually did under real conditions.

Traditional postmortems often produce a narrow bug fix and a list of action items that quietly age in the backlog. In a team practicing [continuous cultivation of software](./continuous-cultivation-of-software.md), an incident has a more concrete destination: it defines the next round of investigations and strengthens the system's verification instruments.

If a compaction stall occurred because a long-lived snapshot interacted badly with a recent optimization, the follow-up is not merely patching the interaction. It is turning that workload into a reproducible experiment, asking what other assumptions around compaction remain untested and tightening the rules governing autonomous changes in that part of the engine until confidence is earned back.

In this way, operations and cultivation form a loop. Production tells us where our verification was incomplete; cultivation turns those lessons into lasting protection before the next incident occurs.

## The test of a development practice

When implementation becomes fast, it is tempting to judge a development process by how smoothly changes move from specification to production.

A better test is what happens when something goes wrong in production. Can the team explain what the system is doing? Can they intervene safely without guessing? Do they learn something durable from the failure, or does the same class of surprise recur under a slightly different change?

Delegating implementation works best when it is paired with systems designed to be observed, bounded and recovered calmly. The real measure of our readiness to hand more coding work to agents is not how quickly pull requests merge on a Tuesday afternoon, but how well we can operate the software when it misbehaves in the middle of the night.
