import asyncio
import os
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from lilybud420.lilybud420 import Bot
from highrise import User, Position, AnchorPosition

# Mock the simpleaudio library
@pytest.fixture(autouse=True)
def mock_simpleaudio():
    with patch('simpleaudio.WaveObject') as mock_wave_object:
        mock_wave_object.from_wave_file.return_value.play.return_value = MagicMock()
        yield

@pytest.fixture
def bot():
    test_bot = Bot()
    test_bot.highrise = AsyncMock() # Mock the highrise API
    test_bot.music_folder = "test_mp3" # Use a test music folder
    return test_bot

@pytest.fixture
def mock_user():
    return User(id="123", username="test_user")

@pytest.mark.asyncio
async def test_play_command_no_song_name(bot, mock_user):
    await bot.on_chat(mock_user, "/play")
    bot.highrise.send_chat.assert_called_with("Usage: /play <song_name>")

@pytest.mark.asyncio
async def test_play_command_song_not_found(bot, mock_user):
    with patch('os.path.exists', return_value=False):
        await bot.on_chat(mock_user, "/play non_existent_song")
        bot.highrise.send_chat.assert_called_with("Song 'non_existent_song' not found.")

@pytest.mark.asyncio
async def test_list_songs_no_songs(bot, mock_user):
    with patch('os.listdir', return_value=[]):
        await bot.on_chat(mock_user, "/list")
        bot.highrise.send_chat.assert_called_with("No songs found in the music folder.")

@pytest.mark.asyncio
async def test_list_songs_with_songs(bot, mock_user):
    with patch('os.listdir', return_value=["song1.mp3", "song2.mp3"]):
        await bot.on_chat(mock_user, "/list")
        bot.highrise.send_chat.assert_called_with("Available songs:\nsong1\nsong2")

@pytest.mark.asyncio
async def test_pause_command_no_song_playing(bot, mock_user):
    bot.is_playing = False
    await bot.on_chat(mock_user, "/pause")
    bot.highrise.send_chat.assert_called_with("No song is currently playing or it's already paused.")

@pytest.mark.asyncio
async def test_resume_command_no_song_paused(bot, mock_user):
    bot.is_paused = False
    await bot.on_chat(mock_user, "/resume")
    bot.highrise.send_chat.assert_called_with("No song is paused to resume.")

@pytest.mark.asyncio
async def test_stop_command_no_song_playing(bot, mock_user):
    bot.is_playing = False
    bot.is_paused = False
    await bot.on_chat(mock_user, "/stop")
    bot.highrise.send_chat.assert_called_with("No song is currently playing.")

@pytest.mark.asyncio
async def test_dance_all_users(bot, mock_user):
    # Mock the User object returned by get_room_users to have an id
    mock_room_user = MagicMock(spec=User)
    mock_room_user.id = "user1"
    bot.highrise.get_room_users.return_value = [mock_room_user]
    await bot.on_chat(mock_user, "/dance_all")
    bot.highrise.send_emote.assert_called_with('emote-dance', "user1")
    bot.highrise.send_chat.assert_called_with(f"Everyone is dancing thanks to {mock_user.username}!")

@pytest.mark.asyncio
async def test_set_volume_valid(bot, mock_user):
    await bot.on_chat(mock_user, "/volume 0.5")
    assert bot.volume == 0.5
    bot.highrise.send_chat.assert_called_with(f"Volume set to 50% by {mock_user.username}. (Note: This is a placeholder as simpleaudio does not support direct volume control.)")

@pytest.mark.asyncio
async def test_set_volume_invalid_range(bot, mock_user):
    await bot.on_chat(mock_user, "/volume 1.5")
    assert bot.volume == 1.0 # Should remain unchanged
    bot.highrise.send_chat.assert_called_with("Volume level must be between 0.0 and 1.0.")

@pytest.mark.asyncio
async def test_set_volume_invalid_input(bot, mock_user):
    await bot.on_chat(mock_user, "/volume abc")
    assert bot.volume == 1.0 # Should remain unchanged
    bot.highrise.send_chat.assert_called_with("Invalid volume level. Please use a number between 0.0 and 1.0.")

@pytest.mark.asyncio
async def test_show_queue_empty(bot, mock_user):
    await bot.on_chat(mock_user, "/queue")
    bot.highrise.send_chat.assert_called_with("The queue is empty.")

@pytest.mark.asyncio
async def test_show_queue_with_songs(bot, mock_user):
    # Add some songs to the queue
    with patch('os.path.exists', return_value=True):
        await bot.add_to_queue("songA", mock_user)
        await bot.add_to_queue("songB", mock_user)
    
    # Mock the current song playing
    bot.current_song = "songX"

    await bot.on_chat(mock_user, "/queue")
    # The queue will be consumed and then re-added, so we need to check the content of the message
    # The order of songs in the queue might vary due to asyncio.Queue implementation details
    # So we'll check for the presence of expected strings rather than exact match
    call_args = bot.highrise.send_chat.call_args[0][0]
    assert "Current queue:" in call_args
    assert "songX (Now Playing)" in call_args
    assert "songA" in call_args
    assert "songB" in call_args
