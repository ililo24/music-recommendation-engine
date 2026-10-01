"""FastAPI dependencies (dependency injection).

Phase 0 provides only settings. Auth (``get_current_user``) and database
(``get_db``) dependencies are added in later phases.
"""

from typing import Annotated

from fastapi import Depends

from musicrec.core.config import Settings, get_settings

SettingsDep = Annotated[Settings, Depends(get_settings)]

__all__ = ["Settings", "SettingsDep", "get_settings"]
