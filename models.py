from enum import Enum
from dataclasses import dataclass

# 1. Build a support ticket board. The board owns tickets and indexes them.
# 2. Create enums severity, ticket status.
# 3. Create dataclass Ticket(ticket_id, customer, severity, status, minutes_open, tags) and validate fields, property active, class method from raw
# Raw format: ticket_id | customer | ... | tag1, tag2
# Create class SeveritySummary(severity, count, active_count)
# Create class TicketBoard that stores tickets, maintains indexes by severity and status, supports len and in.
# Exposes count, open count, averege minutes open, methods: active_tickets, tickets_with_tag, severity_summaries, sorted_by_age
# Create base class escalation policy with should_escalate(ticket) -> bool:
# Sub-classes: critical_or_old_policy, tag based policy, composit escalation policy
# Create escalated tickets, sort by: minutes open DESC, ticket id ascending. Use a lambda function.
# Write tests for parsing, indexes, list comprehansion queries and escalation policies used polymorphically.

class Severity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class TicketStatus(Enum):
    OPEN = "open"
    PENDING = "pending"
    CLOSED = "closed"
    
@dataclass(frozen = True)
class Ticket:
    
    ticket_id: str
    customer: str
    severity: Severity
    status: TicketStatus
    minutes_open: int
    tags: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.ticket_id.strip():
            raise ValueError("Ticket ID cannot be empty")
        if not self.customer.strip():
            raise ValueError("Customer cannot be empty")
        if self.minutes_open < 0:
            raise ValueError("Minutes oppen cannout be lower than zero")
        object.__setattr__{
            self,
            "tags",
            tuple(tag.strip().lower() for tag in self.tags if tag.strip()),
        }

    @property
    def active(self) -> bool:
        return self.status is not TicketStatus.CLOSED

    @classmethod   
    def from_raw(cls, line: str) -> Ticket:
        parts = [part.strip() for part in line.split("|")]
        if len(parts) != 6:
            raise ValueError("Ticket line must have six fields")
        ticket_id, customer, severity, status, minutes_open, tags = parts
        return cls(
            ticket_id = ticket_id,
            customer = customer,
            severity = Severity(severity.lower()),
            status = TicketStatus(status.lower()),
            minutes_open = int(minutes_open),
            tags = tuple(tags.split(","))
        )
    
@dataclass(frozen = True)
class SeveritySummary:
    
    severity: Severity
    count: int
    active_count: int

class TicketBoard:
    def __init__(self) -> None:
        self._tickets: list[Ticket] = []
        self._by_severity: dict{Severity, list[Ticket]} = {
            severity: [] for severity in Severity
        }
        self._by_status: dict{TicketStatus, list[Ticket]} = {}

    
