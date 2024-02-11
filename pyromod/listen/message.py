from typing import Optional, Union, List

import pyrogram
from pyrogram.filters import Filter

from .client import Client
from ..types import ListenerTypes
from ..utils import patch_into, should_patch


@patch_into(pyrogram.types.messages_and_media.message.Message)
class Message(pyrogram.types.messages_and_media.message.Message):
    _client: Client

    @should_patch()
    async def wait_for_click(
            self,
            from_user_id: Optional[Union[Union[int, str], List[Union[int, str]]]] = None,
            timeout: Optional[int] = None,
            filters=None,
            alert: Union[str, bool] = True,
    ):
        message_id = getattr(self, "id", getattr(self, "message_id", None))

        return await self._client.listen(
            listener_type=ListenerTypes.CALLBACK_QUERY,
            timeout=timeout,
            filters=filters,
            unallowed_click_alert=alert,
            chat_id=self.chat.id,
            user_id=from_user_id,
            message_id=message_id,
        )

    @should_patch()
    async def ask(
            self,
            text: str,
            quote: bool | None = None,
            filters: Optional[Filter] = None,
            listener_type: ListenerTypes = ListenerTypes.MESSAGE,
            timeout: Optional[int] = None,
            unallowed_click_alert: bool = True,
            user_id: Union[Union[int, str], List[Union[int, str]]] = None,
            message_id: Union[int, List[int]] = None,
            inline_message_id: Union[str, List[str]] = None,
            *args,
            **kwargs,
    ):
        sent_message = None
        if text.strip() != "":
            sent_message = await self.reply_text(text, quote, *args, **kwargs)

        response = await self._client.listen(
            filters=filters,
            listener_type=listener_type,
            timeout=timeout,
            unallowed_click_alert=unallowed_click_alert,
            chat_id=self.chat.id,
            user_id=user_id,
            message_id=message_id,
            inline_message_id=inline_message_id,
        )
        if response:
            response.sent_message = sent_message

        return response

    @should_patch()
    async def ask_edit_text(
            self,
            text: str,
            filters: Optional[Filter] = None,
            listener_type: ListenerTypes = ListenerTypes.MESSAGE,
            timeout: Optional[int] = None,
            unallowed_click_alert: bool = True,
            user_id: Union[Union[int, str], List[Union[int, str]]] = None,
            message_id: Union[int, List[int]] = None,
            inline_message_id: Union[str, List[str]] = None,
            *args,
            **kwargs,
    ):
        sent_message = None
        if text.strip() != "":
            sent_message = await self.edit_text(text, *args, **kwargs)

        response = await self._client.listen(
            filters=filters,
            listener_type=listener_type,
            timeout=timeout,
            unallowed_click_alert=unallowed_click_alert,
            chat_id=self.chat.id,
            user_id=user_id,
            message_id=message_id,
            inline_message_id=inline_message_id,
        )
        if response:
            response.sent_message = sent_message

        return response
