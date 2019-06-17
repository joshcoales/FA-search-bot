import unittest
import uuid

from telegram import Chat


def generate_key():
    return str(uuid.uuid4())


class MockTelegramUpdate:

    def __init__(self):
        if self.__class__ == MockTelegramUpdate:
            raise NotImplementedError()
        self.message = None
        self.callback_query = None

    @staticmethod
    def with_message(message_id=None, chat_id=None, text=None, text_markdown_urled=None, chat_type=Chat.PRIVATE):
        return _MockTelegramMessage(
            message_id=message_id,
            chat_id=chat_id,
            text=text,
            text_markdown_urled=text_markdown_urled,
            chat_type=chat_type
        )

    @classmethod
    def with_callback_query(cls, data=None):
        return _MockTelegramCallback(
            data=data
        )

    @classmethod
    def with_command(cls, message_id=None, chat_id=None):
        return _MockTelegramCommand(
            message_id=message_id,
            chat_id=chat_id
        )

    @classmethod
    def with_inline_query(cls, query_id=None, query=None, offset=None):
        return _MockTelegramInlineQuery(
            query_id=query_id,
            query=query,
            offset=offset
        )


class _MockTelegramMessage(MockTelegramUpdate):

    def __init__(self, *, message_id=None, text=None, text_markdown_urled=None, chat_id=None, chat_type=None):
        super().__init__()
        # Set up message data
        self.message = _MockMessage(
            message_id=message_id,
            chat_id=chat_id,
            text=text,
            text_markdown_urled=text_markdown_urled,
            chat_type=chat_type
        )

    def with_photo(self, photo_file_id=None, caption=None):
        self.message.set_photo(photo_file_id, caption)
        return self

    def with_document(self, file_id=None, mime_type=None):
        self.message.set_document(file_id, mime_type)
        return self


class _MockTelegramCallback(MockTelegramUpdate):

    def __init__(self, *, data=None):
        super().__init__()
        self.callback_query = _MockCallback(data)

    def with_originating_message(self, message_id=None, chat_id=None):
        self.callback_query.set_message(message_id, chat_id)
        return self


class _MockTelegramCommand(MockTelegramUpdate):

    def __init__(self, *, message_id=None, chat_id=None):
        super().__init__()
        self.message = _MockMessage(
            message_id=message_id,
            chat_id=chat_id
        )


class _MockTelegramInlineQuery(MockTelegramUpdate):

    def __init__(self, query_id=None, query=None, offset=None):
        super().__init__()
        self.query_id = query_id
        self.query = query
        self.offset = offset
        # Set defaults
        if query_id is None:
            self.query_id = generate_key()
        if offset is None:
            self.offset = ""


class _MockMessage:

    def __init__(self, *, message_id=None, chat_id=None, text=None, text_markdown_urled=None, chat_type=None):
        self.message_id = message_id
        self.chat_id = chat_id
        self.text = text
        self.text_markdown_urled = text_markdown_urled or text
        self.chat = _MockChat(chat_type=chat_type)
        # Set defaults
        self.photo = []
        self.caption = None
        self.document = None
        if message_id is None:
            self.message_id = generate_key()
        if chat_id is None:
            self.chat_id = generate_key()
        if text_markdown_urled is None:
            self.text_markdown_urled = self.text

    def set_photo(self, photo_file_id, caption):
        # Defaults
        if photo_file_id is None:
            photo_file_id = generate_key()
        # Set values
        self.photo.append({"file_id": photo_file_id})
        self.caption = caption

    def set_document(self, file_id, mime_type):
        self.document = _MockDocument(
            file_id,
            mime_type
        )


class _MockChat:

    def __init__(self, chat_type=None):
        self.type = chat_type


class _MockDocument:

    def __init__(self, file_id=None, mime_type=None):
        self.file_id = file_id
        self.mime_type = mime_type
        # Set defaults
        if file_id is None:
            self.file_id = generate_key()


class _MockCallback:

    def __init__(self, data=None):
        self.data = data
        self.message = None

    def set_message(self, message_id, chat_id):
        self.message = _MockMessage(message_id=message_id, chat_id=chat_id)


class MockObjectsTest(unittest.TestCase):

    def test_cannot_create_update(self):
        try:
            update = MockTelegramUpdate()
            assert False, "Should have failed to create."
        except NotImplementedError:
            pass

    def test_can_create_message(self):
        update = MockTelegramUpdate.with_message()
        assert update.callback_query is None
        assert update.message is not None
        assert update.message.message_id is not None
        assert update.message.chat_id is not None
        assert isinstance(update.message.photo, list)
        assert len(update.message.photo) == 0

    def test_can_create_message_with_photo(self):
        update = MockTelegramUpdate.with_message().with_photo()
        assert update.callback_query is None
        assert update.message is not None
        assert update.message.message_id is not None
        assert update.message.chat_id is not None
        assert isinstance(update.message.photo, list)
        assert len(update.message.photo) == 1
        assert update.message.photo[0]["file_id"] is not None

    def test_can_create_message_with_document(self):
        update = MockTelegramUpdate.with_message().with_document()
        assert update.callback_query is None
        assert update.message is not None
        assert update.message.message_id is not None
        assert update.message.chat_id is not None
        assert isinstance(update.message.photo, list)
        assert len(update.message.photo) == 0
        assert update.message.document is not None
        assert isinstance(update.message.document, _MockDocument)
        assert update.message.document.file_id is not None
        assert update.message.document.mime_type is None

    def test_can_create_callback(self):
        update = MockTelegramUpdate.with_callback_query()
        assert update.message is None
        assert update.callback_query is not None
        assert update.callback_query.message is None

    def test_can_create_callback_with_message(self):
        update = MockTelegramUpdate.with_callback_query().with_originating_message()
        assert update.message is None
        assert update.callback_query is not None
        assert update.callback_query.message is not None
        assert update.callback_query.message.message_id is not None
        assert update.callback_query.message.chat_id is not None

    def test_can_create_command(self):
        update = MockTelegramUpdate.with_command()
        assert update.callback_query is None
        assert update.message is not None
        assert update.message.message_id is not None
        assert update.message.chat_id is not None