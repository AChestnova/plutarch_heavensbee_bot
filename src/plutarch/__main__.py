#!/usr/bin/env python
# pylint: disable=unused-argument
# This program is dedicated to the public domain under the CC0 license.

"""Simple inline keyboard bot with multiple CallbackQueryHandlers.

This Bot uses the Application class to handle the bot.
First, a few callback functions are defined as callback query handler. Then, those functions are
passed to the Application and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Example of a bot that uses inline keyboard that has multiple CallbackQueryHandlers arranged in a
ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line to stop the bot.
"""
import logging

from dynaconf import Dynaconf
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

settings = Dynaconf(
    envvar_prefix="PLUTARCH",
    settings_file="settings.toml",
    sysenv_fallback=True,
)

# Stages
START_ROUTES, END_ROUTES, HELPERS = range(3)
# Callback data
ONE, TWO, THREE, FOUR, FIVE = range(5)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Send message on `/start`."""
    # Get user that sent /start and log his name
    user = update.message.from_user
    logger.info("User %s started the conversation.", user.first_name)
    # Build InlineKeyboard where each button has a displayed text
    # and a string as callback_data
    # The keyboard is a list of button rows, where each row is in turn
    # a list (hence `[[...]]`).
    keyboard = [
            [InlineKeyboardButton("Join The Games", callback_data=str(ONE))],
            [InlineKeyboardButton("Yield The Arena", callback_data=str(TWO))],
            [InlineKeyboardButton("Show The Roster", callback_data=str(THREE))],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    # Send message with text and appended InlineKeyboard
    await update.message.reply_text("Greetings! What may I help you with?", reply_markup=reply_markup)
    # Tell ConversationHandler that we're in state `FIRST` now
    return START_ROUTES


async def start_over(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Prompt same text & keyboard as `start` does but not as new message"""
    # Get CallbackQuery from Update
    query = update.callback_query
    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    await query.answer()
    keyboard = [
            [InlineKeyboardButton("Join The Games", callback_data=str(ONE))],
            [InlineKeyboardButton("Yield The Arena", callback_data=str(TWO))],
            [InlineKeyboardButton("Show The Roster", callback_data=str(THREE))],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    # Instead of sending a new message, edit the message that
    # originated the CallbackQuery. This gives the feeling of an
    # interactive menu.
    await query.edit_message_text(text="Of course! What else?", reply_markup=reply_markup)
    return START_ROUTES


async def join_the_games(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show new choice of buttons"""
    query = update.callback_query
    await query.answer()
    keyboard = [
        [
            InlineKeyboardButton("This week", callback_data=str(ONE)),
            InlineKeyboardButton("Next week", callback_data=str(TWO)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text=f"Which week you'd like to play?", reply_markup=reply_markup
    )
    return HELPERS

async def join_this_week(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show new choice of buttons. This is the end point of the conversation."""
    query = update.callback_query
    await query.answer()

    game_date = "2025-03-08"
    await query.edit_message_text(
        text=f"Successfully registered on {game_date}. See you next time!"
    )
    # Transfer to conversation state `SECOND`
    return ConversationHandler.END

async def join_next_week(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show new choice of buttons. This is the end point of the conversation."""
    query = update.callback_query
    await query.answer()

    game_date = "2025-03-16"
    await query.answer()
    await query.edit_message_text(text=f"Successfully registered on {game_date}! See you next time!")
    return ConversationHandler.END

async def see_the_roster(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show new choice of buttons"""
    query = update.callback_query
    await query.answer()
    keyboard = [
    [
        InlineKeyboardButton("Yes, let's do it again!", callback_data=str(ONE)),
        InlineKeyboardButton("Nah, I've had enough ...", callback_data=str(TWO)),
    ]
]
    reply_markup = InlineKeyboardMarkup(keyboard)

    participants = ["Kostya", "Nastya"]
    await query.edit_message_text(
        text=f"Current list of participants {participants}. Do you want to start over?", reply_markup=reply_markup
    )
    return END_ROUTES


async def yield_the_arena(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show new choice of buttons. This is the end point of the conversation."""
    query = update.callback_query
    await query.answer()
    keyboard = [
        [
            InlineKeyboardButton("This week", callback_data=str(THREE)),
            InlineKeyboardButton("Next week", callback_data=str(FOUR)),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text="Which week you'd like to yield?", reply_markup=reply_markup
    )
    # Transfer to conversation state `SECOND`
    return HELPERS

async def sell_this_week(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show new choice of buttons. This is the end point of the conversation."""
    query = update.callback_query
    await query.answer()

    game_date = "2025-03-08"
    await query.answer()
    await query.edit_message_text(text=f"Added slot {game_date} to auction! See you next time!")
    return ConversationHandler.END

async def sell_next_week(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show new choice of buttons. This is the end point of the conversation."""
    query = update.callback_query
    await query.answer()

    game_date = "2025-03-16"
    await query.answer()
    await query.edit_message_text(text=f"Added slot {game_date} to auction! See you next time!")
    return ConversationHandler.END

async def end(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Returns `ConversationHandler.END`, which tells the
    ConversationHandler that the conversation is over.
    """
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text="See you next time!")
    return ConversationHandler.END


def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(settings.telegram.token).build()

    # Setup conversation handler with the states FIRST and SECOND
    # Use the pattern parameter to pass CallbackQueries with specific
    # data pattern to the corresponding handlers.
    # ^ means "start of line/string"
    # $ means "end of line/string"
    # So ^ABC$ will only allow 'ABC'
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            START_ROUTES: [
                CallbackQueryHandler(join_the_games, pattern="^" + str(ONE) + "$"),
                CallbackQueryHandler(yield_the_arena, pattern="^" + str(TWO) + "$"),
                CallbackQueryHandler(see_the_roster, pattern="^" + str(THREE) + "$"),
            ],
            END_ROUTES: [
                CallbackQueryHandler(start_over, pattern="^" + str(ONE) + "$"),
                CallbackQueryHandler(end, pattern="^" + str(TWO) + "$"),
            ],
            HELPERS: [
                CallbackQueryHandler(join_this_week, pattern="^" + str(ONE) + "$"),
                CallbackQueryHandler(join_next_week, pattern="^" + str(TWO) + "$"),
                CallbackQueryHandler(sell_this_week, pattern="^" + str(THREE) + "$"),
                CallbackQueryHandler(sell_next_week, pattern="^" + str(FOUR) + "$"),
            ]
        },
        fallbacks=[CommandHandler("start", start)],
    )

    # Add ConversationHandler to application that will be used for handling updates
    application.add_handler(conv_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
