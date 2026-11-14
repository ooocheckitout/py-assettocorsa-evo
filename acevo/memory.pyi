from types import TracebackType
from typing import NamedTuple, Optional, Type

from .models.graphics import GraphicsPage
from .models.physics import PhysicsPage
from .models.static import StaticPage


class Snapshot(NamedTuple):
    static: StaticPage
    physics: PhysicsPage
    graphics: GraphicsPage


class ACEvoSharedMemory:
    def __init__(self) -> None: ...
    def __enter__(self) -> "ACEvoSharedMemory": ...
    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None: ...
    def read_static(self) -> StaticPage: ...
    def read_physics(self) -> PhysicsPage: ...
    def read_graphics(self) -> GraphicsPage: ...
    def read_snapshot(self) -> Snapshot: ...
