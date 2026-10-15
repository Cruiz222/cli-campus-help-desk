For CampusFlow Pro integration, I'm implementing the SLA engine.

I propose tracking escalation with two ticket fields:

- escalation_cycle: integer starting at 0.
- escalated_cycle: integer or None, identifying the cycle already escalated.

On reopening, the cycle increments and the marker resets.

Your audit module should support recording an ESCALATE event with the ticket ID, actor, timestamp, before/after status, and the SLA cycle in `details`.

We need to coordinate event recording and ticket-state persistence so that successful escalation creates exactly one event per cycle, while failed operations create none.

Please confirm this contract before we integrate the modules.




## Engineer B response

Confirmed, with these points:

- `escalation_cycle` (int, starts at 0) and `escalated_cycle` (int or None) are accepted as the ticket fields. Reopening increments the cycle and resets the marker.
- An ESCALATE audit event records `ticket_id`, `actor`, a timezone-aware UTC `timestamp`, `before_status` and `after_status`, with `{"sla_cycle": <n>}` in `details`. Escalation does not change status, so before and after are equal.
- Exactly one ESCALATE event is allowed per ticket per cycle. A repeated escalation check in the same cycle records nothing.
- An event is recorded only after the ticket operation succeeds. A rejected operation changes neither the ticket nor the event history.
- Tickets and events are saved together in the schema-v2 document, so a successful operation never leaves a ticket change without its event, or the reverse.