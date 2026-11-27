# Implementation and understanding

One of the benefits of implementing a change to a piece of software is that we tend to understand the software better afterwards.

Suppose we want to change when a storage engine can reclaim old log segments. Before making the change, we need to understand how checkpointing works, when a checkpoint is considered durable and under what circumstances recovery depends on an older checkpoint. The implementation itself could amount to a few lines of code. Working out which lines to change is what takes time.

In the process, we often learn things about the storage engine that have little to do with the original task. We discover assumptions we were unaware of and come to appreciate design decisions that previously seemed questionable.

An AI agent given the same task can go through much the same process and produce an equally good implementation. But if we review the change and merge it, we have not necessarily acquired the understanding we would have acquired by doing the work ourselves.

For much of the history of software engineering, implementation and the acquisition of understanding have been closely connected. AI is beginning to separate them.

## Understanding and trust

Much of the current reluctance to delegate implementation to AI stems from uncertainty about the quality of its work. We feel a need to understand the code because we are not entirely comfortable trusting it.

Suppose, however, that we eventually have greater confidence in the implementations produced by AI than in those we produce ourselves. Would we still be concerned about the understanding we no longer acquire through implementation?

Engineering has always benefited from our ability to rely on things we do not fully understand. Few software engineers understand the internals of their compilers, and there is rarely a good reason for them to do so. Reliable abstractions allow us to devote our attention to other problems. I expect that AI will similarly allow us to stop concerning ourselves with many implementation details.

But some of the understanding we acquire during implementation is valuable for reasons other than establishing its correctness.

In the storage engine example, we might discover that retaining older log segments would allow us to recover from certain kinds of checkpoint corruption. Whether we want to support such recovery involves trade-offs between disk usage, performance and operational reliability. In working on the implementation, we have discovered a question about the requirements themselves.

Making a good decision about what the storage engine should guarantee requires an understanding of both the system and the circumstances in which it is used. That understanding remains valuable regardless of how reliably we can implement the decision.

## Programming as a way of learning

In his 1985 essay [Programming as Theory Building](https://doi.org/10.1016/0165-6074(85)90032-8), Peter Naur argued that the essential activity of programming is the development of a theory in the minds of the programmers. This theory enables them to relate the program to the problem it solves, account for its design and reason about possible modifications.

Anyone who has inherited a substantial software project will be familiar with the difficulty of acquiring this kind of understanding. Much of what experienced maintainers know comes from things they have attempted over the years. They remember why a seemingly obvious solution did not work, why a particular abstraction was introduced or why an earlier design was abandoned. These experiences inform subsequent decisions in ways that are difficult to capture fully in documentation.

Naur was concerned with what happens to a program when the people who possess its underlying theory are no longer around.

It is now possible to imagine something similar happening without the original maintainers ever leaving the project.

There is an economic aspect to this that is easy to overlook. When an organization pays an engineer to implement a feature, it is also paying, indirectly, for that engineer to become more knowledgeable about the system. Nobody needs to make a separate business case for the acquisition of understanding. It happens during work that the organization has already decided is worth doing.

As implementation and understanding become separated, this arrangement begins to change. The time spent acquiring understanding increasingly competes with time that could be spent delivering another feature. An organization can become considerably more efficient at producing software while inadvertently weakening one of the mechanisms through which it has traditionally developed engineering expertise.

## Understanding without implementation

Despite its benefits, implementation is a haphazard way of learning about software. What we learn depends largely on the features we happen to implement and the problems we happen to encounter. There are important properties of the systems we maintain that we have never investigated simply because they have given us no trouble.

With the help of AI, we can be more deliberate about what we investigate. We can examine the recovery protocol of a storage engine without any intention of changing it, explore its behavior under unusual failure conditions or investigate whether a simpler protocol can provide the same guarantees. Much of the practical work involved in preparing and conducting these experiments can be delegated.

One of the advantages of learning through implementation is that it confronts us with questions we would not otherwise have thought to ask. We discover gaps in our understanding by attempting things that turn out to be more difficult than we expected. Investigations guided solely by our existing understanding risk leaving those gaps undiscovered.

One source of questions for further investigation is implementation itself. An agent working on a feature encounters unexpected behavior, discovers dependencies and abandons approaches that turn out not to work. When we receive the finished implementation, we rarely see much of this. Yet some of what the agent encountered along the way may be more interesting to the maintainers than the change itself.

We can make a practice of examining such discoveries. We can also use experimental implementations, failure injection and attempts to simplify existing designs as means of exploring a system. These activities have value even when they produce no changes worth incorporating into the software.

Of course, having an agent conduct an investigation and write a report does not mean we have acquired an understanding of what it discovered. There is a considerable difference between reading an explanation of a recovery protocol and making a prediction about its behavior, discovering that the prediction is wrong and working out why.

What makes AI particularly interesting in this context is how much easier it becomes to pursue the questions that arise during such an investigation. We can try things that we would previously have dismissed as too laborious and follow an unexpected observation considerably further than we otherwise would.

## Cultivating understanding

We cannot maintain a detailed understanding of every part of the software for which we are responsible. Nor do we necessarily need to. If we can investigate an unfamiliar subsystem reliably and with relatively little effort, it is often reasonable to defer doing so until the need arises.

This gives us another reason to care about simplicity, explicit contracts, reproducible experiments and the preservation of design rationale. They make it easier for someone to acquire an understanding of the system when they need it. The ease with which software can be understood is itself an important engineering property.

This is one of the motivations behind what I have previously described as [continuous cultivation of software](./continuous-cultivation-of-software.md): the systematic investigation and improvement of existing software, independent of the immediate demands of feature development.

Some of this work can arise naturally from ordinary development. An unexpected discovery during implementation can become the subject of a subsequent investigation. An incident review can lead to a broader examination of the assumptions on which a subsystem depends. An engineer becoming acquainted with an unfamiliar part of the system can conduct experiments rather than rely entirely on reading code and documentation.

Other investigations need no more immediate justification than the importance of the questions they address. Understanding the failure guarantees of a storage engine before we have experienced a serious failure seems a perfectly reasonable use of engineering time.

A continuous stream of automated investigations could nevertheless leave the maintainers no more knowledgeable than they were before. We need to distinguish between accumulating knowledge about a project and developing the understanding of the people responsible for it. Making knowledge available helps, but acquiring understanding still requires effort on our part.

## A different way of working

If AI substantially reduces the effort required to implement software, I suspect that most of the effort we save will initially be spent implementing more software. This is what our existing engineering practices and measures of productivity encourage us to do.

But we also have an opportunity to reconsider how we develop expertise and how we spend our time as engineers. We can investigate design alternatives that we would previously have had to dismiss without much consideration. We can become better acquainted with the systems we maintain and explore questions that have remained unanswered for years because there has always been more pressing work to do.

I see little reason to preserve manual implementation solely for its educational value. It would be strange to insist on implementing something by hand in order to learn about it if we had more effective means of acquiring the same understanding.

We have spent decades developing better ways of producing software. It seems worth devoting some of our attention to developing better ways of understanding it.

If I am going to spend less time implementing a storage engine's recovery protocol, I would like to spend some of that time gaining a deeper understanding of what the protocol guarantees, what those guarantees depend on and whether they are the guarantees we ought to provide.