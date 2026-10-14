"""Summary metrics for CampusFlow Pro."""

from collections import Counter

from campusflow_pro.sla.attention_queue import attention_queue
from campusflow_pro.ticket_fields import get_field


def build_report(tickets, now=None):
    tickets = list(tickets)
    by_status = Counter(str(get_field(t, "status")).lower() for t in tickets)
    by_priority = Counter(str(get_field(t, "priority")).lower() for t in tickets)
    queue = attention_queue(tickets, now)

    return {
        "total": len(tickets),
        "by_status": dict(by_status),
        "by_priority": dict(by_priority),
        "sla_breached": sum(1 for i in queue if i["state"] == "breached"),
        "sla_at_risk": sum(1 for i in queue if i["state"] == "at_risk"),
    }