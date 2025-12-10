# Discord Bot Setup Guide

This guide will walk you through setting up the BO7 Discord bot prototype in your Discord server.

## Prerequisites

- Python 3.11 or higher
- A Discord account with permission to create bots
- A Supabase account (free tier works fine)

## Step 1: Create a Discord Bot Application

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click **"New Application"** and give it a name (e.g., "BO7 Match Logger")
3. Go to the **"Bot"** section in the left sidebar
4. Click **"Add Bot"** and confirm
5. Under **"Token"**, click **"Reset Token"** or **"Copy"** to get your bot token
   - ⚠️ **Keep this token secret!** You'll need it for the `.env` file
6. Scroll down to **"Privileged Gateway Intents"** and enable:
   - ✅ **Server Members Intent** (if you need member info)
   - The bot uses minimal intents, so you may not need this
7. Go to the **"OAuth2"** → **"URL Generator"** section:
   - Under **"Scopes"**, select:
     - ✅ `bot`
     - ✅ `applications.commands`
   - Under **"Bot Permissions"**, select:
     - ✅ `Send Messages`
     - ✅ `Use Slash Commands`
     - ✅ `Read Message History`
   - Copy the generated URL at the bottom
8. Open the URL in your browser to invite the bot to your Discord server
   - Select the server you want to add it to
   - Authorize the bot

## Step 2: Set Up Supabase

1. Go to [Supabase](https://supabase.com) and sign up/login
2. Create a new project (or use an existing one)
3. Wait for the project to finish setting up (takes a few minutes)
4. Go to **Settings** → **API**
5. Copy the following:
   - **Project URL** (looks like `https://xxxxx.supabase.co`)
   - **service_role key** (under "Project API keys" - use the `service_role` key, NOT the `anon` key)
     - ⚠️ **Keep this key secret!** It has full database access
6. Go to **SQL Editor** in the left sidebar
7. Run the database schema:
   - Open `db/master_denorm_dev.sql` from this project
   - Copy and paste the SQL into the Supabase SQL Editor
   - Click **"Run"** to execute it
   - This creates the necessary tables for match logging

## Step 3: Set Up Python Environment

1. Open a terminal/command prompt in the project root directory
2. Navigate to the bot directory:
   ```powershell
   cd discordbot_dev
   ```
3. Create a virtual environment:
   ```powershell
   python -m venv .venv
   ```
4. Activate the virtual environment:
   ```powershell
   .venv\Scripts\Activate.ps1
   ```
   (If you get an execution policy error, run: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`)
5. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

## Step 4: Configure Environment Variables

1. Copy the example environment file:
   ```powershell
   copy env.example .env
   ```
2. Open `.env` in a text editor and fill in your values:
   ```env
   DISCORD_TOKEN=your-actual-discord-bot-token-here
   SUPABASE_URL=https://your-project-id.supabase.co
   SUPABASE_SERVICE_KEY=your-service-role-key-here
   SUPABASE_TABLE=match_master
   DRY_RUN=true
   GUILD_LABEL=Guild
   JSOC_LABEL=JSOC
   ```
   - Replace `your-actual-discord-bot-token-here` with your Discord bot token from Step 1
   - Replace `https://your-project-id.supabase.co` with your Supabase project URL
   - Replace `your-service-role-key-here` with your Supabase service_role key
   - Keep `DRY_RUN=true` for now (this prevents writing to the database while testing)

## Step 5: Validate Your Configuration

Run the validation script to check that everything is set up correctly:

```powershell
python validate_env.py
```

This will check:
- ✅ That your `.env` file exists
- ✅ That all required variables are set
- ✅ That your Discord token format looks correct
- ✅ That your Supabase URL is valid
- ✅ That you can connect to Supabase

Fix any errors before proceeding.

## Step 6: Run the Bot

**Important:** You can run the bot in two ways:

**Option 1: From the project root directory (recommended)**
```powershell
cd ..  # Go back to project root if you're in discordbot_dev
python -m discordbot_dev.main
```

**Option 2: From within the discordbot_dev directory**
```powershell
# Make sure you're in the discordbot_dev directory
python main.py
```

You should see:
```
INFO:__main__:Slash commands synced.
INFO:__main__:Logged in as YourBotName#1234
```

The bot is now online! 🎉

## Step 7: Test the Bot

1. Go to your Discord server
2. Type `/logmatch` in any channel
3. You should see an interactive menu with dropdowns to:
   - Select game mode
   - Select map
   - Choose team sizes
   - Pick players
   - Enter scores
   - Submit the match

## Troubleshooting

### Bot doesn't appear online
- Check that you copied the Discord token correctly (no extra spaces)
- Make sure the bot was successfully invited to your server
- Check the console for error messages

### Slash command doesn't appear
- Slash commands can take up to 1 hour to sync globally
- Try restarting Discord
- Make sure the bot has the `applications.commands` scope

### "Module not found" errors
- Make sure you're running from the project root: `python -m discordbot_dev.main`
- Make sure your virtual environment is activated
- Try reinstalling dependencies: `pip install -r requirements.txt`

### Supabase connection errors
- Verify your Supabase URL and service_role key are correct
- Make sure you ran the SQL schema in Supabase
- Check that your Supabase project is active (not paused)

### Bot responds but can't write to database
- Check that `DRY_RUN=false` in your `.env` file (when ready to write)
- Verify your Supabase service_role key has the correct permissions
- Check the Supabase logs for any errors

## Next Steps

Once everything is working:

1. **Test with DRY_RUN enabled**: Try logging a few matches to see the payloads without writing to the database
2. **Disable DRY_RUN**: When ready, set `DRY_RUN=false` in your `.env` file to start saving matches
3. **Customize labels**: Update `GUILD_LABEL` and `JSOC_LABEL` in `.env` to match your team names
4. **Add more players**: Edit `discordbot_dev/roster.py` to add more players to the roster

## Getting Help

- Check the console output for error messages
- Run `python validate_env.py` to verify your configuration
- Review the main README.md for more information about the project

