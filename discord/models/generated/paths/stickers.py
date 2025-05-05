from __future__ import annotations

from pydantic import BaseModel, Field, RootModel

from ..schemas import GuildStickerResponse, StandardStickerResponse


class StickersStickerIdGetResponse(
    RootModel[GuildStickerResponse | StandardStickerResponse]
):
    root: GuildStickerResponse | StandardStickerResponse
