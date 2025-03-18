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
from dynaconf import Dynaconf
from datetime import datetime
from models import Priorities, BotStorage
from helpers import get_this_sunday, get_next_sunday
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
)

# Enable loggings
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

log = logging.getLogger(__name__)

plutarch = Plutarch()

settings = Dynaconf(
    envvar_prefix="PLUTARCH",
    settings_file="settings.toml",
    sysenv_fallback=True,
)

START_ROUTES, HELPERS = range(2)

# 3 horizontally splitted buttons
START_REPLY_MARKUP = [
            [InlineKeyboardButton("Join The Games", callback_data="join_the_games")],
            [InlineKeyboardButton("Yield The Arena", callback_data="leave_the_games")],
            [InlineKeyboardButton("Show The Roster", callback_data="see_the_roster")],
    ]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Send message on `/start`."""
    # Get user that sent /start and log his name
    # Store it in a context
    user_name = update.message.from_user.name
    context.bot_data[BotStorage.USER_ID] = user_name
    # HTML-formatted header of the reply
    reply = [f"Greetings <b>{user_name}</b>!"]
    # Check if player is added to the list of players 
    player, err = plutarch.get_player(user_name)
    context.bot_data[BotStorage.PLAYER] = player
    # If we cannot get details from the DB - return
    if err:
        reply.append(f"I cannot foresee your future now - please come later")
        text = "\n".join(reply)
        await update.message.reply_text(text=text, parse_mode="HTML")
        return ConversationHandler.END
    # Send player to admin to validate and add him
    if not player:
        reply.append(f"You are not registered member. Please ask admin to add you")
        text = "\n".join(reply)
        await update.message.reply_text(text=text, parse_mode="HTML")
        return ConversationHandler.END
    
    # Check if the user already registered
    upcoming_games = [
        get_this_sunday().strftime("%Y-%m-%d"),
        get_next_sunday().strftime("%Y-%m-%d")
    ]
    context.bot_data[BotStorage.UPCOMING_GAME_DATES] = upcoming_games

    registrations = plutarch.is_registered(user_name, upcoming_games)
   

    registration_dates = []
    registration_objects = []
    for registration, err in registrations:
        if err:
            reply.append(f"I cannot foresee your future now - please come later")
            text = "\n".join(reply)
            await update.message.reply_text(text=text, parse_mode="HTML")
            return ConversationHandler.END
        if registration: # Not None
            registration_dates.append(registration.game_date)
            registration_objects.append(registration)

    context.bot_data[BotStorage.REGISTRATION_DATES] = registration_dates
    context.bot_data[BotStorage.REGISTRATIONS] = registration_objects

    if registration_dates:
        reply.append(f"I see you have been registered for " + " and ".join(registration_dates) + ". Great!")
    else:
        reply.append(f"I see you are <b>not</b> registered for any game yet. Please join!")
    text = "\n".join(reply)
    # Send only those buttons that are needed now
    # Add context for further calls
    # To minimize amount of calls, from here onwards in any other handler we assume:
    # User is valid and registered
    # Game does exist
    # TODO: this should be handled via, returning closest Sundays
    #   get_this_sunday - closest available game
    #   get_next_sunday - closest available game after that
    
    
    
    if len(registration_dates) == 2:
        # Do not show "Join The Games", already joined everything
        buttons = START_REPLY_MARKUP[1:]
    elif len(registration_dates) == 1:
        # Show all options
        buttons = START_REPLY_MARKUP
    else:
        # do not show "Yield The Arena"
        buttons = START_REPLY_MARKUP[:1] + START_REPLY_MARKUP[2:]
    reply_markup = InlineKeyboardMarkup(buttons)
    await update.message.reply_text(text=text, parse_mode="HTML", reply_markup=reply_markup)
    # Tell ConversationHandler to send those buttons
    return START_ROUTES


async def end(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Returns `ConversationHandler.END`, which tells the
    ConversationHandler that the conversation is over.
    """
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(text="See you next time!", parse_mode="HTML")
    return ConversationHandler.END

