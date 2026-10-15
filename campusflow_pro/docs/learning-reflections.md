# CampusFlow Pro — Learning Reflections

**Project:** CampusFlow Pro
**Team:** Engineer A and Engineer B
**Date:** October 15, 2026

## Engineer A — My Learning Reflection

### What I learned from this project

Working on CampusFlow Pro helped me understand software development beyond just writing code that works.

Before this project, I mostly focused on getting individual functions to produce the correct result. But while working on the SLA engine and persistence, I realized that I also needed to think about how different parts of the application communicate and what happens when something goes wrong.

One important lesson was understanding how deadlines should work. At first, calculating an SLA deadline seemed straightforward. But when I started considering exact deadline boundaries, reopening tickets, and repeated escalation checks, I realized there were more cases to handle than I expected.

I also learned more about data integrity. When saving tickets to JSON, it is not enough to simply write the updated data to a file. I needed to consider what would happen if validation failed or if the application encountered an error while saving.

### The most challenging part

One of the most challenging parts for me was integrating the new SLA behavior with the existing attention queue.

The new SLA engine used stored deadlines, while the older queue calculated deadlines using its existing rules.

Both approaches made sense in their own context, but they did not always produce the same result.

I learned that when working on an existing codebase, introducing a better approach does not automatically mean I should remove the old behavior.

We needed to support the new schema while preserving compatibility with older tickets.

### Working with another engineer

Working with Engineer B helped me understand the importance of communication during development.

We were responsible for different parts of the project, but some of those parts depended on each other.

For example, my escalation logic needed to work with her audit events. We had to agree on the fields used to track escalation and the information recorded when an escalation happened.

This taught me that even when developers work on separate modules, they still need clear agreements about how those modules will interact.

### How I used AI

I used AI mainly to understand unfamiliar concepts, discuss possible solutions, and identify edge cases I might have missed.

However, I also learned that AI suggestions need to be checked against the actual code and requirements.

The attention-queue integration was a useful example. The suggested approach needed adjustment because the existing application still had legacy behavior that we needed to preserve.

Instead of accepting the suggestion immediately, I compared the behavior and used tests to verify the final decision.

### What I would improve next time

If I were starting a similar project again, I would spend more time agreeing on shared interfaces before implementing features.

I would also write down important assumptions earlier, especially where one module depends on another.

I think this would reduce integration problems and make it easier for both engineers to understand what the other person expects.

I would also like to learn more about database transactions and concurrency because the project showed me some of the limitations of JSON-based persistence.

### Final thoughts

Overall, this project gave me more confidence working with an existing Python codebase.

I learned more about testing, application structure, persistence, integration, Git, and collaboration.

I still have a lot to learn, but I now understand better why developers need to think about reliability and maintainability, not just whether their code runs successfully.

---