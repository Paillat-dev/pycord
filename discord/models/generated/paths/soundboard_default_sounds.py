from __future__ import annotations

from pydantic import BaseModel, Field, RootModel

from ..schemas import SoundboardSoundResponse


class SoundboardDefaultSoundsGetResponse(RootModel[list[SoundboardSoundResponse]]):
    root: list[SoundboardSoundResponse]
