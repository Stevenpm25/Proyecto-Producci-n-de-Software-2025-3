from typing import Callable, Dict, List, Any

class EventBus:
    def __init__(self) -> None:
        self._subs: Dict[str, List[Callable[[Any], None]]] = {}
    def subscribe(self, event: str, fn: Callable[[Any], None]) -> None:
        self._subs.setdefault(event, []).append(fn)
    def publish(self, event: str, payload: Any) -> None:
        for fn in self._subs.get(event, []):
            fn(payload)

bus = EventBus()
