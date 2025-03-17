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
from plutarch import Plutarch
from helpers import get_this_sunday, get_next_sunday
from dynaconf import Dynaconf
from datetime import datetime 
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

plutarch = Plutarch()

settings = Dynaconf(
    envvar_prefix="PLUTARCH",
    settings_file="settings.toml",
    sysenv_fallback=True,
)

START_ROUTES, END_ROUTES, HELPERS = range(3)

# 3 horizontally splitted buttons
START_REPLY_MARKUP = InlineKeyboardMarkup([
            [InlineKeyboardButton("Join The Games", callback_data="join_the_games")],
            [InlineKeyboardButton("Yield The Arena", callback_data="leave_the_games")],
            [InlineKeyboardButton("Show The Roster", callback_data="see_the_roster")],
    ])

# 2 vertically splitted buttons
END_REPLY_MARKUP = InlineKeyboardMarkup([[
    InlineKeyboardButton("Yes, let's do it again!", callback_data="start_over"),
    InlineKeyboardButton("Nah, I've had enough ...", callback_data="end"),
    ]])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Send message on `/start`."""
    # Get user that sent /start and log his name
    user = update.message.from_user
    context.bot_data["user_id"] = user.name
    # Send message with text and appended InlineKeyboard
    await update.message.reply_text("Greetings! What may I help you with?", reply_markup=START_REPLY_MARKUP)
    # Tell ConversationHandler that we're in state `FIRST` now
    return START_ROUTES


async def end(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Returns `ConversationHandler.END`, which tells the
    ConversationHandler that the conversation is over.
    """
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text="See you next time!")
    return ConversationHandler.END


