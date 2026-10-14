For CampusFlow Pro integration, I'm implementing the SLA engine.

I propose tracking escalation with two ticket fields:

- escalation_cycle: integer starting at 0.
- escalated_cycle: integer or None, identifying the cycle already escalated.

On reopening, the cycle increments and the marker resets.

Your audit module should support recording an ESCALATE event with the ticket ID, actor, timestamp, before/after status, and the SLA cycle in `details`.

We need to coordinate event recording and ticket-state persistence so that successful escalation creates exactly one event per cycle, while failed operations create none.

Please confirm this contract before we integrate the modules.