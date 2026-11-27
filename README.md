# Software that improves with age

*Essays on software engineering in the age of AI*

Much of the discussion about AI in software development focuses on producing more code faster. When implementation becomes cheaper, however, it alters the relative economics of every other engineering activity: discovery, design, understanding, verification, operations and maintenance. It also separates benefits we once acquired automatically by writing code by hand.

Cheaper code generation does not automatically save a team time overall, because review, ambiguous requirements and verification can easily absorb the difference. What changes is which kinds of engineering work become practical. Across the collection runs a recurring choice: we can put cheaper implementation toward changing software faster, or we can invest it in improving the conditions under which future changes are made. These essays explore what that choice looks like across the lifecycle, and how understanding, boundaries, verification, operational legibility and simplicity reinforce one another over the life of a system.

## Reading order

The essays can be read independently, though they build on one another in the order below:

1. **[Continuous cultivation of software](./essays/continuous-cultivation-of-software.md)** — Frames continuous cultivation as the ongoing practice of tending existing software, and introduces *software farms* as a complement to software factories for organizing proactive, bounded investigation.
2. **[Discovering what software should do](./essays/discovering-what-software-should-do.md)** — Argues that requirements are often discovered rather than merely specified, and shows how cheap throwaway implementations and bounded investigations can inform consequential decisions before committing to production code.
3. **[Implementation and understanding](./essays/implementation-and-understanding.md)** — Examines how delegating implementation separates producing code from building a mental model of the system, and argues for deliberate practices to cultivate engineering understanding.
4. **[Designing for delegation](./essays/designing-for-delegation.md)** — Explores how clear module boundaries, structural enforcement of core guarantees and small replaceable components determine what work can be safely delegated to agents.
5. **[When code review becomes the work](./essays/when-code-review-becomes-the-work.md)** — Looks at what happens when verification becomes the bottleneck and reviewing agent output replaces the rewarding parts of engineering, proposing upstream investigation, durable verification instruments and bounded autonomy.
6. **[Knowing what constitutes convincing evidence](./essays/knowing-what-constitutes-convincing-evidence.md)** — Examines why passing tests generated alongside code can become circular confirmation, and how independent properties, fault injection and proportionate verification build justified confidence.
7. **[Operating software you didn't write](./essays/operating-software-you-didnt-write.md)** — Follows delegated and autonomous changes into production, looking at operational accountability, understanding under incident pressure, operational legibility and closing the loop with cultivation.
8. **[The economics of removing software](./essays/the-economics-of-removing-software.md)** — Addresses the growing asymmetry between adding and deleting code when implementation is cheap, and how teams can practice deliberate subtraction to keep systems small enough to understand.
9. **[Software that improves with age](./essays/software-that-improves-with-age.md)** — Brings the collection together around two feedback loops, examining how cheaper implementation can accelerate decay or feed a self-reinforcing cycle in which a system's accumulated experience becomes an engineering asset rather than a liability.

## License

Licensed under the [Apache License 2.0](./LICENSE).
