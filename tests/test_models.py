from models import Ticket
from models import Severity
from models import TicketStatus
from models import TicketBoard

def test_ticket_from_raw() -> None:
    ticket_1 = Ticket.from_raw("T1 | customer | high | open | 10 | vip, priority")
    assert ticket_1.severity is Severity.HIGH
    assert ticket_1.status is TicketStatus.OPEN
    assert ticket_1.tags == ("vip", "priority")
    assert ticket_1.ticket_id == "T1"
    assert ticket_1.customer == "customer"
    assert ticket_1.minutes_open == 10

def build_board() -> TicketBoard:
    ticket_board = TicketBoard()
    ticket_board.add(Ticket.from_raw("T1 | customer | high | open | 10 | vip, priority"))
    ticket_board.add(Ticket.from_raw("T2 | customer 2 | low | pending | 15 | priority"))
    ticket_board.add(Ticket.from_raw("T3 | customer 3 | critical | closed | 100 | urgent, vip, tag 3"))
    return ticket_board

def test_ticket_board_indexs_and_dunders() -> None:
    ticket_board = build_board()
    assert len(ticket_board) == 3
    assert "T1" in (ticket_board)
    ticket_ids = [tickets.ticket_id for tickets in ticket_board]
    assert ticket_ids == ["T1", "T2", "T3"]
    assert ticket_board.count == 3
    assert ticket_board.open_count == 1
    
def test_ticket_baord_queries() -> None:
    ticket_board = build_board()
    assert [active_ticket.ticket_id for active_ticket in ticket_board.active_tickets()] == ["T1", "T2"]
    assert [active_ticket.ticket_id for active_ticket in ticket_board.tickets_with_tag("priority")] == ["T1", "T2"]
    assert [active_ticket.ticket_id for active_ticket in ticket_board.sorted_by_age()] == ["T3", "T2", "T1"]