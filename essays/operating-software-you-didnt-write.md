# Operating software you didn't write

At three in the morning, a storage engine begins stalling writes shortly after a background compaction starts. Disk usage climbs, write latency crosses timeout thresholds and upstream services begin failing.

The on-call engineer opens the deployment history and finds four changes released over the past week: an optimization to compaction scheduling, an adjustment to how long-lived snapshots pin old log segments, a refactoring of metric reporting and a dependency update. Three were implemented by AI agents and reviewed briefly. The compaction change was merged autonomously after passing the test suite.

Within minutes, the engineer has to decide whether to roll back one of those releases, throttle incoming writes, abort the running compaction or restart the affected node. A mistaken move, such as restarting in the middle of a degraded recovery or rolling back across a subtle metadata change, can turn a latency spike into lost writes.

Writing software is only part of the job. We also have to keep it running when it does something nobody expected.

## When nobody wrote it

Engineers have always operated software they did not write. You rotate onto a new team, inherit a legacy service or run a database written by people you have never met. Operating unfamiliar code is nothing new.

What changes with AI is that often nobody on the team wrote the code either. When you go on call for a service a teammate maintains, you may not know every line, yet someone nearby built a mental model while working through the recent changes. You can page them, check their reasoning or ask why a lock is acquired in a particular order. In [Implementation and understanding](./implementation-and-understanding.md), I wrote about how AI separates producing code from building a mental model of the system. While tests are green and features keep landing, that separation is easy to ignore. When last week's changes were written by agents and skimmed in review, nobody in the room carries the author's intuition. We can delegate implementation, test generation and initial alert triage, while accountability stays with the people responsible for the service.

The pace of change shifts as well. Running a mature database or a quiet inherited service works because its failure modes are relatively stationary; over months of operating it, engineers learn its habits under load without ever reading its source. When agents make it cheap to ship steady streams of optimizations, refactors and autonomous merges, the system's operational behavior drifts faster than an on-call rotation can build a feel for it.

## Understanding under pressure

During ordinary work, an unfamiliar subsystem is something you can investigate calmly. You can read the code, run a local experiment and watch how recovery behaves under load. During an outage, stabilization and exploration pull in opposite directions. The immediate job is to stop customer impact without making the damage worse.

AI agents are useful here. They can correlate a latency spike with recent deployments, search logs across nodes and trace unfamiliar code paths far faster than a tired engineer. Used well, they shorten the time it takes to gather context and form hypotheses.

An agent's explanation during an incident is still only a hypothesis, and under fatigue a fluent diagnosis is hard to challenge. An agent inspecting the repository might point confidently to the autonomously merged compaction change and recommend reverting it, while missing an operational fact that is not in the repository at all: an analytics job started holding a snapshot open for six hours after a partner shifted its nightly export window, or a neighboring workload saturated disk I/O. When the engineer on call has little independent feel for the subsystem, it is difficult to tell whether the agent has found the cause or simply built a tidy story out of the files it could see.

Fast code generation also creates a temptation to fix forward. When an agent can draft a plausible patch in two minutes, tired teams feel a pull to ship a quick hotfix for code nobody deeply understands rather than rolling back or shedding load. A hurried patch that passes a couple of local checks during an outage can easily make a bad night much worse.

Handing routine alert triage and minor daytime incidents to agents carries a subtler cost. Small production hiccups are one of the main ways engineers learn how a service bends before it breaks. Automate away all of that exposure, and the first time a human looks closely at a subsystem's live behavior is during a serious outage.

## Designing for calm recovery

If teams are going to run code they did not write line by line, recovery cannot wait until an operator has read the latest commits.

Telemetry has to reflect the system's guarantees rather than generic symptoms. HTTP error rates and CPU graphs tell you that something hurts, not which promise is failing. In the storage engine, the signals that matter are compaction backlog, oldest pinned snapshot age, checkpoint lag and recovery progress. If a dashboard immediately shows a six-hour-old snapshot pinning log segments while compaction falls behind, the on-call engineer does not have to reconstruct the compaction scheduler from source code to see what is happening. In an order management system, nightly reconciliation against a payment provider, which I described in [Knowing what constitutes convincing evidence](./knowing-what-constitutes-convincing-evidence.md) as detective evidence, tells you that settled payments and recorded orders have drifted apart. Operational telemetry around stuck webhook retries and unconfirmed cancellations tells you where that drift is accumulating so you can stop it.

