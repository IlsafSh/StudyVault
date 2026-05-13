import dataclasses
import datetime
import weakref


@dataclasses.dataclass(frozen=True)
class Session:
    user_id: int
    logged_in: datetime.datetime = dataclasses.field(default_factory=datetime.datetime.now)


class SessionsCache:
    def __init__(self):
        self._cache = weakref.WeakValueDictionary()
        self._hit_count = 0

    @property
    def hit_count(self) -> int:
        return self._hit_count
        
    def get_session(self, user_id: int) -> Session:
        session = self._cache.get(user_id)
        
        if session is not None:
            self._hit_count += 1
            return session
            
        new_session = Session(user_id=user_id)
        self._cache[user_id] = new_session
        
        return new_session

    def __len__(self) -> int:
        return len(self._cache)


if __name__ == "__main__":
    cache = SessionsCache()

    session1 = cache.get_session(1)
    session2 = cache.get_session(2)

    assert session1.user_id == 1
    assert session2.user_id == 2

    assert len(cache) == 2

    assert cache.hit_count == 0
    
    cache.get_session(1)
    cache.get_session(1)
    assert cache.hit_count == 2

    del session1
    del session2

    assert len(cache) == 0
    
    print("Все проверки пройдены успешно")