async def start_over(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Prompt same text & keyboard as `start` does but not as new message"""
    # Get CallbackQuery from Update
    query = update.callback_query
    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    await query.answer()
    # Instead of sending a new message, edit the message that
    # originated the CallbackQuery. This gives the feeling of an
    # interactive menu.
    await query.edit_message_text(text="Of course! What else?", reply_markup=START_REPLY_MARKUP)
    return START_ROUTES


async def join_the_games(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Propose to join a game in this sunday or sunday in 2 weeks"""
    query = update.callback_query
    await query.answer()

    this_sunday = get_this_sunday().strftime("%Y-%m-%d")
    in_two_weeks = get_next_sunday().strftime("%Y-%m-%d")
    keyboard = [
        [
            InlineKeyboardButton("This week", callback_data=f"join_game:{this_sunday}"),
            InlineKeyboardButton("Next week", callback_data=f"join_game:{in_two_weeks}"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text=f"Which week you'd like to play?", reply_markup=reply_markup
    )
    return HELPERS


async def join_game(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Calls Plutarch to register user on a given date. 
    Obtains date from callback_date and user from context
    """
    query = update.callback_query
    await query.answer()

    game_date = query.data.split(':')[1]
    user_id = context.bot_data["user_id"]

    
    success, reason = plutarch.register(user_id, game_date)
    
    if success:
        reply = f"You were registered for a game on {game_date}!"
    else:
        reply = f"You cannot join the game: {reason}"

    await query.edit_message_text(
        text=reply+"\n\nDo you want to start over?", reply_markup=END_REPLY_MARKUP
    )
    return END_ROUTES


async def leave_the_games(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Propose to leave a game in this sunday or sunday in 2 weeks"""

    query = update.callback_query
    await query.answer()

    this_sunday = get_this_sunday().strftime("%Y-%m-%d")
    in_two_weeks = get_next_sunday().strftime("%Y-%m-%d")

    keyboard = [
        [
            InlineKeyboardButton("This week", callback_data=f"leave_game:{this_sunday}"),
            InlineKeyboardButton("Next week", callback_data=f"leave_game:{in_two_weeks}"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        text="Which week you'd like to yield?", reply_markup=reply_markup
    )
    # Transfer to conversation state `SECOND`
    return HELPERS


async def leave_game(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Calls Plutarch to unregister the user on a given date and try to sell his slot 
    Obtains date from callback_date and user from context.
    """
    query = update.callback_query
    await query.answer()
    
    user_id = context.bot_data["user_id"]
    game_date = query.data.split(':')[1]

    unergistered, sold, reason = plutarch.leave_game(user_id, game_date, "https://payme")
    if unergistered:
        reply = f"You were un-registered from a game on {game_date}"
        if sold:
            reply += " and I also added your slot to auction!"
        elif reason:
            reply += " but could't add it to auction: {reason}"
    else:
        reply = f"You shall not leave: {reason}"

    await query.edit_message_text(
        text=reply+"\n\nDo you want to start over?", reply_markup=END_REPLY_MARKUP
    )

    return END_ROUTES


async def see_the_roster(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show new choice of buttons"""
    query = update.callback_query
    await query.answer()
    keyboard = [
    [
        InlineKeyboardButton("Yes, let's do it again!", callback_data="start_over"),
        InlineKeyboardButton("Nah, I've had enough ...", callback_data="end"),
    ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    priorities = [
        "", "full","half","one-time"
    ]
    this_sunday = get_this_sunday().strftime("%Y-%m-%d")
    participants_this_sunday, reason = plutarch.list_participants(this_sunday)
    if reason:
        reply = "Something went wrong, {reason}"
        await query.edit_message_text(text=reply)
        return ConversationHandler.END
    for i, player in enumerate(participants_this_sunday):
        date = datetime.fromtimestamp(int(player.requested_at))
        formatted_date = date.strftime('%y-%m-%d %H:%M')
        participants_this_sunday[i] = f"{player.user_name} ({priorities[int(player.prio)]}) at {formatted_date}"

    reply = []
    reply.append(f"{this_sunday}")
    
    # Trying to split participants between current and waiting list
    main_section = participants_this_sunday[:14]
    waiting_section = participants_this_sunday[14:]
    
    reply.extend(main_section)
    
    if waiting_section:
        reply.append("--- waiting list ---")
        reply.extend(waiting_section)
    
    reply.append("---")
    
    # Another day, same logic
    next_sunday = get_next_sunday().strftime("%Y-%m-%d")
    participants_next_sunday, reason = plutarch.list_participants(next_sunday)
    if reason:
        reply = "Something went wrong, {reason}"
        await query.edit_message_text(text=reply)
        return ConversationHandler.END
    for i, player in enumerate(participants_next_sunday):
        date = datetime.fromtimestamp(int(player.requested_at))
        formatted_date = date.strftime('%y-%m-%d %H:%M')
        participants_next_sunday[i] = f"{player.user_name} ({priorities[int(player.prio)]}) at {formatted_date}"

    reply.append(f"{next_sunday}")
    
    main_section = participants_next_sunday[:14]
    waiting_section = participants_next_sunday[14:]
    
    reply.extend(main_section)
    
    if waiting_section:
        reply.append("--- waiting list ---")
        reply.extend(waiting_section)
    
    reply.append("---")
    reply.append("\nDo you want to start over?")

    text = "\n".join(reply)
    await query.edit_message_text(
        text=text, reply_markup=reply_markup
    )
    return END_ROUTES


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
                CallbackQueryHandler(join_the_games, pattern=r"join_the_games"),
                CallbackQueryHandler(leave_the_games, pattern=r"leave_the_games"),
                CallbackQueryHandler(see_the_roster, pattern=r"see_the_roster"),
            ],
            END_ROUTES: [
                CallbackQueryHandler(start_over, pattern=r"start_over"),
                CallbackQueryHandler(end, pattern=r"end"),
            ],
            HELPERS: [
                
                CallbackQueryHandler(join_game, pattern=r"join_game:\d{4}-\d{2}-\d{2}"),
                CallbackQueryHandler(leave_game, pattern=r"leave_game:\d{4}-\d{2}-\d{2}"),
            ]
        },
        fallbacks=[CommandHandler("start", start)],
        per_user=True,
        per_chat=True
    )

    # Add ConversationHandler to application that will be used for handling updates
    application.add_handler(conv_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
