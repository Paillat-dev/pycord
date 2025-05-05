from __future__ import annotations

from pydantic import AnyUrl, BaseModel, Field, RootModel

from ..schemas import (
    ApplicationCommandAutocompleteCallbackRequest,
    CreateMessageInteractionCallbackRequest,
    LaunchActivityInteractionCallbackRequest,
    ModalInteractionCallbackRequest,
    PongInteractionCallbackRequest,
    UpdateMessageInteractionCallbackRequest,
)


class InteractionsInteractionIdInteractionTokenCallbackPostRequest(
    RootModel[
        ApplicationCommandAutocompleteCallbackRequest
        | CreateMessageInteractionCallbackRequest
        | LaunchActivityInteractionCallbackRequest
        | ModalInteractionCallbackRequest
        | PongInteractionCallbackRequest
        | UpdateMessageInteractionCallbackRequest
    ]
):
    root: (
        ApplicationCommandAutocompleteCallbackRequest
        | CreateMessageInteractionCallbackRequest
        | LaunchActivityInteractionCallbackRequest
        | ModalInteractionCallbackRequest
        | PongInteractionCallbackRequest
        | UpdateMessageInteractionCallbackRequest
    )
