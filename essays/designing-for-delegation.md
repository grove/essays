# Designing for delegation

Suppose we want to add a new promotional discount rule to an order management system, say a bundle discount that applies only to certain product categories. On the surface, it looks like a routine change that an AI agent ought to handle with little supervision.

When the agent starts working, however, it finds that assumptions about discounts are scattered across checkout validation, invoice generation, refund calculation and a reporting query. To make the new rule work, it has to edit all four areas, including the code responsible for ensuring that refunds never exceed the amount collected. What looked like a low-risk feature now touches billing invariants we cannot afford to break.

It is tempting to treat this as a limitation of the model and wait for agents that can reason more reliably across tangled codebases. Even an experienced engineer would hesitate before making that change casually, though. Handing it to an agent simply exposes the coupling sooner. How safely we can delegate a task depends as much on the structure of the software as on the capability of the agent.

## Boundaries for humans and boundaries for agents

In his 1972 paper *On the Criteria To Be Used in Decomposing Systems into Modules*, David Parnas argued that module boundaries should be chosen to hide design decisions that are likely to change. If a decision lives inside a single module, it can be revised without disturbing the rest of the system.

For decades, we have valued those boundaries mostly for human reasons. Good boundaries limit how much of a system a person has to keep in mind at once, and as I argued in [Implementation and understanding](./implementation-and-understanding.md), they make it possible to understand one part of a codebase without having to read all of it.

When AI agents participate in development, those same boundaries do additional work, and two qualities matter much more than they used to.

The first is mechanical enforcement. Human teams rely heavily on unwritten conventions: everyone on the team eventually learns which helper must be called before writing to the ledger, or which module you do not touch without asking someone who knows the billing code. An agent working across fresh sessions does not carry that tribal knowledge, and it is strongly biased toward doing whatever makes the current task succeed and the tests pass. If a boundary exists only as a folder convention or a comment, an agent will cross it without hesitation, add a special case in the wrong place or duplicate logic to get past a failure. Boundaries for delegation have to be enforced by types, visibility rules, narrow APIs or repository permissions.

The second is locality of reasoning. Experienced maintainers often live comfortably with deep inheritance hierarchies, implicit framework wiring or shared utilities stretched across several features because they already hold the mental model in their heads. For an agent that has to gather context before making a change, scattered indirection turns a small adjustment into a tour of the repository. A self-contained module with explicit wiring is much easier for an agent to work on safely, even when it involves a little more repetition than a human author might have chosen.

## Separating guarantees from variation

Not every part of a system carries the same consequence when it goes wrong. In the order management system, payment ledger integrity and endpoint authorization are core guarantees. Promotional rules, email templates and export formats change frequently and should never be in a position to compromise them.

Look back at why the promotional discount rule was so awkward to change. Invoice generation, refund calculation and reporting were each re-interpreting raw discount rules on their own.

We can structure that domain differently. If checkout evaluates promotional rules once and records the outcome as immutable line-item price adjustments on the order, downstream components no longer need to know what kind of promotion produced a discount. Invoicing, refunds and reporting all work from settled amounts. Meanwhile, the invariant that refunds never exceed collected payments can live inside a single ledger component whose interface makes it impossible to record an unvalidated refund, backed by strict types or database constraints rather than a convention every caller has to remember.

Once that separation is in place, adding a new promotional rule touches only the pricing module. Even if the agent gets the rule completely wrong, it cannot corrupt the ledger or issue an over-refund, because the pricing code has no way to bypass the ledger's checks.

None of this is new; engineers have been trying to separate stable cores from volatile rules for decades. What changes is the payoff. Every invariant we move out of convention and into a structural choke point expands the part of the codebase where work can be delegated without close supervision.

## Making boundaries enforceable

If we want routine, independently verifiable changes to proceed with lighter human oversight, a question I explore further in [When code review becomes the work](./when-code-review-becomes-the-work.md), our review and permission rules can only be as sharp as the boundaries in the code.

When a subsystem sits behind a narrow interface with explicit contracts and independent verification checks, we can grant an agent wide latitude inside that module while denying it permission to alter the interface, the core guarantees or the checks themselves. If the agent makes a mistake, the blast radius stays local and the failure is much more likely to be caught at the boundary, provided the contract and its tests actually reflect what matters.

When modules share mutable state, rely on undocumented ordering assumptions or reach directly into each other's internals, no review rule can reliably separate a safe change from a dangerous one. A diff that claims to add a discount rule looks indistinguishable from one that subtly alters how refunds are accounted for. We end up either reviewing everything line by line or accepting risks we have not really evaluated.

## Designing modules to be replaced

Historically, we have been reluctant to rewrite working components because implementation was expensive. Once a module worked in production, we extended and patched it for years, even after its internal structure no longer matched the problem. That gave us a habit of building elaborate internal abstractions up front in the hope of accommodating future variations without a rewrite.

Cheaper implementation changes that calculation. Speculative internal flexibility has a real ongoing cost: extra layers of indirection, more context for an agent to load and more places for subtle assumptions to hide. Small modules with simple internals and clear external contracts become much more valuable. We can write an implementation that fits today's requirements straightforwardly, knowing that when requirements change substantially, replacing the internals behind a well-tested boundary is often cleaner and safer than layering another workaround onto an aging design.

There is an important limit to this idea. Replacing a stateless or computational component, such as a pricing calculator, an export formatter or a parser, is straightforward when its behavior is well captured at the boundary. Replacing a stateful component is a different matter. Modules that own persistent schemas, queues, wire formats or subtle undocumented behavior that callers have quietly come to rely on cannot be swapped out casually. In a storage engine, you can replace a compaction heuristic behind a stable interface far more easily than you can replace an on-disk format. Recognizing that difference helps us put our design discipline where it lasts: into durable data models, explicit contracts and narrow cores, while keeping the surrounding logic small enough to replace.

## Where designing for delegation breaks down

Clean boundaries are much easier to draw on a whiteboard than to maintain in a working system.

Parnas's principle depends on knowing which design decisions are likely to change. If we draw boundaries prematurely around a domain we do not yet understand, ordinary changes still cut across multiple modules, except now every edit also has to pass through extra interfaces and translation layers. Designing for delegation does not mean carving a system into tiny pieces before we know where the real seams are.

Protected interfaces also accumulate workarounds. When an agent runs into a narrow boundary that does not quite fit the task, it will often look for a way around it rather than stop to question the design: smuggling extra data through an existing field, duplicating part of a neighbor module's logic or pressuring the contract to grow optional parameters and loosely typed metadata bags. Eventually a legitimate requirement really does call for changing a core guarantee or moving a seam. Someone who understands the system still has to notice when workarounds are piling up and decide when a boundary has outlived its usefulness.

Most teams are not starting from a clean design either. They already live inside the tangled order management system from the opening example. Trying to re-architect an entire codebase up front so agents can work safely on it is a good way to spend months drawing speculative boxes. A more practical path aligns with [continuous cultivation of software](./continuous-cultivation-of-software.md): watch where routine changes repeatedly collide with high-consequence code, and use those collisions to decide which invariant-enforcing core or volatile module is worth untangling next.

## Architecture as an enabling investment

Architectural work is often treated with skepticism, and for good reason: it is easy to spend weeks designing for hypothetical futures that never arrive. Designing for delegation has a more immediate test. Does a proposed change in structure make ordinary work easier to isolate, understand and verify today?

If we shape our systems so that the consequences of a change stay proportional to its intent, we do not have to wait for agents capable of safely editing checkout, invoicing, refunds and reporting all at once. In the order management system, the point is to structure the domain so that adding a promotional discount rule never has to touch refund invariants.
