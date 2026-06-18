"""Unit tests for Bot handlers."""
import pytest
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from telegram import Update, User, Message, Chat, Voice, PhotoSize
from src.bot import ExpenseBot


@pytest.fixture
def mock_gemini():
    """Mock Gemini handler."""
    with patch('src.bot.get_gemini_handler') as mock:
        handler = Mock()
        handler.analyze_content = Mock(return_value={
            'date': '2026-02-07',
            'item': 'Coffee',
            'amount': 5.50,
            'paid_by': 'Me'
        })
        mock.return_value = handler
        yield handler


@pytest.fixture
def mock_sheets():
    """Mock Sheets handler."""
    with patch('src.bot.get_sheets_handler') as mock:
        handler = Mock()
        handler.add_expense = Mock(return_value=True)
        handler.get_recent_expenses = Mock(return_value=[
            ['2026-02-07', 'Coffee', '5.50', 'Me'],
            ['2026-02-06', 'Lunch', '15.00', 'John']
        ])
        mock.return_value = handler
        yield handler


@pytest.fixture
def bot(mock_gemini, mock_sheets):
    """Create ExpenseBot instance for testing."""
    with patch('src.bot.Application.builder') as mock_builder:
        mock_app = Mock()
        mock_builder.return_value.token.return_value.build.return_value = mock_app

        bot = ExpenseBot()
        bot.gemini = mock_gemini
        bot.sheets = mock_sheets
        return bot


@pytest.fixture
def mock_update():
    """Create a mock Telegram Update in a private chat."""
    update = Mock(spec=Update)
    update.effective_user = Mock(spec=User)
    update.effective_user.id = 12345
    update.effective_user.first_name = "TestUser"
    update.effective_chat = Mock(spec=Chat)
    update.effective_chat.id = -1001234567890
    update.effective_chat.type = 'private'
    update.message = Mock(spec=Message)
    update.message.reply_text = AsyncMock()
    return update


@pytest.fixture
def mock_group_update():
    """Create a mock Telegram Update in a group chat."""
    update = Mock(spec=Update)
    update.effective_user = Mock(spec=User)
    update.effective_user.id = 12345
    update.effective_user.first_name = "TestUser"
    update.effective_chat = Mock(spec=Chat)
    update.effective_chat.id = -1009876543210
    update.effective_chat.type = 'group'
    update.message = Mock(spec=Message)
    update.message.reply_text = AsyncMock()
    return update