async def join_the_games(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Propose to join a game in this sunday or sunday in 2 weeks"""
    query = update.callback_query
    await query.answer()

    upcoming_games = context.bot_data[BotStorage.UPCOMING_GAME_DATES]
    registrations = context.bot_data[BotStorage.REGISTRATION_DATES]

    keyboard = [[]]
    for game in upcoming_games:
        if not game in registrations:
            keyboard[0].append(InlineKeyboardButton(f"Join on {game}", callback_data=f"join_game:{game}"))

    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(
        text=f"You can register for this games", parse_mode="HTML", reply_markup=reply_markup
    )
    return HELPERS


async def join_game(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Calls Plutarch to register user on a given date. 
    Obtains date from callback_date and user from context
    """
    query = update.callback_query
    await query.answer()

    game_date = query.data.split(':')[1]
    player = context.bot_data[BotStorage.PLAYER]

    _, err = plutarch.register(player, game_date)
    if not err:
        reply = f"You were registered for a game on {game_date}!"
    else:
        reply = f"You cannot join the game: {err}"

    await query.edit_message_text(text=reply, parse_mode="HTML")
    return ConversationHandler.END


async def leave_the_games(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Propose to leave a game in this sunday or sunday in 2 weeks"""

    query = update.callback_query
    await query.answer()

    upcoming_games = context.bot_data[BotStorage.UPCOMING_GAME_DATES]
    registrations = context.bot_data[BotStorage.REGISTRATION_DATES]

    keyboard = [[]]
    for game in upcoming_games:
        if game in registrations:
            keyboard[0].append(InlineKeyboardButton(f"Leave {game}", callback_data=f"leave_game:{game}"))

    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text(
        text="Which week you'd like to yield?", parse_mode="HTML", reply_markup=reply_markup
    )
    # Transfer to conversation state `SECOND`
    return HELPERS


async def leave_game(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Calls Plutarch to unregister the user on a given date and try to sell his slot 
    Obtains date from callback_date and user from context.
    """
    query = update.callback_query
    await query.answer()
    
    player = context.bot_data[BotStorage.PLAYER]
    registrations = context.bot_data[BotStorage.REGISTRATIONS]
    print(registrations)
    # We trust this is set to a date where user is already registered
    game_date = query.data.split(':')[1]

    # Just a bit of syntax sugar here. Get registration for matching date
    registration = [r for r in registrations if r.game_date == game_date][0]

    unergistered, sold, err = plutarch.leave_game(player, registration, "pay to https://payme")
    if unergistered:
        reply = f"You were un-registered from a game on {game_date}"
        if sold:
            reply += " and I also added your slot to auction!"
        elif err:
            reply += f" but could't add it to auction: {err}"
    else:
        reply = f"You shall not leave: {err}"


    await query.edit_message_text(text=reply, parse_mode="HTML")
    return ConversationHandler.END


async def see_the_roster(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Show new choice of buttons"""
    query = update.callback_query
    await query.answer()

    priority_to_emoji_map = {
        1: "∞", # Infinite Arena Access - No Reaping Required!
        2: "🎟️", # Arena Strategist – Choose Your Matches Wisely!
        3: "🎲" # The Reaped – One Game, One Fate!
    }

    upcoming_games = context.bot_data[BotStorage.UPCOMING_GAME_DATES]
    
    reply = []
    for game in upcoming_games:
        participants, err = plutarch.list_participants(game)
        if err:
            reply = "I cannot foresee the future <b>now</b> - please come later"
            await query.edit_message_text(text=reply)
            return ConversationHandler.END
        for i, player in enumerate(participants):
            date = datetime.fromtimestamp(int(player.requested_at))
            formatted_date = date.strftime('%y-%m-%d %H:%M')
            # TODO: looks like there are roughly 40 characters in a string
            # Need to find a way how to align it 
            participants[i] = f"{priority_to_emoji_map[player.prio]} {player.user_name} at {formatted_date}"


        # TODO: Add flip - if we are past registration deadline, change the subject to
        # <i>No more waiting. No more second chances. Play hard. 🔥</i>
        # <i>No more waiting. No more hesitation. Just play. </i>
        reply.append(f"<b>{game}</b>\n───────────────\n<i>Hold tight. The arena is filling up…</i>\n")
        
        # Trying to split participants between current and waiting list
        main_section = participants[:14]
        waiting_section = participants[14:]
        
        reply.extend(main_section)
        
        if waiting_section:
            reply.append("\n<b>👀 Waiting List 👀</b>\n───────────────\n<i>Patience is a virtue… Your turn will come!</i>\n")
            reply.extend(waiting_section)
        
        reply.append("\n")
    
    text = "\n".join(reply)
    await query.edit_message_text(text=text, parse_mode="HTML")
    return ConversationHandler.END

async def summarize(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    user_name = update.message.from_user.name
    context.bot_data[BotStorage.USER_ID] = user_name
    if user_name != "@kchestnov":
        return ConversationHandler.END
    
    # TODO: Validate input
    if len(context.args) == 1:
        game_date = context.args[0]
    else:
        game_date = get_this_sunday().strftime("%Y-%m-%d")

    text = f"Let's see who pays whom for on {game_date}\n" 
    message = await update.message.reply_text(text=text, parse_mode="HTML")
    participants, err = plutarch.list_participants(game_date)
    if err:
        reply = "I cannot help you <b>now</b> - please come later"
        await message.edit_text(text=reply)
        return ConversationHandler.END
    
    text += "Current list is:\n"
    registrations = participants[:14]
    for registration in registrations:
        player, err = plutarch.get_player(registration.user_name)
        # if player.balance > 0:
        #     text += f"{registration.user_name}'s balance: {player.balance}\n"
        #     err = plutarch.update_balance(player)
        #     if err:
        #         reply = "I cannot help you now - please come later"
        #         await message.edit_text(text=reply)
        #         return ConversationHandler.END
        # else:
        slot, err = plutarch.collect_money(player, registration)
        if err:
            reply = "I cannot help you <b>now</b> - please come later"
            await message.edit_text(text=reply)
            return ConversationHandler.END
        text += f"{slot.buyer_user_name} {slot.tikkie_link}\n"
            
        await message.edit_text(text=text, parse_mode="HTML")

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
        entry_points=[CommandHandler("start", start), CommandHandler("summarize", summarize)],
        states={
            START_ROUTES: [
                CallbackQueryHandler(join_the_games, pattern=r"join_the_games"),
                CallbackQueryHandler(leave_the_games, pattern=r"leave_the_games"),
                CallbackQueryHandler(see_the_roster, pattern=r"see_the_roster"),
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
    # This handles CTR+C under the hood
    # TODO: Need to close all on-going conversations
    # or remove buttons from them
    # TODO: Need to terminage conversations (remove buttons and send Conversation.END)
    # for every request after certain threshold
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
