import asyncio
from typing import Optional, Union, List

from pyrogram.filters import Filter
from pyrogram.types import Message as _Message, CallbackQuery

from .client import Client
from ..types import ListenerTypes
from ..utils import patch_into, should_patch


@patch_into(_Message)
class Message(_Message):
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
    async def ask(self,
                  text: str,
                  quote: bool | None = None,
                  message_filters: Optional[Filter] = None,
                  callback_filters: Optional[Filter] = None,
                  timeout: Optional[int] = None,
                  unallowed_click_alert: bool = True,
                  user_id: Union[Union[int, str], List[Union[int, str]]] = None,
                  message_id: Union[int, List[int]] = None,
                  inline_message_id: Union[str, List[str]] = None,
                  **kwargs,
                  ) -> _Message | CallbackQuery:

        message_task = asyncio.create_task(
            self._client.listen(message_filters, ListenerTypes.MESSAGE, timeout, unallowed_click_alert,
                                self.chat.id, user_id, message_id, inline_message_id))
        callback_task = asyncio.create_task(
            self._client.listen(callback_filters, ListenerTypes.CALLBACK_QUERY, timeout, unallowed_click_alert,
                                self.chat.id, user_id, message_id, inline_message_id))

        sent_message = None
        if text.strip() != "":
            sent_message = await self.reply_text(text, quote, **kwargs)

        response, pending = await asyncio.wait([message_task, callback_task], timeout=timeout,
                                               return_when=asyncio.FIRST_COMPLETED)

        for task in pending:
            task.cancel()

        for completed_task in response:
            completed_task = completed_task.result()
            if isinstance(completed_task, _Message):
                if completed_task:
                    completed_task.sent_message = sent_message
                return completed_task
            elif isinstance(completed_task, CallbackQuery):
                return completed_task
            else:
                raise RuntimeError("Unexpected update type received")

    @should_patch()
    async def ask_only(self,
                       text: str,
                       quote: bool | None = None,
                       message_filters: Optional[Filter] = None,
                       callback_filters: Optional[Filter] = None,
                       timeout: Optional[int] = None,
                       unallowed_click_alert: bool = True,
                       inline_message_id: Union[str, List[str]] = None,
                       **kwargs,
                       ) -> _Message | CallbackQuery:

        return await self.ask(text, quote, message_filters, callback_filters, timeout, unallowed_click_alert,
                              self.from_user.id, self.id, inline_message_id, **kwargs)

    @should_patch()
    async def ask_edit(
            self,
            text: str,
            message_filters: Optional[Filter] = None,
            callback_filters: Optional[Filter] = None,
            timeout: Optional[int] = None,
            unallowed_click_alert: bool = True,
            user_id: Union[Union[int, str], List[Union[int, str]]] = None,
            message_id: Union[int, List[int]] = None,
            inline_message_id: Union[str, List[str]] = None,
            *args,
            **kwargs,
    ):

        message_task = asyncio.create_task(
            self._client.listen(message_filters, ListenerTypes.MESSAGE, timeout, unallowed_click_alert,
                                self.chat.id, user_id, message_id, inline_message_id))
        callback_task = asyncio.create_task(
            self._client.listen(callback_filters, ListenerTypes.CALLBACK_QUERY, timeout, unallowed_click_alert,
                                self.chat.id, user_id, message_id, inline_message_id))

        sent_message = None
        if text.strip() != "":
            sent_message = await self.edit_text(text, *args, **kwargs)

        response, pending = await asyncio.wait([message_task, callback_task], timeout=timeout,
                                               return_when=asyncio.FIRST_COMPLETED)

        for task in pending:
            task.cancel()

        for completed_task in response:
            completed_task = completed_task.result()
            if isinstance(completed_task, _Message):
                if completed_task:
                    completed_task.sent_message = sent_message
                return completed_task
            elif isinstance(completed_task, CallbackQuery):
                return completed_task
            else:
                raise RuntimeError("Unexpected update type received")
