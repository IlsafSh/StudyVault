import dataclasses
import datetime
import weakref


class UnknownUser(Exception):
    pass


@dataclasses.dataclass(frozen=True)
class Session:
    user_id: int
    logged_in: datetime.datetime = dataclasses.field(default_factory=datetime.datetime.now)


class UserSessions:
    def __init__(self):
        self._sessions = weakref.WeakValueDictionary()
        self._user_id: int | None = None

    def add_session(self, session: Session) -> None:
        if self._user_id is None:
            self._user_id = session.user_id
            
        if self._user_id != session.user_id:
            raise UnknownUser(
                f"Невозможно добавить сессию пользователя {session.user_id}. "
                f"Хранилище принадлежит пользователю {self._user_id}."
            )
            
        self._sessions[id(session)] = session

    def __len__(self) -> int:
        return len(self._sessions)


if __name__ == "__main__":
    user_sessions = UserSessions()

    session1 = Session(user_id=1)
    session2 = Session(user_id=1)

    user_sessions.add_session(session1)
    user_sessions.add_session(session2)

    try:
        user_sessions.add_session(Session(user_id=2))
    except UnknownUser:
        pass  # Исключение успешно поймано

    assert len(user_sessions) == 2

    # Удаляем жесткие ссылки на объекты
    del session1
    del session2

    # Значения удалились из памяти, WeakValueDictionary автоматически очистил ключи
    assert len(user_sessions) == 0
    
    print("Все проверки пройдены успешно")