class TestExpenseBot:
    """Test suite for ExpenseBot."""

    @pytest.mark.unit
    def test_bot_initialization(self, bot):
        """Test bot initialization."""
        assert bot is not None
        assert bot.gemini is not None
        assert bot.sheets is not None

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_cmd_start_private(self, bot, mock_update):
        """Test /start command in private chat."""
        await bot.cmd_start(mock_update, None)

        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args
        assert "Welcome" in call_args[0][0]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_cmd_start_group(self, bot, mock_group_update):
        """Test /start command in group chat."""
        await bot.cmd_start(mock_group_update, None)

        mock_group_update.message.reply_text.assert_called_once()
        call_args = mock_group_update.message.reply_text.call_args
        assert "Welcome" in call_args[0][0]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_cmd_help_private(self, bot, mock_update):
        """Test /help command in private chat."""
        await bot.cmd_help(mock_update, None)

        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args
        assert "How to Use" in call_args[0][0]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_cmd_help_group(self, bot, mock_group_update):
        """Test /help command in group chat."""
        await bot.cmd_help(mock_group_update, None)

        mock_group_update.message.reply_text.assert_called_once()
        call_args = mock_group_update.message.reply_text.call_args
        assert "How to Use" in call_args[0][0]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_cmd_summary_private(self, bot, mock_update):
        """Test /summary command in private chat."""
        await bot.cmd_summary(mock_update, None)

        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args
        assert "Recent Expenses" in call_args[0][0]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_cmd_summary_group(self, bot, mock_group_update):
        """Test /summary command in group chat."""
        await bot.cmd_summary(mock_group_update, None)

        mock_group_update.message.reply_text.assert_called_once()
        call_args = mock_group_update.message.reply_text.call_args
        assert "Recent Expenses" in call_args[0][0]

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_handle_text_private(self, bot, mock_update, mock_gemini, mock_sheets):
        """Test text message handling in private chat."""
        mock_update.message.text = "Coffee 5.50 USD"

        await bot.handle_text(mock_update, None)

        assert mock_update.message.reply_text.call_count == 2
        mock_gemini.analyze_content.assert_called_once_with(text="Coffee 5.50 USD", default_paid_by="TestUser")
        mock_sheets.add_expense.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_handle_text_group(self, bot, mock_group_update, mock_gemini, mock_sheets):
        """Test text message handling in group chat."""
        mock_group_update.message.text = "Dinner 25.50"

        await bot.handle_text(mock_group_update, None)

        assert mock_group_update.message.reply_text.call_count == 2
        mock_gemini.analyze_content.assert_called_once_with(text="Dinner 25.50", default_paid_by="TestUser")
        mock_sheets.add_expense.assert_called_once()

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_handle_photo_private(self, bot, mock_update, mock_gemini, mock_sheets):
        """Test photo message handling in private chat."""
        mock_photo = Mock(spec=PhotoSize)
        mock_photo_file = AsyncMock()
        mock_photo_file.download_to_drive = AsyncMock()
        mock_photo.get_file = AsyncMock(return_value=mock_photo_file)

        mock_update.message.photo = [mock_photo]
        mock_update.message.caption = "Paid by John"

        with patch('tempfile.NamedTemporaryFile') as mock_temp:
            mock_temp.return_value.__enter__.return_value.name = '/tmp/test.jpg'
            with patch('os.path.exists', return_value=True):
                with patch('os.remove'):
                    await bot.handle_photo(mock_update, None)

        assert mock_update.message.reply_text.call_count >= 1
        mock_gemini.analyze_content.assert_called_once()
        assert mock_gemini.analyze_content.call_args[1]['media_type'] == 'image'

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_handle_photo_group(self, bot, mock_group_update, mock_gemini, mock_sheets):
        """Test photo message handling in group chat."""
        mock_photo = Mock(spec=PhotoSize)
        mock_photo_file = AsyncMock()
        mock_photo_file.download_to_drive = AsyncMock()
        mock_photo.get_file = AsyncMock(return_value=mock_photo_file)

        mock_group_update.message.photo = [mock_photo]
        mock_group_update.message.caption = "Groceries"

        with patch('tempfile.NamedTemporaryFile') as mock_temp:
            mock_temp.return_value.__enter__.return_value.name = '/tmp/test.jpg'
            with patch('os.path.exists', return_value=True):
                with patch('os.remove'):
                    await bot.handle_photo(mock_group_update, None)

        assert mock_group_update.message.reply_text.call_count >= 1
        mock_gemini.analyze_content.assert_called_once()
        assert mock_gemini.analyze_content.call_args[1]['media_type'] == 'image'

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_handle_voice_private(self, bot, mock_update, mock_gemini, mock_sheets):
        """Test voice message handling in private chat."""
        mock_voice = Mock(spec=Voice)
        mock_voice_file = AsyncMock()
        mock_voice_file.download_to_drive = AsyncMock()
        mock_voice.get_file = AsyncMock(return_value=mock_voice_file)

        mock_update.message.voice = mock_voice

        with patch('tempfile.NamedTemporaryFile') as mock_temp:
            mock_temp.return_value.__enter__.return_value.name = '/tmp/test.ogg'
            with patch('os.path.exists', return_value=True):
                with patch('os.remove'):
                    await bot.handle_voice(mock_update, None)

        assert mock_update.message.reply_text.call_count >= 1
        mock_gemini.analyze_content.assert_called_once()
        assert mock_gemini.analyze_content.call_args[1]['media_type'] == 'audio'

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_handle_voice_group(self, bot, mock_group_update, mock_gemini, mock_sheets):
        """Test voice message handling in group chat."""
        mock_voice = Mock(spec=Voice)
        mock_voice_file = AsyncMock()
        mock_voice_file.download_to_drive = AsyncMock()
        mock_voice.get_file = AsyncMock(return_value=mock_voice_file)

        mock_group_update.message.voice = mock_voice

        with patch('tempfile.NamedTemporaryFile') as mock_temp:
            mock_temp.return_value.__enter__.return_value.name = '/tmp/test.ogg'
            with patch('os.path.exists', return_value=True):
                with patch('os.remove'):
                    await bot.handle_voice(mock_group_update, None)

        assert mock_group_update.message.reply_text.call_count >= 1
        mock_gemini.analyze_content.assert_called_once()
        assert mock_gemini.analyze_content.call_args[1]['media_type'] == 'audio'

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_handle_text_error(self, bot, mock_update, mock_gemini):
        """Test error handling in text message."""
        mock_update.message.text = "Coffee"
        mock_gemini.analyze_content.side_effect = Exception("API Error")

        await bot.handle_text(mock_update, None)

        assert mock_update.message.reply_text.call_count >= 1
        last_call = mock_update.message.reply_text.call_args_list[-1]
        assert "wrong" in last_call[0][0].lower() or "error" in last_call[0][0].lower()

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_cmd_summary_empty(self, bot, mock_update, mock_sheets):
        """Test /summary with no data."""
        mock_sheets.get_recent_expenses.return_value = []

        await bot.cmd_summary(mock_update, None)

        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args
        assert "No expenses" in call_args[0][0]
