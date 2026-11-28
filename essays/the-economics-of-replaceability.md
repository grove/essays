# The economics of replaceability

A shipping quote component has accumulated years of exceptions. Each carrier uses different service names. Some quotes expire after a few minutes; others remain valid until a particular local time. A customer agreement overrides one surcharge, and an old integration expects unavailable services to appear in a particular order.

An engineer asks an agent to write a simpler implementation. It produces plausible code quickly. The difficult question arrives afterwards: what would give the team sufficient confidence to use it?

This is a hypothetical system, but it exposes a useful distinction. Making a replacement inexpensive to write changes only part of the economics. The team must still understand which behavior matters, establish that the replacement provides it, move callers and state, and operate the result. If all that knowledge lives implicitly in the old implementation, the apparent saving may disappear before the first customer sees a quote.

[Designing for delegation](./designing-for-delegation.md) argues for small components with explicit boundaries. Replaceability adds another question: what must survive a change of implementation, and how will we know that it has?

## Decide what deserves continuity

For the shipping component, a useful boundary might accept a shipment and return available services, prices, delivery estimates and quote expiry conditions. The implementation can change while callers continue using those concepts.

That interface is only the beginning. A quoted price may be a commitment for the duration of the quote. An unavailable service must not be presented as bookable. A customer agreement must apply to the intended account. These requirements need to survive a replacement even if the data structures and algorithms change completely.

Other behavior may have survived by accident. Suppose the old component always lists a particular carrier first because it was the first integration written. A caller might interpret that ordering as a recommendation. Preserving the order would maintain compatibility, but it would also preserve an accidental product decision. Sorting by price would change customer behavior without anyone choosing to do so explicitly.

Investigating the replacement gives the team a reason to settle that question. The product owner can decide what recommendation the interface should make; engineers can then make that meaning explicit and update callers deliberately. The replacement need not preserve every quirk, but changing a quirk with a consumer is still a change to the product.

This is why a full comparison against the old implementation is useful evidence and an incomplete specification. Agreement can preserve a mistake. Disagreement can reveal either a regression or an improvement. Someone needs a reason to choose between them.

## Keep evidence close to the obligations

The team can collect a small set of reviewed shipping situations: a quote used just before expiry, a carrier unavailable for the destination, a surcharge excluded by an agreement, and a service whose advertised delivery estimate depends on a cutoff time. Each case needs an explanation of the expected result and where that expectation came from.

Those cases become more useful when they are independent of the current component's internal representation. If every test constructs private objects and inspects helper methods, replacing the implementation requires rewriting the evidence at the same time. A comparison through the meaningful boundary can continue answering the same question while the internals change.

Independence does not mean an immutable test suite. Carrier terms and customer agreements change. The evidence must change with them, and the team must be able to tell a revised obligation from an implementation defect. Keeping old expectations indefinitely would make the component easy to replace only with another obsolete component.

