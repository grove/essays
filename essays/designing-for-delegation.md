# Designing for delegation

Suppose we want to add a new promotional discount rule to an order management system. On the surface, it looks like a routine change that an AI agent should be able to implement with minimal supervision.

When the agent starts working, however, it discovers that assumptions about discounts are scattered across checkout validation, invoice generation, refund calculation and a reporting query. To implement the rule, it has to modify all four areas, including the code responsible for ensuring that refunds never exceed the amount collected. What began as a low-risk change has become entangled with billing invariants we cannot afford to get wrong.

Whether a task can be safely delegated to an agent depends less on the capability of the model than on the structure of the software.

## Boundaries for humans and boundaries for agents

In his 1972 paper *On the Criteria To Be Used in Decomposing Systems into Modules*, David Parnas argued that module boundaries should be chosen to hide design decisions that are likely to change. If a decision is contained within a single module, it can be altered without disturbing the rest of the system.

For decades, we have designed software architecture primarily around human cognitive load and organizational structure. Good boundaries let a team work on one part of a system without having to keep the whole system in mind.

When AI agents participate in development, boundaries take on an additional role. They define the scope of safe delegation. A clear boundary limits how much context an agent needs to load, what files it needs permission to touch and what evidence is required to verify its work.

In a poorly structured system, small changes leak across unrelated concerns. Every task requires understanding large parts of the codebase and reviewing wide diffs that mix trivial adjustments with sensitive logic. In a well-bounded system, routine work stays contained.

## Separating guarantees from variation

Not all code in a system carries the same risk.

In a storage engine, the write-ahead log, checkpointing and recovery paths enforce core durability guarantees. A mistake there can corrupt customer data. By contrast, a new administrative command or a diagnostic metric carries far lower consequence.

In the order management system, payment ledger integrity and endpoint authorization are high-consequence guarantees. Promotional rules, email templates and export formats change frequently and should not be able to compromise them.

Designing for delegation means separating these layers deliberately. High-consequence guarantees should be enforced structurally at narrow, well-protected choke points rather than left to convention across dozens of call sites. If refunds are always validated by a single ledger component with strict invariants, and authorization is enforced centrally at endpoint registration rather than remembered inside every handler, an agent modifying a promotional rule or adding a new view cannot easily violate those rules by accident.

This is not a new architectural principle. What changes with AI is the return on investing in it. Every invariant we move from human convention into structural enforcement expands the area of the codebase where work can be delegated with confidence.

## Blast radius and authority

In [When code review becomes the work](./when-code-review-becomes-the-work.md), I suggested that routine, independently verifiable changes should be able to proceed without individual human approval, while changes to core guarantees retain close human involvement.

That distinction is difficult to enforce if core guarantees and routine features live in the same modules. Permissions and review policies can only be as crisp as the boundaries in the codebase.

When a subsystem has a narrow interface, explicit contracts and independent verification checks, we can grant an agent broad freedom inside that boundary while denying it authority to alter the contract or the checks themselves. If the agent makes a mistake, the blast radius is limited to that component and the failure is caught at the boundary.

When modules share mutable state, rely on undocumented ordering assumptions or reach directly into each other's internals, no review rule can reliably separate safe changes from dangerous ones. We end up either reviewing everything manually or accepting risks we do not understand.

## Designing modules to be replaced

Historically, we have been cautious about rewriting existing components because implementation was expensive. Once a module worked, we tended to extend and patch it for years, even after its internal design no longer suited the problem.

Cheaper implementation shifts that trade-off. If a component is small, cleanly isolated behind a clear interface and backed by behavioral tests at its boundary, replacing its internals becomes far less risky than layering another workaround onto an aging design.

This changes what we should value in software design. Intricate internal abstractions built to anticipate every future variation become less attractive; they add complexity and context cost without paying for themselves. Small, replaceable modules with clear external contracts become much more valuable. We can keep internal implementations simple for today's requirements, knowing that when requirements change substantially, we can replace the module rather than bend it out of shape.

This also reinforces [continuous cultivation of software](./continuous-cultivation-of-software.md). Investigating whether a tangled subsystem can be split into a small invariant-enforcing core and simpler replaceable parts is an investment that pays off on every subsequent change.

## Architecture as an enabling investment

Architectural work is sometimes viewed with skepticism because it is easy to over-design for hypothetical futures that never arrive. Designing for delegation has a more immediate test: does this structure make ordinary changes easier to isolate, verify and trust today?

We do not need to wait for AI agents to become capable of reasoning reliably across an entire tangled monolith before we can benefit from delegating work to them. We can shape our systems so that the consequences of a change are proportional to its intent.

In the order management system, the goal is not to build an agent clever enough to edit checkout, invoicing, refunds and reporting safely all at once. It is to structure the system so that adding a discount rule never needed to touch refund invariants in the first place.
