from __future__ import annotations

from pydantic import BaseModel, RootModel

from ..schemas import VoiceRegionResponse


class VoiceRegionsGetResponse(RootModel[list[VoiceRegionResponse]]):
    root: list[VoiceRegionResponse]
