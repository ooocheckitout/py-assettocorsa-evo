from ctypes import LittleEndianStructure


class StaticPage(LittleEndianStructure):
    sm_version: bytes
    ac_evo_version: bytes
    session: int
    session_name: bytes
    event_id: int
    session_id: int
    starting_grip: int
    starting_ambient_temperature_c: float
    starting_ground_temperature_c: float
    is_static_weather: bool
    is_timed_race: bool
    is_online: bool
    number_of_sessions: int
    nation: bytes
    longitude: float
    latitude: float
    track: bytes
    track_configuration: bytes
    track_length_m: float
