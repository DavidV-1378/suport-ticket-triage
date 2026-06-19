from enum import Enum
from dataclasses import dataclass

# 1. Build a support ticket board. The board owns tickets and indexes them.
# 2. Create enums severity, ticket status.
# 3. Create dataclass Ticket(ticket_id, customer, severity, status, minutes_open, tags) and validate fields, property active, class method from raw
# Raw format: ticket_id | customer | ... | tag1, tag2
# Create class SeveritySummary(severity, count, active_count)
# Create class TicketBoard that stores tickets, maintains indexes by severity and status, supports len, in and iter.
# Exposes count, open count, averege minutes open, methods: active_tickets, tickets_with_tag, severity_summaries, sorted_by_age, add_tickets.
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
        self._by_severity: dict[Severity, list[Ticket]] = {
            severity: [] for severity in Severity
        }
        self._by_status: dict[TicketStatus, list[Ticket]] = {
            status: [] for status in TicketStatus
        }

    def __len__(self) -> int:
        return len(self._tickets)
    
    def __contains__(self, ticket_id: str) -> bool:
        return any(ticket.ticket_id == ticket_id for ticket in self._tickets)
    
    def __iter__(self):
        return iter(self._tickets)
    
    @property
    def count(self) -> int:
        return len(self._tickets)
    
    @property
    def open_count(self) -> int:
        return len(self._by_status[TicketStatus.OPEN])
    
    @property
    def avearge_minutes_open(self) -> float:
        if not self._tickets:
            return 0.0
        return sum(ticket.minutes_open for ticket in self._tickets) / len(self._tickets)
    
    def add(self, ticket: Ticket) -> None:
        self._tickets.append(ticket)
        self._by_severity[ticket.severity].append(ticket)
        self._by_status[ticket.status].append(ticket)

    def active_tickets(self) -> list[Ticket]:
        return [ticket for ticket in self._tickets if ticket.active]

    def tickets_with_tag(self, tag: str) -> list[Ticket]:
        normalised_tag = tag.strip().lower()
        return [ticket for ticket in self._tickets if normalised_tag in ticket.tags]
    
    def severity_summaries(self) -> list[SeveritySummary]:
        return [
            SeveritySummary(
                severity = severity,
                count = len(tickets),
                active_count = len([ticket for ticket in tickets if ticket.active])
            )
            for severity, tickets in self._by_severity.items()
            if tickets
        ]
    
    def sorted_by_age(self) -> list[Ticket]:
        return sorted(
            self._tickets,
            key = lambda ticket: (-ticket.minutes_open, ticket.ticket_id)
        )

class EscalationPolicy:
    def should_escalate(self, ticket) -> bool:
        raise NotImplementedError
    
class CriticalOrOldPolicy(EscalationPolicy): 
    def __init__(self, max_minutes: int) -> None:
        if max_minutes < 0:
            raise ValueError("Max minutes cannot be lower than zero")
        self._max_minutes = max_minutes
        
    def should_escalate(self, ticket) -> bool:
        return (
            ticket.active
            and (
                ticket.severity is Severity.CRITICAL
                or ticket.minutes_open >= self._max_minutes
            )
            
        )
    
class TagBasedPolicy(EscalationPolicy):
    def __init__(self, escalation_tag: set[str]) -> None:
        self._escalation_tag = {tag.strip().lower() for tag in escalation_tag}

    def should_escalate(self, ticket) -> bool:
        return ticket.active and any(tag in self._escalation_tag for tag in ticket.tags)
    

class CompositeEscaltionPolicy(EscalationPolicy):
    def __init__(self, escalate_policies: list[EscalationPolicy]) -> None:
        if not escalate_policies:
            raise ValueError("Escalte ploicies list cannot be empty")
        self._policies = list(escalate_policies)
    
    def should_escalate(self, ticket) -> bool:
        return any(policy.should_escalate(ticket) for policy in self._policies)
    
    def escalated_tickets(self, escaltion_policy: EscalationPolicy, ticket_board: TicketBoard) -> list[Ticket]:
        tickets = [ticket for ticket in ticket_board if escaltion_policy.should_escalate(ticket)]

        return sorted(tickets, key = lambda ticket: (-ticket.minutes_open, ticket.ticket_id))
    
    

    