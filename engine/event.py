from enum import IntEnum, auto

class EventType(IntEnum):
    Null = 0
    WindowResized = auto()
    MouseScrolled = auto()
    KeyPressedEvent = auto()

class Event:
    def __init__(self):
        self.handled = False
        self.name = 'Null'
        self.type = EventType.Null

class WindowResizedEvent(Event):
    def __init__(self, width: int, height: int):
        super().__init__()
        self.width = width
        self.height = height
        self.name = 'window_resized'
        self.type = EventType.WindowResized

class MouseScrolledEvent(Event):
    def __init__(self, x: float, y: float):
        super().__init__()
        self.x = x
        self.y = y
        self.name = 'mouse_scrolled'
        self.type = EventType.MouseScrolled

class KeyPressedEvent(Event):
    def __init__(self, key: int, repeated: bool):
        self.key = key
        self.repeated = repeated
        self.name = 'key_pressed'
        self.type = EventType.KeyPressedEvent
