import ctypes
from collections import namedtuple
from contextlib import ExitStack
from ctypes import wintypes

from .models.graphics import GraphicsPage
from .models.physics import PhysicsPage
from .models.static import StaticPage

_kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
_kernel32.OpenFileMappingW.argtypes = (
    wintypes.DWORD,
    wintypes.BOOL,
    wintypes.LPCWSTR,
)
_kernel32.OpenFileMappingW.restype = wintypes.HANDLE
_kernel32.MapViewOfFile.argtypes = (
    wintypes.HANDLE,
    wintypes.DWORD,
    wintypes.DWORD,
    wintypes.DWORD,
    ctypes.c_size_t,
)
_kernel32.MapViewOfFile.restype = ctypes.c_void_p
_kernel32.UnmapViewOfFile.argtypes = (ctypes.c_void_p,)
_kernel32.UnmapViewOfFile.restype = wintypes.BOOL
_kernel32.CloseHandle.argtypes = (wintypes.HANDLE,)
_kernel32.CloseHandle.restype = wintypes.BOOL


Snapshot = namedtuple("Snapshot", ["static", "physics", "graphics"])


class ACEvoSharedMemory:
    """Keep EVO shared memory open inside a with block and return copied snapshots."""

    def __init__(self):
        self._resources = ExitStack()
        self._pages = {}

    def __enter__(self):
        if self._pages:
            raise RuntimeError("Close the reader first.")
        try:
            for name, page_type in (
                ("Local\\acevo_pmf_static", StaticPage),
                ("Local\\acevo_pmf_physics", PhysicsPage),
                ("Local\\acevo_pmf_graphics", GraphicsPage),
            ):
                self._pages[page_type] = self._open_page(name, page_type)
        except BaseException:
            self._close()
            raise
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._close()

    def _close(self):
        self._pages.clear()
        self._resources.close()

    def read_static(self):
        """Return snapshot of a static page. Updates when a new session loads."""
        return self._read_page(StaticPage)

    def read_physics(self):
        """Return snapshot of a physics page. Updates every simulation step."""
        return self._read_page(PhysicsPage)

    def read_graphics(self):
        """Return snapshot of a graphics page. Updates every rendered frame."""
        return self._read_page(GraphicsPage)

    def read_snapshot(self):
        """Return snapshot of all pages."""
        return Snapshot(self.read_static(), self.read_physics(), self.read_graphics())

    def _read_page(self, page_type):
        return page_type.from_buffer_copy(
            ctypes.string_at(self._pages[page_type], ctypes.sizeof(page_type))
        )

    def _open_page(self, name, page_type):
        handle = _kernel32.OpenFileMappingW(4, False, name)
        if not handle:
            error = ctypes.get_last_error()
            if error == 2:
                message = "The Assetto Corsa Evo shared memory is unavailable. Start a driving session."
                raise FileNotFoundError(message)
            raise ctypes.WinError(error)

        self._resources.callback(_kernel32.CloseHandle, handle)
        address = _kernel32.MapViewOfFile(handle, 4, 0, 0, ctypes.sizeof(page_type))
        if not address:
            raise ctypes.WinError(ctypes.get_last_error())
        self._resources.callback(_kernel32.UnmapViewOfFile, address)
        return address
