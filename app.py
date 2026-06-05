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