Safe containment matters just as much, provided we are honest about where rollback stops. Rehearsed rollbacks, write throttling, circuit breakers and kill switches let an operator return a service to a known-good state before finishing a diagnosis. Here the distinction I drew in [Designing for delegation](./designing-for-delegation.md) between stateless logic and persistent state becomes an operational rule. Rolling back a metric refactoring or an export formatter is straightforward. Rolling back a storage engine release that altered a checkpoint or compaction format, or reverting a pricing change after incorrect charges have already been written to the ledger, does not undo the state already on disk or sent to a payment provider. Changes that cannot be reversed cleanly under pressure require a different release discipline: explicit human approval before deployment, staged rollouts or forward-compatible migrations rather than an autonomous path straight to production.

Release history also needs to stay readable under higher volume. When dozens of agent-assisted changes land in a week, a chronological commit log is noise during an outage. An operator needs to see quickly which module boundary each release touched, whether it altered persistent state or a core guarantee, what verification evidence backed it and whether it can be reverted on its own.

## Where operational legibility breaks down

The same habits that weaken testing and architecture show up in operations too.

Observability can become circular. Just as an agent writing tests alongside an implementation tends to confirm its own assumptions, an agent asked to add metrics, alerts and runbooks for a feature will instrument the failure modes it already imagined. Every panel on the dashboard can stay green while an unimagined interaction, such as a long-lived snapshot starving a new compaction heuristic, quietly stalls writes.

Release summaries and operational levers degrade under volume as well. Requiring every agent pull request to include an operational note easily turns into boilerplate prose that nobody can parse under pressure. Wrapping every change in a feature flag or kill switch multiplies the states the system can occupy; left behind after a rollout settles, those levers turn into dead branches and configuration paths that every later change has to carry around.

Recovery mechanisms also rot when they are not exercised. A rollback procedure that worked six months ago breaks quietly after a schema migration adds a non-nullable column. An agent can write a detailed runbook in seconds, yet a runbook nobody has actually run against a realistic failure offers false comfort when it matters.

## Turning incidents into lasting protection

Every real production failure exposes a gap between the fault model encoded in our verification checks and what actually happens under live traffic.

Traditional postmortems often stall at a narrow bug fix and a list of follow-up items that quietly age in the backlog. Usually that is not because teams do not care; building a realistic reproduction or crash harness takes days that lose out to feature work.

When a team practices [continuous cultivation of software](./continuous-cultivation-of-software.md), the economics of post-incident follow-through shift. Because agents lower the mechanical effort of constructing a workload and wiring it into an existing harness, the team can turn an outage into a repeatable experiment while the details are still fresh. If the compaction stall came from a long-lived snapshot colliding with the scheduling optimization, fixing that interaction is only the start. The team can turn the workload into a permanent check, examine what other assumptions around snapshots and compaction went untested and surface pinned-snapshot age on the dashboard before writes ever stall.

The incident should also change how much autonomy that part of the codebase is granted. As I argued in [When code review becomes the work](./when-code-review-becomes-the-work.md), the engineers who carry the pager need the authority to govern autonomous development. When production shows that a boundary or test suite is weaker than we believed, the response should include narrowing what agents can merge there without human review, slowing rollout pace or pausing autonomous changes in that subsystem until the verification instruments can catch that class of failure.

## The test of a development practice

When implementation becomes fast, it is easy to judge a development process by how smoothly changes move from specification to production.

Operations is where the shortcuts show up. Delegating more coding work to agents raises the standard for how observable, bounded and recoverable our systems have to be, and for how seriously we act when live traffic proves our assumptions wrong.

The real measure of our readiness to hand more coding work to agents is not how quickly pull requests merge on a Tuesday afternoon, but how calmly we can operate the software when it misbehaves in the middle of the night.
