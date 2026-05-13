import dataclasses
import datetime
import typing


@dataclasses.dataclass
class Session:
    user_id: int
    logged_in: datetime.datetime = dataclasses.field(default_factory=datetime.datetime.now)
    logged_out: typing.Optional[datetime.datetime] = None
    

class SessionManager:
    def __init__(self):
        self._sessions: list[Session] = []

    def open_session(self, user_id: int) -> Session:
        session = Session(user_id=user_id)
        self._sessions.append(session)
        return session

    def __del__(self):
        logout_time = datetime.datetime.now()
        
        for session in self._sessions:
            if session.logged_out is None:
                session.logged_out = logout_time


if __name__ == "__main__":
    manager = SessionManager()

    session1 = manager.open_session(1)
    session2 = manager.open_session(2)

    assert session1.logged_out is None
    assert session2.logged_out is None

    del manager

    assert session1.logged_out is not None
    assert session2.logged_out is not None
    
    print("Все проверки пройдены успешно")