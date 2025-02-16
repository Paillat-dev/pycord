"""
The MIT License (MIT)

Copyright (c) 2015-2021 Rapptz
Copyright (c) 2021-present Pycord Development

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

from __future__ import annotations

from typing import Literal

from typing_extensions import NotRequired, TypedDict

from .snowflake import Snowflake

SKUType = Literal[2, 3, 5, 6]
EntitlementType = Literal[1, 2, 3, 4, 5, 6, 7, 8]
OwnerType = Literal[1, 2]
SubscriptionStatus = Literal[1, 2, 3]


class SKU(TypedDict):
    id: Snowflake
    type: SKUType
    application_id: Snowflake
    name: str
    slug: str
    flags: int


class Entitlement(TypedDict):
    id: Snowflake
    sku_id: Snowflake
    application_id: Snowflake
    user_id: NotRequired[Snowflake]
    type: EntitlementType
    deleted: bool
    starts_at: NotRequired[str]
    ends_at: NotRequired[str]
    guild_id: NotRequired[Snowflake]
    consumed: NotRequired[bool]


class CreateTestEntitlementPayload(TypedDict):
    sku_id: Snowflake
    owner_id: Snowflake
    owner_type: OwnerType


class Subscription(TypedDict):
    id: Snowflake
    user_id: Snowflake
    sku_ids: list[Snowflake]
    entitlement_ids: list[Snowflake]
    renewal_sku_ids: list[Snowflake]
    current_period_start: str
    current_period_end: str
    status: SubscriptionStatus
    canceled_at: str | None
    country: NotRequired[str]