The same care applies to operational behavior. Price and availability can match while the new implementation sends too many carrier requests, responds too slowly or hides useful failure information. A replay needs representative conditions, and the people who will operate the component need a way to understand its failures. [Knowing what constitutes convincing evidence](./knowing-what-constitutes-convincing-evidence.md) and [Operating software you didn't write](./operating-software-you-didnt-write.md) develop those questions.

For a first attempt, choose one carrier behind the existing interface. Ask the replacement to handle a few reviewed cases and deliberately give the comparison a wrong candidate. If the comparison cannot detect a known error, generating more candidates is premature.

## Replacement has a migration cost even when the function looks pure

A quote calculator appears stateless until checkout needs to honor a quote created by the previous version. The calculation may be replaceable, while the commitments already made by it remain in force.

The team needs to know which version and terms produced an outstanding quote, what has been stored, and whether the new component can interpret it. One option is to keep the old interpreter for those quotes until they expire. Another is to use a stable stored representation that both versions understand. The right choice depends on the actual commitments; a clean new function does not settle it.

Now suppose the replacement also changes how quote records are stored. Comparing current calculations will not establish that historical records remain usable. The migration needs its own evidence and recovery plan. Replacing calculation logic and replacing its persistent representation can be separate investments, allowing one to proceed while the other remains unwarranted.

Stripe's account of [online migrations](https://stripe.com/blog/online-migrations) describes moving reads and writes in stages while comparing old and new behavior. It is a useful example of the work surrounding a data-model change. It does not establish that a similar sequence will be sufficient for every component or that dual writes are straightforward.

Martin Fowler's [Strangler Fig](https://martinfowler.com/bliki/StranglerFigApplication.html) describes gradual modernization through smaller replacements and temporary structures that let old and new systems coexist. For the shipping component, an adapter or a period of running both implementations may be part of the investment. Include their upkeep and removal in the plan; leaving every previous implementation active would turn renewal into another form of accumulation.

## Spend on the next change before building a general replacement machine

If the carrier's current integration is costly to maintain, the first useful investment might be clarifying the quote contract and making one comparison possible. The team need not build a framework for continuously rewriting every component.

That comparison has several possible uses. It could reject a replacement. It could expose an error in the existing implementation. It could establish that the current design is adequate and that the proposed simplification does not justify migration. All three answers may save the team from choosing on the basis of an attractive diff.

Suppose the comparison later helps evaluate a new carrier. The earlier work has now contributed to a different capability: the team can investigate what a carrier provides without first committing to a production integration. Reviewed situations help expose missing semantics, and the existing boundary gives the experiment somewhere to connect.

That is a plausible compounding connection. To establish it, follow the later work. What could be reused? Which expectations needed revision? How much adaptation and review remained? If every new carrier needs a different contract, the original comparison may still be useful for maintenance without being the foundation of a broader capability.

AI could make small alternative implementations cheap enough to use in this investigation. The comparison cost then becomes especially important. Producing five candidates is wasteful if a scarce expert has to reconstruct the same evidence for each one. The investment worth making may be a clearer question and a reusable way to answer it.

## Know when keeping the component is cheaper

Replaceability creates an option. Exercising it should depend on the work that needs doing.

A stable component with a small carrying cost may be best left alone. An obscure but reliable implementation does not become a worthwhile rewrite merely because an agent can produce something easier to read. The replacement may introduce new defects, discard useful operational knowledge or require a migration larger than the problem it addresses.

The case becomes stronger when a component repeatedly obstructs valuable changes, depends on a retiring service or requires increasing effort to operate. Even then, compare replacement with a local repair and with removing the capability. A carrier that no customer needs may deserve retirement rather than a better adapter. [The economics of removing software](./the-economics-of-removing-software.md) follows that investigation.

The boundary itself may also be wrong. If every new requirement forces the team to change the quote interface and several callers, investing further in interchangeable implementations could make the existing design harder to question. A useful investigation must be allowed to conclude that the division of responsibilities needs changing.

There is a cost to preserving optionality too. General interfaces, comparison environments and retained scenarios need owners. Their value depends on credible future decisions, not on the number of components they could theoretically accommodate. Keep the simplest arrangement that helps with work the team has reason to expect.

## Practice understanding while it is inexpensive to recover

A component can be easy for an agent to replace while becoming difficult for the team to explain. If the reviewed scenarios are maintained without anyone understanding the commitments behind them, a later change may invalidate an assumption that no check expresses.

Use replacement investigations to exercise that understanding. Before running a case, ask an engineer to predict what happens when a quote expires between selection and booking. Ask which evidence supports the prediction and what the system should tell the customer. Then inspect the result and pursue any disagreement. This follows the approach in [Implementation and understanding](./implementation-and-understanding.md): completing the implementation and acquiring a useful mental model are different outcomes.

The engineer does not need to memorize every carrier adapter. They need to know which promises the system makes, where the evidence is incomplete and how to investigate an unfamiliar case. A clear boundary and a repeatable experiment make that learning less dependent on having written the original code.

On the next proposed replacement, start with the obligation that made it necessary. If the team can state it, test it, trace the migration and explain what will remain uncertain, the old implementation has become less costly to leave behind. If it cannot, the next investment is probably in that understanding.
