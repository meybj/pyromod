from typing import Optional, Union, List

from pyrogram.filters import Filter
from pyrogram.types import Message as _Message, CallbackQuery, ReplyParameters

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
                  quote: bool | None = False,
                  filters: Optional[Filter] = None,
                  message_filters: Optional[Filter] = None,
                  callback_filters: Optional[Filter] = None,
                  listener_type: Union[ListenerTypes, List[ListenerTypes]] = ListenerTypes.MESSAGE,
                  timeout: Optional[int] = None,
                  unallowed_click_alert: bool = True,
                  reply_parameters: ReplyParameters = None,
                  user_id: Union[Union[int, str], List[Union[int, str]]] = None,
                  message_id: Union[int, List[int]] = None,
                  inline_message_id: Union[str, List[str]] = None,
                  **kwargs,
                  ) -> Optional[Union[_Message, CallbackQuery]]:

        if reply_parameters is None and quote:
            reply_parameters = ReplyParameters(
                message_id=self.id
            )

        return await self._client.ask(self.chat.id, text, filters, message_filters, callback_filters, listener_type,
                                      timeout, unallowed_click_alert, reply_parameters, user_id, message_id,
                                      inline_message_id, **kwargs)

    @should_patch()
    async def ask_only(self,
                       text: str,
                       quote: bool | None = None,
                       filters: Optional[Filter] = None, # New
                       message_filters: Optional[Filter] = None,
                       callback_filters: Optional[Filter] = None,
                       listener_type: Union[ListenerTypes, List[ListenerTypes]] = ListenerTypes.MESSAGE,
                       timeout: Optional[int] = None,
                       unallowed_click_alert: bool = True,
                       reply_parameters: "ReplyParameters" = None,
                       inline_message_id: Union[str, List[str]] = None,
                       **kwargs,
                       ) -> Optional[Union[_Message, CallbackQuery]]:

        return await self.ask(text, quote, filters, message_filters, callback_filters, listener_type, timeout,
                              unallowed_click_alert, reply_parameters, self.from_user.id, self.id,
                              inline_message_id, **kwargs)

    @should_patch()
    async def ask_edit(
            self,
            text: str,
            filters: Optional[Filter] = None,  # New
            message_filters: Optional[Filter] = None,
            callback_filters: Optional[Filter] = None,
            listener_type: Union[ListenerTypes, List[ListenerTypes]] = ListenerTypes.MESSAGE,
            timeout: Optional[int] = None,
            unallowed_click_alert: bool = True,
            user_id: Union[Union[int, str], List[Union[int, str]]] = None,
            message_id: Union[int, List[int]] = None,
            inline_message_id: Union[str, List[str]] = None,
            *args,
            **kwargs,
            ) -> Optional[Union[_Message, CallbackQuery]]:

        sent_message = None
        if text.strip() != "":
            sent_message = await self.edit_text(text, *args, **kwargs)

        message_id = message_id if message_id else self.id
        user_id = user_id if user_id else self.from_user.id

        completed_result = await self._client._create_and_wait_for_listeners(
            listener_type=listener_type,
            filters=filters,
            message_filters=message_filters,
            callback_filters=callback_filters,
            timeout=timeout,
            unallowed_click_alert=unallowed_click_alert,
            chat_id=self.chat.id,
            user_id=user_id,
            message_id=message_id,
            inline_message_id=inline_message_id,
        )

        if isinstance(completed_result, _Message) and completed_result:
            completed_result.sent_message = sent_message

        return completed_result