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

## Engineer B — My Learning Reflection

### What I learned from this project

I built the audit history, duplicate detection, the SLA attention queue, reports and the service layer that connects them to the original ticket functions. The main lesson was that a feature isn't finished when it works alone. My modules passed their own tests, but they only became useful once they matched the ticket format, timestamps and event rules that the rest of the project used.

### The most challenging part

The hardest part was timestamps. My first attention queue rejected timestamps without a timezone, but the original app creates tickets with `datetime.now()`, so every real ticket would have been rejected. I changed the queue to treat a naive `created_at` as local time. After the schema-v2 work, that rule applies only to legacy tickets without a `due_at`, and schema-v2 tickets use their stored deadline.

### Working with Engineer A

Engineer A proposed the escalation fields in the integration contract. When I replied, I first wrote that the ESCALATE event stored `sla_cycle` in its details. Searching the code showed the real key is `escalation_cycle`, so I corrected the contract before sending it. This taught me that an agreement between two people has to be checked against the code, not written from memory.

### Knowledge Lab result and what I got wrong

I scored 6/10. I answered Q1, Q3, Q4, Q5, Q6 and Q7 correctly and got four wrong:

- **Q2 (priority):** I answered Medium. Low urgency with 10 affected users is High, because the rule gives high priority when affected users reach 10, whatever the urgency.
- **Q8 (AI suggests `eval()` for JSON):** I chose "copy it". The correct answer is to reject it, because `eval()` runs arbitrary Python. Parsing should use `json.loads()` followed by validation.
- **Q9 (duplicate warning):** I answered "ignore normalization". The correct answer is to warn and ask for confirmation, because titles that match after trimming whitespace and ignoring case may be duplicates.
- **Q10 (rejected operation):** I answered "reset to zero". The event count must stay unchanged, because only successful operations create events.

The Q9 and Q10 answers are the most useful to reflect on, because I implemented those exact behaviours and my own tests check them (`test_duplicate_declined` and `test_failed_operations_record_nothing`). Q8 matters too, because my learning log is about checking AI suggestions against evidence, and here I picked the unsafe suggestion. The lesson is that knowing what the code does is not the same as being able to state the rule when asked a question.

### How I used AI

I used AI to draft modules, tests and documents, and I found real errors in its output by checking it against the repository: the timestamp assumption, the `sla_cycle` key, and a generic task list that did not match what had already been merged. The four cycles in my learning log show these cases.

### What I would improve next time

I would read the existing ticket code and the agreed contract before writing a module, instead of after. I would also revise for the quiz topics that I answered wrongly, especially priority rules and safe JSON handling.

### Final thoughts

This project taught me more about integration, testing and review than about any single module. The mistakes in the quiz were useful, because they showed which rules I still need to learn properly.
