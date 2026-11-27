# Discovering what software should do

Suppose we want to introduce snapshots into a storage engine. We want applications to be able to continue reading the database as it existed at a particular point in time while other applications modify it.

One way of implementing this is to retain older versions of the data for as long as a snapshot needs them. But what happens if an application holds on to a snapshot for several days? Depending on the workload, the storage engine could eventually run out of disk space. Should we allow snapshots to expire? Should we refuse further writes? Should applications be required to tell the storage engine how long they intend to retain a snapshot?

These are questions about what the storage engine should do, but they need not have occurred to us before we began working on the implementation.

An AI agent given the task of implementing snapshots could encounter these questions and arrive at reasonable answers. We could subsequently review the implementation, find it satisfactory and merge it. In doing so, we would have made consequential decisions about the guarantees provided by the storage engine without ever having discussed them.

## Discovering requirements

In his essay [No Silver Bullet](https://www.seltzer.com/margo/teaching/CS508.19/background/NoSilverBullet.html), Fred Brooks argued that determining what software should do is one of the most difficult parts of developing it. He was sceptical of our ability to establish satisfactory requirements for a substantial piece of software before building and trying some version of it. He considered rapid prototyping one of the more promising ways of addressing this difficulty.

Much of what we learn during implementation concerns the problem we are trying to solve rather than the software itself.

Consider an order management system in which we want customers to be able to cancel orders before they have been dispatched. While implementing this feature, we discover that the warehouse sometimes reports a dispatch several hours after it has occurred. We cannot reliably determine whether an order can still be cancelled from the information available to the application.

We could work around this in the software, but it would be worth talking to the people operating the warehouse. How late in the dispatch process can they intervene? Does it make sense to allow cancellations once an order has been packed? We could discover that a small change to the warehouse's operating procedure would make the software simpler and provide a better service to customers.

There is a difference between a requirement that somebody has neglected to communicate and a question that nobody has yet considered. The distinction matters because the latter cannot be resolved by improving the communication between the people specifying the software and those implementing it. Somebody needs to investigate the problem.

Some of the most useful work an engineer does is recognising when a difficulty encountered during implementation warrants reconsidering what we are trying to achieve.

## Delegating decisions

As AI becomes more capable of implementing software, it is tempting to establish a division of work in which humans specify the requirements and agents implement them. This is a sensible arrangement where we have a good understanding of what we want. The difficulty is that we do not always know how well we understand a problem until we attempt to solve it.

Returning to the storage engine, suppose an agent decides that snapshots should expire after a configurable period. It implements expiration, makes sure that applications receive an appropriate error and documents the behaviour.

Whether this is a desirable property of the storage engine depends on what applications use snapshots for. If they are used to produce backups, an occasional interruption could be acceptable. If an application uses them to provide consistent reads across a lengthy computation, expiration complicates its design.

By the time we review the implementation, expiration has become part of the design. Our attention is directed towards whether it has been implemented correctly. We can spend a substantial amount of time reviewing the implementation and its accompanying tests without questioning whether snapshots should expire in the first place.

The problem is not that the agent has made a decision on our behalf. We delegate a great many decisions whenever we assign work to another engineer, and there is no particular reason to change that. Requiring agents to consult us about every ambiguity would make them tedious to work with.

But deciding how to implement snapshot expiration and deciding whether snapshots should expire are different kinds of decisions. The latter has consequences for every application using the feature. We need to recognise such decisions when they arise and give them the attention they deserve.

## Using implementation to investigate requirements

Cheaper implementation changes what we can afford to investigate.

Rather than committing to a design for snapshots, we could use experimental implementations to establish which guarantees we want the storage engine to provide.

It would also be worth investigating whether the applications that prompted us to consider snapshots in the first place actually need them to be long-lived. If the principal use case is producing backups, we could discover that a means of exporting a consistent copy of the database would serve them better. We would not necessarily need to introduce a general mechanism for retaining historical versions of the data.

There is nothing new about working this way. We have been building prototypes and conducting technical investigations for decades. But the cost of implementation limits how extensively we do it. We often choose between designs that we would have preferred to investigate further.

There is also a reluctance to discard experimental implementations once we have invested considerable effort in producing them. Prototypes have a tendency to find their way into production, along with decisions that were made for the convenience of conducting an experiment.

With the help of AI, we can afford to produce more implementations with little expectation of retaining them. We can pursue a design we suspect will not work simply because we would like to understand why. We can spend less time arguing about the likely consequences of a decision and more time investigating them.

This does not make all questions about requirements cheap to answer. In the order management example, no amount of experimentation with the application will tell us how the warehouse actually operates. We still need to go there and find out. But once we have a better understanding of its operations, we can try several ways of accommodating them in the software before committing to one.

## Investigations as development work

Much of the recent interest in specification-driven development is motivated by the difficulty of getting agents to implement what we want. Writing down our intentions more precisely is often helpful, and I expect specifications to become increasingly valuable as we delegate more development work.

But we should distinguish between the effort involved in expressing our intentions and the effort involved in arriving at them.

If we cannot agree on whether snapshots should expire, writing a more detailed specification does little to resolve the disagreement. We need to learn something that we do not currently know.

Rather than assigning an agent the task of implementing snapshots, we could give it an assignment along these lines:

> Investigate the consequences of supporting long-lived snapshots in the storage engine.
>
> Implement two experimental versions: one in which snapshots remain valid until released by the application, and one in which they expire after a configurable period.
>
> Run both versions under the same sustained write workload for ten minutes, with a mixture of short-lived snapshots and a snapshot retained for the duration of the experiment. Use an expiration period short enough to observe its effects during the experiment. Include a run without snapshots for comparison.
>
> Measure disk space consumption, compaction backlog and write latency. Examine what happens when the retained snapshot is released or expires, and what an application experiences when it attempts to read from an expired snapshot.
>
> Document the results, the limitations of the experiment and any questions about the desired behaviour that arose during implementation.
>
> The experimental implementations are not intended to be merged.

The result of this work would be a report accompanied by some experimental code and a reproducible workload. We could examine the measurements, challenge the assumptions behind the experiment and extend it where necessary.

We would still need to establish how representative the workload is of the applications using the storage engine. A ten-minute experiment tells us little about the behaviour of a database under several days of production traffic. But it gives us somewhere to start and helps us formulate better questions.

We could also investigate what would be involved in making the applications tolerate snapshot expiration. If accommodating expiration turns out to be difficult, we have learned something about the cost of imposing that restriction on users of the storage engine.

None of this work requires us to have decided that snapshots should expire. Nor does completing the investigation oblige us to introduce snapshots at all. The work is useful in helping us make those decisions.

I think it is worth making a distinction between this kind of assignment and an ordinary implementation assignment. When we ask somebody to implement a feature, there is an expectation that the work will result in a change to the software. Questions that arise along the way tend to be resolved with that objective in mind. An investigation can be successful even when its findings persuade us not to make the change.

This is also a natural extension of what I have previously described as [continuous cultivation of software](https://gist.github.com/grove/a58ce7b4cf86bcf05111d82c7de7aaf8). We can investigate the requirements of established software in much the same way. A restriction introduced several years ago can be subjected to experiments that would have been too expensive to conduct when the original decision was made. We could find that changes elsewhere in the system have made the restriction unnecessary, or that we misunderstood the problem in the first place.

## What we do with the time we save

There is an implicit assumption in much of the discussion about AI and software development that we know what we ought to build and that we would benefit from being able to build more of it.

That assumption is often wrong. Established software contains features we would not have built had we understood the problem better, restrictions we imposed without establishing whether they were necessary, and substantial amounts of code devoted to accommodating problems that could have been addressed outside the software.

All of this software has to be understood, maintained and taken into account when making subsequent changes. The cost of having built the wrong thing does not disappear because it was cheap to build.

If we spend all the time we save on implementation working our way further down the feature backlog, we should expect to accumulate more of this software. We will have less time to question each decision relative to the number of decisions being made.

We have an opportunity to conduct investigations that we could not previously justify, to try several approaches to problems for which we would previously have tried only one, and to become better acquainted with the circumstances in which our software is used.

The next time we debate the requirements of a feature, we should spend some of the time we have saved on implementation building something we have no intention of keeping.
