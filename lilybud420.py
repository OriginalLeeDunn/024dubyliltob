import asyncio
import os
import subprocess
import json
from typing import Dict, List
from highrise import BaseBot, ChatEvent, User, AnchorPosition, Position
from highrise.webapi import WebAPI
from highrise.models_webapi import *
import random

class RadioBot(BaseBot):
    def __init__(self):
        super().__init__()
        # We don't need audio streaming variables anymore, just keeping teleport and emote functionality
        # Dictionary to store teleport points: name -> Position
        self.teleport_points = {}
        
        # Load teleport points from JSON file if it exists
        self.teleport_file = "teleport_points.json"
        self.load_teleport_points()
        
        # Role-based access control
        self.admin_users = set()  # Set of admin user IDs
        self.overlord_users = set()  # Set of overlord user IDs (highest access)
        self.admin_file = "admin_users.json"
        self.overlord_file = "overlord_users.json"
        self.pending_overlord_file = "pending_overlord.json"
        self.load_admin_users()
        self.load_overlord_users()
        self.check_pending_overlord()
        
        # Web API for item operations
        self.webapi = None
        # Get API key from environment variable
        self.api_key = os.getenv('HIGHRISE_API_KEY')
        # Dictionary of free items by category
        self.free_items = {
            "top": {
                "shirt-n_starteritems2019tankwhite": "Tank - White",
                "shirt-n_starteritems2019tankblack": "Tank - Black",
                "shirt-n_starteritems2019raglanwhite": "Raglan - White",
                "shirt-n_starteritems2019raglanblack": "Raglan - Black",
                "shirt-n_starteritems2019pulloverwhite": "Pullover - White",
                "shirt-n_starteritems2019pulloverblack": "Pullover - Black",
                "shirt-n_starteritems2019maletshirtwhite": "Basic T-shirt - White",
                "shirt-n_starteritems2019maletshirtblack": "Basic T-shirt - Black",
                "shirt-n_starteritems2019femtshirtwhite": "Basic T-shirt - White",
                "shirt-n_starteritems2019femtshirtblack": "Basic T-shirt - Black",
                "shirt-n_room32019slouchyredtrackjacket": "Red Off-shoulder Track Jacket",
                "shirt-n_room32019malepuffyjacketgreen": "Green Puffer and T",
                "shirt-n_room32019longlineteesweatshirtgrey": "Grey Sweatshirt & Tee",
                "shirt-n_room32019jerseywhite": "White Vintage Jersey",
                "shirt-n_room32019hoodiered": "Red Raglan Hoodie",
                "shirt-n_room32019femalepuffyjacketgreen": "Green Puffer and Bra Top",
                "shirt-n_room32019denimjackethoodie": "Yellow Hoodie Denim Jacket",
                "shirt-n_room32019croppedspaghettitankblack": "Black Spaghetti Tank",
                "shirt-n_room22109plaidjacket": "Plaid Jacket",
                "shirt-n_room22109denimjacket": "Classic Denim Jacket",
                "shirt-n_room22019tuckedtstripes": "Striped Shirt",
                "shirt-n_room22019overalltop": "Denim Overall Top",
                "shirt-n_room22019denimdress": "Denim Overall Dress",
                "shirt-n_room22019bratoppink": "Pink Bra Top",
                "shirt-n_room12019sweaterwithbuttondowngrey": "Plain Layered Grey Sweater",
                "shirt-n_room12019cropsweaterwhite": "White Cropped Sweater",
                "shirt-n_room12019cropsweaterblack": "Black Cropped Sweater",
                "shirt-n_room12019buttondownblack": "Black Button Down",
                "shirt-n_philippineday2019filipinotop": "Elegant Top",
                "shirt-n_flashysuit": "Flashy Suit",
                "shirt-n_SCSpring2018flowershirt": "Daisy Crop-Top",
                "shirt-n_2016fallblacklayeredbomber": "Sport Bomber",
                "shirt-n_2016fallblackkknottedtee": "Black Knotted Tee",
                "shirt-f_skullsweaterblack": "Black Skull Sweater",
                "shirt-f_punklace": "Punk Lace",
                "shirt-f_plaidtiedshirtred": "Red Tied Plaid Shirt",
                "shirt-f_marchingband": "Marching Band Top"
            },
            "bottom": {
                "pants-n_starteritems2019jeansblack": "Jeans - Black",
                "pants-n_starteritems2019jeansblue": "Jeans - Blue",
                "pants-n_starteritems2019shortsblack": "Shorts - Black",
                "pants-n_starteritems2019shortsblue": "Shorts - Blue",
                "pants-n_starteritems2019skirtblack": "Skirt - Black",
                "pants-n_starteritems2019skirtblue": "Skirt - Blue",
                "pants-n_room32019trackpantsblack": "Black Track Pants",
                "pants-n_room32019shortsdenim": "Denim Shorts",
                "pants-n_room22019denimshorts": "Denim Shorts",
                "pants-n_room12019sweatpantsblack": "Black Sweatpants"
            },
            "shoes": {
                "shoes-n_starteritems2019sneakerswhite": "Sneakers - White",
                "shoes-n_starteritems2019sneakersblack": "Sneakers - Black",
                "shoes-n_starteritems2019highheelsblack": "High Heels - Black",
                "shoes-n_room32019sneakersred": "Red Sneakers",
                "shoes-n_room22019bootsblack": "Black Boots"
            },
            "hair_front": {
                "hair_front-n_malenew33": "Short Short Fro",
                "hair_front-n_malenew32": "Box Braids",
                "hair_front-n_malenew31": "Long Undercut Dreads",
                "hair_front-n_malenew30": "Undercut Dreads",
                "hair_front-n_malenew29": "Side Swept Fro",
                "hair_front-n_malenew27": "Long Buzzed Fro",
                "hair_front-n_malenew26": "Short Buzzed Fro",
                "hair_front-n_malenew25": "Curly Undercut",
                "hair_front-n_malenew24": "Tight curls",
                "hair_front-n_malenew23": "Loose Curls",
                "hair_front-n_malenew10": "Buzz Cut",
                "hair_front-n_basic2020overshoulderwavyshort": "Over Shoulder Wavy Short",
                "hair_front-n_basic2020overshoulderwavy": "Over Shoulder Wavy Long",
                "hair_front-n_basic2020overshoulderstraight": "Over Shoulder Straight Long",
                "hair_front-n_basic2020overshoulderpony": "Over Shoulder Pony",
                "hair_front-n_basic2020overshouldercurly": "Over Shoulder Curly",
                "hair_front-n_basic2018topknot": "Top Knot",
                "hair_front-n_basic2018straightnobangs": "Straight No Bangs",
                "hair_front-n_basic2018straightfullbangs": "Straight Full Bangs",
                "hair_front-n_basic2018buzzcut": "Bald"
            },
            "hair_back": {
                "hair_back-n_malenew33": "Short Short Fro",
                "hair_back-n_malenew32": "Box Braids",
                "hair_back-n_malenew31": "Long Undercut Dreads",
                "hair_back-n_malenew30": "Undercut Dreads",
                "hair_back-n_malenew29": "Side Swept Fro",
                "hair_back-n_malenew27": "Long Buzzed Fro",
                "hair_back-n_malenew26": "Short Buzzed Fro",
                "hair_back-n_malenew25": "Curly Undercut",
                "hair_back-n_malenew24": "Tight Curls",
                "hair_back-n_malenew23": "Loose Curls",
                "hair_back-n_malenew10": "Buzz Cut",
                "hair_back-n_basic2020overshoulderwavyshort": "Over Shoulder Wavy Short",
                "hair_back-n_basic2020overshoulderwavy": "Over Shoulder Wavy Long",
                "hair_back-n_basic2020overshoulderstraight": "Over Shoulder Straight Long",
                "hair_back-n_basic2020overshoulderpony": "Over Shoulder Pony",
                "hair_back-n_basic2020overshouldercurly": "Over Shoulder Curly",
                "hair_back-n_basic2018topknotback": "Top Knot Back",
                "hair_back-n_basic2018straightshort": "Straight Short",
                "hair_back-n_basic2018straightlong": "Straight Long",
                "hair_back-n_basic2018buzzcut": "Bald"
            },
            "face_hair": {
                "face_hair-n_basic2018stubble": "Stubble",
                "face_hair-n_basic2018fullbeard": "Full Beard",
                "face_hair-n_basic2018goatee": "Goatee",
                "face_hair-n_basic2018mustache": "Mustache"
            },
            "eyebrow": {
                "eyebrow-n_basic2018straight": "Straight",
                "eyebrow-n_basic2018natural": "Natural",
                "eyebrow-n_basic2018arched": "Arched",
                "eyebrow-n_basic2018thin": "Thin"
            },
            "eye": {
                "eye-n_basic2018round": "Round",
                "eye-n_basic2018almond": "Almond",
                "eye-n_basic2018upturned": "Upturned",
                "eye-n_basic2018downturned": "Downturned"
            },
            "nose": {
                "nose-n_basic2018straight": "Straight",
                "nose-n_basic2018button": "Button",
                "nose-n_basic2018roman": "Roman",
                "nose-n_basic2018aquiline": "Aquiline"
            },
            "mouth": {
                "mouth-n_basic2018neutral": "Neutral",
                "mouth-n_basic2018smile": "Smile",
                "mouth-n_basic2018full": "Full",
                "mouth-n_basic2018thin": "Thin"
            },
            "accessories": {
                "glasses-n_basic2018round": "Round Glasses",
                "glasses-n_basic2018square": "Square Glasses",
                "glasses-n_basic2018aviator": "Aviator Glasses",
                "glasses-n_basic2018cat": "Cat Eye Glasses",
                "hat-n_basic2018beanie": "Beanie",
                "hat-n_basic2018cap": "Cap",
                "hat-n_basic2018bucket": "Bucket Hat",
                "earrings-n_basic2018studs": "Stud Earrings",
                "earrings-n_basic2018hoops": "Hoop Earrings"
            },
            "freckle": {
                "freckle-n_basic2018light": "Light Freckles",
                "freckle-n_basic2018medium": "Medium Freckles",
                "freckle-n_basic2018heavy": "Heavy Freckles"
            }
        }
        
        # Dictionary of available emotes
        self.free_emotes = [
            ("Sit", "idle-loop-sitfloor"),
            ("Enthused", "idle-enthusiastic"),
            ("Yes", "emote-yes"),
            ("The Wave", "emote-wave"),
            ("Tired", "emote-tired"),
            ("Snowball Fight!", "emote-snowball"),
            ("Snow Angel", "emote-snowangel"),
            ("Shy", "emote-shy"),
            ("Sad", "emote-sad"),
            ("No", "emote-no"),
            ("Model", "emote-model"),
            ("Flirty Wave", "emote-lust"),
            ("Laugh", "emote-laughing"),
            ("Kiss", "emote-kiss"),
            ("Sweating", "emote-hot"),
            ("Hello", "emote-hello"),
            ("Greedy Emote", "emote-greedy"),
            ("Face Palm", "emote-exasperatedb"),
            ("Curtsy", "emote-curtsy"),
            ("Confusion", "emote-confused"),
            ("Charging", "emote-charging"),
            ("Bow", "emote-bow"),
            ("Thumbs Up", "emoji-thumbsup"),
            ("Tummy Ache", "emoji-gagging"),
            ("Flex", "emoji-flex"),
            ("Cursing Emote", "emoji-cursing"),
            ("Raise The Roof", "emoji-celebrate"),
            ("Angry", "emoji-angry"),
            ("Savage Dance", "dance-tiktok8"),
            ("Don't Start Now", "dance-tiktok2"),
            ("Let's Go Shopping", "dance-shoppingcart"),
            ("Russian Dance", "dance-russian"),
            ("Penny's Dance", "dance-pennywise"),
            ("Macarena", "dance-macarena"),
            ("K-Pop Dance", "dance-blackpink"),
            ("Hyped", "emote-hyped"),
            ("Jinglebell", "dance-jinglebell"),
            ("Nervous", "idle-nervous"),
            ("Toilet", "idle-toilet"),
            ("Astronaut", "emote-astronaut"),
            ("Dance Zombie", "dance-zombie"),
            ("Heart Eyes", "emote-hearteyes"),
            ("Swordfight", "emote-swordfight"),
            ("TimeJump", "emote-timejump"),
            ("Snake", "emote-snake"),
            ("Heart Fingers", "emote-heartfingers"),
            ("Float", "emote-float"),
            ("Telekinesis", "emote-telekinesis"),
            ("Penguin dance", "dance-pinguin"),
            ("Creepy puppet", "dance-creepypuppet"),
            ("Sleigh", "emote-sleigh"),
            ("Maniac", "emote-maniac"),
            ("Energy Ball", "emote-energyball"),
            ("Singing", "idle_singing"),
            ("Frog", "emote-frog"),
            ("Superpose", "emote-superpose"),
            ("Cute", "emote-cute"),
            ("TikTok Dance 9", "dance-tiktok9"),
            ("Weird Dance", "dance-weird"),
            ("TikTok Dance 10", "dance-tiktok10"),
            ("Pose 7", "emote-pose7"),
            ("Pose 8", "emote-pose8"),
            ("Casual Dance", "idle-dance-casual"),
            ("Pose 1", "emote-pose1"),
            ("Pose 3", "emote-pose3"),
            ("Pose 5", "emote-pose5"),
            ("Cutey", "emote-cutey"),
            ("Punk Guitar", "emote-punkguitar"),
            ("Fashionista", "emote-fashionista"),
            ("Gravity", "emote-gravity"),
            ("Ice Cream Dance", "dance-icecream"),
            ("Wrong Dance", "dance-wrong"),
            ("UwU", "idle-uwu"),
            ("TikTok Dance 4", "idle-dance-tiktok4"),
            ("Advanced Shy", "emote-shy2"),
            ("Anime Dance", "dance-anime"),
            ("Kawaii", "dance-kawai"),
            ("Scritchy", "idle-wild"),
            ("Ice Skating", "emote-iceskating"),
            ("SurpriseBig", "emote-pose6"),
            ("Celebration Step", "emote-celebrationstep"),
            ("Creepycute", "emote-creepycute"),
            ("Pose 10", "emote-pose10"),
            ("Boxer", "emote-boxer"),
            ("Head Blowup", "emote-headblowup"),
            ('Ditzy Pose', 'emote-pose9'),
            ('Teleporting', 'emote-teleporting'),
            ('Touch', 'dance-touch'),
            ('Air Guitar','idle-guitar'),
            ("This Is For You", "emote-gift"),
            ("Push it", "dance-employee"),
        ]
        
        # Create a dictionary for quick lookup
        self.emotes = {}
        for name, emote_id in self.free_emotes:
            # Convert to lowercase and remove spaces for command matching
            key = name.lower().replace(" ", "")
            self.emotes[key] = emote_id

        # Web API for item operations
        self.webapi = None
        
        # Available clothing categories
        self.categories = ["aura", "bag", "blush", "body", "dress", "earrings", "eye", "eyebrow", 
                         "freckle", "fullsuit", "glasses", "gloves", "hair_back", "hair_front", 
                         "handbag", "hat", "jacket", "lashes", "mole", "mouth", "necklace", 
                         "nose", "shirt", "shoes", "shorts", "skirt", "sock", "tattoo", "watch"]

    async def on_start(self, session_metadata):
        print("Radio Bot started!")
        
        # Initialize Web API silently if API key is provided
        if self.api_key and self.api_key != "your_api_key_here":
            try:
                # Initialize the Web API with the API key
                self.webapi = WebAPI(self.api_key)
                print("Web API initialized successfully")
            except Exception as e:
                print(f"Web API initialization failed: {str(e)}")
                self.webapi = None
        else:
            print("Web API key not provided - outfit features disabled")
        
                
    async def set_api_key(self, user: User, message: str):
        """Set the Web API key to enable outfit customization."""
        parts = message.split(" ", 1)
        if len(parts) < 2:
            await self.highrise.send_whisper(user.id, "Please provide an API key: /setapikey [your_api_key]")
            return
            
        api_key = parts[1].strip()
        try:
            # Test the API key by initializing WebAPI
            self.webapi = WebAPI(api_key)
            # If no exception, save the key
            self.api_key = api_key
            await self.highrise.send_whisper(user.id, "👕 API key set successfully! Outfit customization features are now enabled.")
        except Exception as e:
            await self.highrise.send_whisper(user.id, f"⚠️ Invalid API key: {str(e)}")

    def check_pending_overlord(self):
        """Check if there's a pending overlord to auto-promote"""
        try:
            if os.path.exists(self.pending_overlord_file):
                with open(self.pending_overlord_file, 'r') as f:
                    pending_data = json.load(f)
                    self.pending_overlord_username = pending_data.get('pending_overlord', '').lower()
            else:
                self.pending_overlord_username = None
        except Exception as e:
            print(f"Error loading pending overlord: {e}")
            self.pending_overlord_username = None
    
    async def auto_promote_overlord(self, user: User):
        """Auto-promote user to overlord if they match pending username"""
        if (self.pending_overlord_username and 
            user.username.lower() == self.pending_overlord_username and 
            user.id not in self.overlord_users):
            
            # Add as overlord
            self.overlord_users.add(user.id)
            # Also add as admin if not already
            if user.id not in self.admin_users:
                self.admin_users.add(user.id)
                self.save_admin_users()
            self.save_overlord_users()
            
            # Remove pending file
            try:
                os.remove(self.pending_overlord_file)
            except:
                pass
            
            await self.highrise.chat(f"⚡ {user.username} has been automatically promoted to OVERLORD status! Welcome, master!")
            self.pending_overlord_username = None
            return True
        return False

    async def on_chat(self, user: User, message: str):
        # Check for auto-promotion first
        await self.auto_promote_overlord(user)
        lower_message = message.lower()
        
        # Process commands
        if lower_message.startswith("/"):
            # Help command
            if lower_message == "/help":
                await self.show_help(user)
            # Teleport commands
            elif lower_message == "/teleports":
                await self.list_teleport_points(user)
            # Radio commands
            elif lower_message.startswith("/play ") and len(message.split()) > 1:
                await self.provide_stream_info(user, message[6:])
            elif lower_message == "/radio":
                await self.show_radio_help(user)
            elif lower_message == "/stop":
                await self.highrise.chat(f"To stop the radio, the user who is playing it should mute their microphone.")
            # Outfit commands
            elif lower_message == "/outfit":
                await self.show_outfit_help(user)
            elif lower_message == "/randomoutfit":
                await self.random_outfit(user)
            elif lower_message.startswith("/equip ") and len(message.split()) > 1:
                await self.equip_item(user, message)
            elif lower_message.startswith("/color ") and len(message.split()) > 2:
                await self.change_item_color(user, message)
            elif lower_message.startswith("/remove ") and len(message.split()) > 1:
                await self.remove_item(user, message)
            elif lower_message == "/outfit_categories":
                await self.list_outfit_categories(user)
            elif lower_message.startswith("/setapikey "):
                await self.set_api_key(user, message)
            elif lower_message == "/freeitems":
                await self.list_free_items(user)
            elif lower_message.startswith("/freeitem ") and len(message.split()) > 1:
                await self.equip_free_item(user, message)
            # Emote commands
            elif lower_message == "/emotes":
                await self.list_emotes(user)
            elif lower_message.startswith("/emotes "):
                await self.handle_emote_command(user, message[8:].strip())
            # Group emote command
            elif lower_message.startswith("/all "):
                await self.perform_group_emote(user, message[5:].strip())
            # Summon command
            elif lower_message.startswith("/summon "):
                await self.summon_user(user, message)
            # Admin commands
            elif lower_message.startswith("/addadmin "):
                await self.add_admin(user, message)
            elif lower_message.startswith("/removeadmin "):
                await self.remove_admin(user, message)
            elif lower_message == "/admins":
                await self.list_admins(user)
            # Overlord commands
            elif lower_message.startswith("/addoverlord "):
                await self.add_overlord(user, message)
            elif lower_message.startswith("/removeoverlord "):
                await self.remove_overlord(user, message)
            elif lower_message == "/overlords":
                await self.list_overlords(user)
            elif lower_message == "/botinfo":
                await self.show_bot_info(user)
            elif lower_message == "/clearroom":
                await self.clear_room(user)
            elif lower_message.startswith("/announce "):
                await self.announce_message(user, message)
            elif lower_message.startswith("/kick "):
                await self.kick_user(user, message)
            elif lower_message == "/shutdown":
                await self.shutdown_bot(user)
            # Try to handle as direct emote command if nothing else matched
            else:
                emote_name = lower_message[1:].lower().replace(" ", "")
                if emote_name in self.emotes:
                    await self.perform_emote(user, emote_name)
        # Handle 'here' commands for teleport points
        elif lower_message == "here":
            await self.set_teleport_point(user, "default")
        elif lower_message.startswith("here "):
            point_name = message[5:].strip()
            await self.set_teleport_point(user, point_name)
        # Teleport to saved point
        elif message in self.teleport_points:
            await self.teleport_user(user, message)

    async def on_user_join(self, user: User, position) -> None:
        """On a user joining the room: greet them and attempt overlord auto-promotion."""
        try:
            # Attempt auto-promotion if applicable
            await self.auto_promote_overlord(user)

            # Friendly greeting for NoSlaggs' room
            await self.highrise.chat(f"👋 Welcome to NoSlaggs' room, {user.username}! Make yourself at home.")

            # Perform a friendly hello emote if available
            try:
                await self.highrise.send_emote(self.emotes.get("hello", "emote-hello"))
            except Exception:
                # Ignore emote failures silently
                pass
        except Exception as e:
            # Log to console to avoid spamming chat on errors
            print(f"Error in on_user_join: {e}")

    async def on_user_leave(self, user: User) -> None:
        """On a user leaving the room: acknowledge their departure."""
        try:
            await self.highrise.chat(f"👋 {user.username} has left the room.")
        except Exception as e:
            print(f"Error in on_user_leave: {e}")

    async def provide_stream_info(self, user: User, stream_url: str):
        """Provide information about a stream URL for a human DJ to play."""
        # Basic URL validation
        if not stream_url.startswith(('http://', 'https://')):
            await self.highrise.chat(f"Invalid URL format. Please use a URL starting with http:// or https://")
            return
            
        # Clean the URL (remove any trailing spaces or text)
        stream_url = stream_url.split()[0].strip()
        
        # Send instructions to the room
        await self.highrise.chat(f"🎵 Radio Stream URL: {stream_url}")
        await self.highrise.chat(f"Instructions for {user.username} or any age-verified user:\n1. Copy this URL\n2. Open it in a media player (VLC, browser, etc.)\n3. Join voice chat in Highrise\n4. Share your computer audio through your microphone")

    def load_teleport_points(self):
        """Load teleport points from JSON file"""
        try:
            if os.path.exists(self.teleport_file):
                with open(self.teleport_file, 'r') as f:
                    teleport_data = json.load(f)
                    
                # Convert the JSON data back to Position objects
                for name, pos_data in teleport_data.items():
                    self.teleport_points[name] = Position(
                        pos_data['x'],
                        pos_data['y'],
                        pos_data['z'],
                        pos_data.get('facing', 'front')
                    )
                print(f"Loaded {len(self.teleport_points)} teleport points from {self.teleport_file}")
        except Exception as e:
            print(f"Error loading teleport points: {str(e)}")
    
    def save_teleport_points(self):
        """Save teleport points to JSON file"""
        try:
            # Convert Position objects to dictionaries for JSON serialization
            teleport_data = {}
            for name, pos in self.teleport_points.items():
                teleport_data[name] = {
                    'x': pos.x,
                    'y': pos.y,
                    'z': pos.z,
                    'facing': getattr(pos, 'facing', 'front')
                }
                
            with open(self.teleport_file, 'w') as f:
                json.dump(teleport_data, f, indent=2)
            print(f"Saved {len(self.teleport_points)} teleport points to {self.teleport_file}")
        except Exception as e:
            print(f"Error saving teleport points: {str(e)}")
            
    async def set_teleport_point(self, user: User, point_name: str):
        """Set a teleport point at the user's current position"""
        # Get the user's current position
        response = await self.highrise.get_room_users()
        
        user_position = None
        for room_user, position in response.content:
            if room_user.id == user.id:
                user_position = position
                break
        
        if user_position:
            # Only store Position objects, not AnchorPosition
            if isinstance(user_position, Position):
                self.teleport_points[point_name] = user_position
                await self.highrise.chat(f"Teleport point '{point_name}' set at {user_position.x}, {user_position.y}, {user_position.z}")
                # Save to JSON file
                self.save_teleport_points()
            else:
                await self.highrise.chat("Cannot set teleport point at an anchor position.")
        else:
            await self.highrise.chat("Could not determine your position.")
            
    async def teleport_user(self, user: User, point_name: str):
        """Teleport a user to a saved point"""
        if point_name in self.teleport_points:
            position = self.teleport_points[point_name]
            await self.highrise.teleport(user.id, position)
            await self.highrise.chat(f"Teleported {user.username} to '{point_name}'")
        else:
            await self.highrise.chat(f"Teleport point '{point_name}' not found.")
            
    async def list_teleport_points(self, user: User):
        """List all saved teleport points"""
        if not self.teleport_points:
            await self.highrise.chat("No teleport points have been set.")
            return
        
        points_list = "\n".join([f"- {name}" for name in self.teleport_points.keys()])
        await self.highrise.send_whisper(user.id, f"📍 Teleport Points:\n{points_list}")
            
    async def show_radio_stations(self, user: User):
        """Show a list of popular radio stations that can be played."""
        stations = [
            {"name": "BBC Radio 1", "url": "https://stream.live.vc.bbcmedia.co.uk/bbc_radio_one"},
            {"name": "Lofi Hip Hop", "url": "http://usa9.fastcast4u.com/proxy/jamz?mp=/1"},
            {"name": "Classic Rock", "url": "http://185.33.21.112:80/rock_128"},
            {"name": "Smooth Jazz", "url": "http://strm112.1.fm/smoothjazz_mobile_mp3"},
            {"name": "Dance/EDM", "url": "http://stream.dancewave.online:8080/dance.mp3"}
        ]
        
        message = "📻 Available Radio Stations:\n"
        for i, station in enumerate(stations, 1):
            message += f"{i}. {station['name']} - Use command: /play {station['url']}\n"
        
        message += "\nAn age-verified user needs to play these streams through their microphone."
        await self.highrise.send_whisper(user.id, message)

    async def show_help(self, user: User):
        """Show help information in very small chunks to avoid message length limits."""
        # General info
        help_text1 = "📻 Radio Bot Commands 📻"
        await self.highrise.send_whisper(user.id, help_text1)
        
        # Radio Commands
        help_text2 = (
            "Radio Commands:\n"
            "- /radio: Show stations\n"
            "- /play [url]: Provide stream URL\n"
            "- /stop: Stop radio"
        )
        await self.highrise.send_whisper(user.id, help_text2)
        
        # Teleport Commands
        help_text3 = (
            "Teleport Commands:\n"
            "- /teleports: List points\n"
            "- here: Save default point\n"
            "- here [name]: Save named point\n"
            "- [point_name]: Teleport to point"
        )
        await self.highrise.send_whisper(user.id, help_text3)
        
        # Emote Commands
        help_text4 = (
            "Emote Commands:\n"
            "- /emotes: List emotes\n"
            "- /emotes [name]: Do emote\n"
            "- /[emote_name]: Direct emote\n"
            "- /all [emote_name]: Everyone emotes"
        )
        await self.highrise.send_whisper(user.id, help_text4)
        
        # Outfit Commands - Part 1
        help_text5 = (
            "Outfit Commands (1/3):\n"
            "- /outfit: Show outfit help\n"
            "- /randomoutfit: Random outfit\n"
            "- /equip [item]: Equip item"
        )
        await self.highrise.send_whisper(user.id, help_text5)
        
        # Outfit Commands - Part 2
        help_text6 = (
            "Outfit Commands (2/3):\n"
            "- /color [category] [#]: Change color\n"
            "- /remove [category]: Remove item\n"
            "- /outfit_categories: List categories"
        )
        await self.highrise.send_whisper(user.id, help_text6)
        
        # Outfit Commands - Part 3
        help_text7 = (
            "Outfit Commands (3/3):\n"
            "- /freeitems: List free items\n"
            "- /freeitem [category] [item_number]: Equip item\n"
            "- /setapikey [key]: Set API key"
        )
        await self.highrise.send_whisper(user.id, help_text7)
        
        # Summon Commands
        help_text8 = (
            "Summon Commands:\n"
            "- /summon @username: Teleport user to you"
        )
        await self.highrise.send_whisper(user.id, help_text8)
        
        # Admin Commands (only show to admins)
        if self.is_admin(user):
            help_text9 = (
                "Admin Commands:\n"
                "- /addadmin @username: Add admin\n"
                "- /removeadmin @username: Remove admin\n"
                "- /admins: List all admins"
            )
            await self.highrise.send_whisper(user.id, help_text9)
        
        # Overlord Commands (only show to overlords)
        if self.is_overlord(user):
            help_text10 = (
                "⚡ OVERLORD Commands (1/2):\n"
                "- /addoverlord @username: Grant overlord\n"
                "- /removeoverlord @username: Remove overlord\n"
                "- /overlords: List all overlords\n"
                "- /botinfo: Show bot statistics"
            )
            await self.highrise.send_whisper(user.id, help_text10)
            
            help_text11 = (
                "⚡ OVERLORD Commands (2/2):\n"
                "- /announce [msg]: Broadcast message\n"
                "- /kick @username: Kick user\n"
                "- /clearroom: Clear all non-overlords\n"
                "- /shutdown: Shutdown bot"
            )
            await self.highrise.send_whisper(user.id, help_text11)
        
        # Add API key status
        if not self.webapi:
            await self.highrise.send_whisper(user.id, "⚠️ Web API is not initialized. Use /setapikey to enable outfit features.")
        else:
            await self.highrise.send_whisper(user.id, "✅ Web API is initialized. Outfit features are enabled.")
        
    async def handle_emote_command(self, user: User, emote_name: str):
        """Handle the /emotes command to make the bot perform an emote."""
        emote_name = emote_name.lower().replace(" ", "")
        if emote_name in self.emotes:
            await self.perform_emote(user, emote_name)
        else:
            await self.highrise.chat(f"Unknown emote: {emote_name}. Use /emotes to see available emotes.")

    async def list_emotes(self, user: User):
        """List available emotes in smaller chunks to avoid message length limits."""
        # Send introduction message
        await self.highrise.send_whisper(user.id, "📋 Available Emotes (use /emotename to perform):\n")
        
        # Get list of emote names from the free_emotes list
        emote_names = [name for name, _ in self.free_emotes]
        
        # Send emotes in chunks of 6 to avoid message length limits
        chunk_size = 6
        for i in range(0, len(emote_names), chunk_size):
            chunk = emote_names[i:i+chunk_size]
            # Format each emote as /emotename
            formatted_chunk = [f"/{name.lower().replace(' ', '')}" for name in chunk]
            # Join with commas and send as a whisper
            chunk_message = ", ".join(formatted_chunk)
            await self.highrise.send_whisper(user.id, chunk_message)
        
        # Send final instruction message
        await self.highrise.send_whisper(user.id, "\nUse /emotename to perform an emote (e.g., /wave, /dance, /bow).")

    async def perform_emote(self, user: User, emote_name: str):
        """Make the bot perform an emote"""
        if emote_name in self.emotes:
            emote_id = self.emotes[emote_name]
            await self.highrise.send_emote(emote_id)
        else:
            await self.highrise.chat(f"Unknown emote: {emote_name}. Use /emotes to see available emotes.")

    async def perform_group_emote(self, user: User, emote_name: str):
        """Make all users in the room perform the specified emote"""
        emote_name = emote_name.lower().replace(" ", "")
        
        if emote_name in self.emotes:
            emote_id = self.emotes[emote_name]
            
            try:
                # Get all users in the room
                room_users = await self.highrise.get_room_users()
                user_ids = [room_user.id for room_user, _ in room_users.content]
                
                # Make everyone perform the emote
                for user_id in user_ids:
                    try:
                        await self.highrise.send_emote(emote_id, user_id)
                    except Exception:
                        # Silently ignore if we can't make a specific user emote
                        pass
                        
                await self.highrise.chat(f"Everyone is doing the {emote_name} emote!")
            except Exception as e:
                await self.highrise.chat(f"Error making group emote: {str(e)}")
        else:
            await self.highrise.chat(f"Unknown emote: {emote_name}. Use /emotes to see available emotes.")

    # Outfit customization methods
    
    async def show_outfit_help(self, user: User):
        """Show help for outfit commands."""
        help_text = [
            "📋 Outfit Commands:",
            "/randomoutfit - Generate a random outfit",
            "/equip [item_name] [index] - Equip a specific item (index is optional)",
            "/color [category] [palette_number] - Change color palette of an item",
            "/remove [category] - Remove an item from the outfit",
            "/outfit_categories - List all available clothing categories",
            "/setapikey [your_api_key] - Set the Web API key to enable outfit features",
            "/freeitems - List all available free items",
            "/freeitem [category] [item_number] - Equip a free item from the list"
        ]
        
        # Add API key status
        if not self.webapi:
            help_text.append("⚠️ Web API is not initialized. Use /setapikey to enable outfit features.")
        else:
            help_text.append("✅ Web API is initialized. Outfit features are enabled.")
        
        for line in help_text:
            await self.highrise.send_whisper(user.id, line)

    async def list_outfit_categories(self, user: User):
        """List available outfit categories."""
        categories_text = "👗 Available clothing categories:\n\n"
        for category in self.categories:
            categories_text += f"- {category}\n"
        await self.highrise.send_whisper(user.id, categories_text)
        
    async def list_free_items(self, user: User):
        """List all available free items."""
        # Send a message with the categories of free items
        categories_text = "👕 Free Item Categories:\n\n"
        for category in self.free_items.keys():
            categories_text += f"- {category}\n"
        categories_text += "\nUse /freeitem [category] to list items in a category."
        
        await self.highrise.send_whisper(user.id, categories_text)
        
    async def equip_free_item(self, user: User, message: str):
        """Equip a free item from the list."""
        parts = message.split(" ", 2)
        
        # Check if we have enough parameters
        if len(parts) < 2:
            await self.highrise.send_whisper(user.id, "Usage: /freeitem [category] or /freeitem [category] [item_number]")
            return
            
        category = parts[1].lower()
        
        # Check if the category exists
        if category not in self.free_items:
            categories = ", ".join(self.free_items.keys())
            await self.highrise.send_whisper(user.id, f"Category '{category}' not found. Available categories: {categories}")
            return
            
        # If no item number provided, list items in the category
        if len(parts) < 3:
            items_text = f"👕 Free Items in '{category}':\n\n"
            for i, (item_id, item_name) in enumerate(self.free_items[category].items()):
                items_text += f"{i}: {item_name}\n"
            items_text += "\nUse /freeitem [category] [item_number] to equip an item."
            
            await self.highrise.send_whisper(user.id, items_text)
            return
            
        # Try to equip the item by index
        try:
            item_index = int(parts[2])
            if item_index < 0 or item_index >= len(self.free_items[category]):
                await self.highrise.send_whisper(user.id, f"Item number {item_index} is out of range. Use /freeitem {category} to see available items.")
                return
                
            # Get the item ID by index
            item_id = list(self.free_items[category].keys())[item_index]
            item_name = self.free_items[category][item_id]
            
            # Equip the item
            try:
                # Extract the category from the item_id (format: category-id)
                item_parts = item_id.split('-', 1)
                if len(item_parts) >= 2:
                    category = item_parts[0]
                    # Create outfit item dictionary
                    outfit_item = {category: item_id}
                    await self.highrise.set_outfit(outfit_item)
                    await self.highrise.send_whisper(user.id, f"✅ Successfully equipped {item_name}!")
                else:
                    await self.highrise.send_whisper(user.id, f"❌ Invalid item ID format: {item_id}")
            except Exception as e:
                await self.highrise.send_whisper(user.id, f"❌ Error equipping item: {str(e)}")
        except ValueError:
            await self.highrise.send_whisper(user.id, "Item number must be a valid integer.")
        except Exception as e:
            await self.highrise.send_whisper(user.id, f"❌ Error: {str(e)}")

    async def random_outfit(self, user: User):
        """Generate a random outfit for the bot."""
        if not self.webapi:
            await self.highrise.chat("⚠️ Web API is not initialized. Outfit customization is disabled.")
            return
            
        try:
            # Get current outfit to know what we're working with
            outfit_response = await self.highrise.get_my_outfit()
            current_outfit = outfit_response.outfit
            new_outfit = []
            
            # Keep basic body parts (body) if they exist
            for item in current_outfit:
                category = item.id.split("-")[0]
                if category in ["body"]:
                    new_outfit.append(item)
            
            # Get inventory items
            inventory_response = await self.highrise.get_inventory()
            inventory = inventory_response.items
            
            # Group inventory by category
            items_by_category = {}
            for item in inventory:
                category = item.id.split("-")[0]
                if category not in items_by_category:
                    items_by_category[category] = []
                items_by_category[category].append(item)
            
            # Priority categories that should always be included if available
            priority_categories = [
                "hair_front", "hair_back", "face_hair", "eyebrow", "eye", "nose", "mouth",
                "top", "bottom", "shoes", "accessories", "freckle"
            ]
            
            # Other categories from inventory that aren't in our priority list
            other_categories = set(list(items_by_category.keys()) + list(self.free_items.keys())) - set(priority_categories) - {"body"}
            
            # Add all priority categories to use
            categories_to_use = []
            for category in priority_categories:
                # Check if we have this category in either free items or inventory
                has_free = category in self.free_items and self.free_items[category]
                has_inventory = category in items_by_category and items_by_category[category]
                
                if has_free or has_inventory:
                    categories_to_use.append(category)
            
            # Add other categories with lower probability
            for category in other_categories:
                if random.random() < 0.3:  # 30% chance to include non-priority categories
                    categories_to_use.append(category)
            
            # For each category, decide whether to use inventory item or free item
            for category in categories_to_use:
                # Higher chance to use free items for priority categories
                use_free_item_chance = 0.7 if category in priority_categories else 0.5
                use_free_item = random.random() < use_free_item_chance
                
                if use_free_item and category in self.free_items and self.free_items[category]:
                    # Use a free item
                    item_id = random.choice(list(self.free_items[category].keys()))
                    item_name = self.free_items[category][item_id]
                    
                    # Extract the category from the item_id (format: category-id)
                    item_parts = item_id.split('-', 1)
                    if len(item_parts) >= 2:
                        item_category = item_parts[0]
                        # Add the item directly to the outfit as a dictionary
                        outfit_item = {item_category: item_id}
                        new_outfit.append(outfit_item)
                        await self.highrise.send_whisper(user.id, f"Added free {category}: {item_name}")
                    
                elif category in items_by_category and items_by_category[category]:
                    # Use an inventory item
                    chosen_item = random.choice(items_by_category[category])
                    # Randomly select a color palette if available
                    if hasattr(chosen_item, 'num_palettes') and chosen_item.num_palettes > 1:
                        chosen_item.active_palette = random.randint(0, chosen_item.num_palettes - 1)
                    new_outfit.append(chosen_item)
            
            # Debug output before conversion
            print(f"Debug: New outfit list has {len(new_outfit)} items")
            
            # The set_outfit method expects a list of Item objects
            # We need to convert our free items to proper Item objects
            final_outfit = []
            
            # Keep the inventory items that are already Item objects
            for item in new_outfit:
                if hasattr(item, 'id'):  # This is an inventory Item object
                    final_outfit.append(item)
                    print(f"Debug: Added inventory item: {item.id}")
            
            # Now convert the free items to Item objects
            for item in new_outfit:
                if isinstance(item, dict):  # This is a free item dictionary
                    for category, item_id in item.items():
                        # Create a proper Item object for each free item
                        try:
                            # Import the Item class from highrise.models
                            from highrise.models import Item as HRItem
                            
                            # Create an Item object with only the required attributes
                            # Note: The Item class doesn't accept owner_id parameter
                            new_item = HRItem(
                                id=item_id,
                                active_palette=0,
                                created_at="",
                                rarity="",
                                name=""
                            )
                            final_outfit.append(new_item)
                            print(f"Debug: Added free item as Item object: {item_id}")
                        except Exception as e:
                            print(f"Debug: Error creating Item object: {str(e)}")
            
            # Debug output after conversion
            print(f"Debug: Final outfit has {len(final_outfit)} Item objects")
            
            try:
                # Apply the new outfit with the list of Item objects
                print(f"Debug: Attempting to apply outfit with {len(final_outfit)} Item objects...")
                await self.highrise.set_outfit(final_outfit)
                await self.highrise.chat("🔄 Generated a random outfit with free items!")
                print("Debug: Successfully applied outfit!")
            except Exception as e:
                print(f"Debug: Error applying outfit: {str(e)}")
                
                # If that fails, try using the equip_free_item method for individual items
                print("Debug: Trying to equip items one by one...")
                
                # First, reset to just the body
                try:
                    # Get current outfit
                    outfit_response = await self.highrise.get_my_outfit()
                    body_items = []
                    
                    # Keep only body items
                    for item in outfit_response.outfit:
                        if item.id.startswith("body-"):
                            body_items.append(item)
                    
                    # Set outfit to just body items
                    await self.highrise.set_outfit(body_items)
                    print("Debug: Reset outfit to just body items")
                except Exception as e2:
                    print(f"Debug: Error resetting outfit: {str(e2)}")
                
                # Now try to equip each free item one by one
                success_count = 0
                for category in self.free_items:
                    if self.free_items[category]:  # If category has items
                        try:
                            # Pick a random item from this category
                            item_id = random.choice(list(self.free_items[category].keys()))
                            item_name = self.free_items[category][item_id]
                            
                            # Extract the category from the item_id
                            item_parts = item_id.split('-', 1)
                            if len(item_parts) >= 2:
                                item_category = item_parts[0]
                                # Create outfit item dictionary - this works in equip_free_item
                                outfit_item = {item_category: item_id}
                                await self.highrise.set_outfit(outfit_item)
                                print(f"Debug: Successfully equipped {category}: {item_name}")
                                success_count += 1
                        except Exception as e3:
                            print(f"Debug: Error equipping individual item {category}: {str(e3)}")
                
                if success_count > 0:
                    print(f"Debug: Successfully equipped {success_count} individual items")
                    await self.highrise.chat(f"🔄 Generated a random outfit with {success_count} free items!")
                else:
                    print("Debug: Failed to equip any items individually")
                    await self.highrise.send_whisper(user.id, "Unable to apply random outfit. Please try individual /freeitem commands instead.")
            
            
        except Exception as e:
            await self.highrise.chat(f"Error generating random outfit: {str(e)}")
    
    async def equip_item(self, user: User, message: str):
        """Equip a specific item."""
        if not self.webapi:
            await self.highrise.chat("⚠️ Web API is not initialized. Outfit customization is disabled.")
            return
            
        try:
            # Parse the item name from the message
            parts = message.split(" ")
            if len(parts) < 2:
                await self.highrise.chat("You need to specify the item name.")
                return
                
            item_name = " ".join(parts[1:])
            
            # Check if the last part is a number (index)
            index = 0
            if parts[-1].isdigit():
                item_name = " ".join(parts[1:-1])
                index = int(parts[-1])
                
            # Search for the item
            try:
                items_response = await self.webapi.get_items(item_name=item_name)
                items = items_response.items
            except Exception as e:
                await self.highrise.chat(f"Error searching for item: {e}")
                return
            
            # Check if items were found
            if not items:
                await self.highrise.chat(f"Item '{item_name}' not found.")
                return
            elif len(items) > 1 and index >= len(items):
                await self.highrise.chat(f"Found {len(items)} items but index {index} is out of range.")
                return
            elif len(items) > 1:
                await self.highrise.chat(f"Multiple items found for '{item_name}', using item #{index}: {items[index].item_name}.")
                
            # Select the item
            item = items[index]
            item_id = item.item_id
            category = item.category
            
            # Check if the bot has the item or can get it
            has_item = False
            inventory = (await self.highrise.get_inventory()).items
            
            for inv_item in inventory:
                if inv_item.id == item_id:
                    has_item = True
                    break
                    
            if not has_item:
                # Try to get the item if it's free or purchasable
                if hasattr(item, 'rarity') and item.rarity == "NONE":  # Free item
                    pass  # Can equip directly
                elif hasattr(item, 'is_purchasable') and item.is_purchasable:
                    try:
                        response = await self.highrise.buy_item(item_id)
                        if response != "success":
                            await self.highrise.chat(f"Could not purchase item '{item_name}'.")
                            return
                        await self.highrise.chat(f"Purchased '{item_name}'.")
                    except Exception as e:
                        await self.highrise.chat(f"Error purchasing item: {e}")
                        return
                else:
                    await self.highrise.chat(f"Item '{item_name}' is not in inventory and cannot be purchased.")
                    return
            
            # Get current outfit
            outfit_response = await self.highrise.get_my_outfit()
            outfit = outfit_response.outfit
            
            # Remove items of the same category
            items_to_remove = []
            for outfit_item in outfit:
                item_category = outfit_item.id.split("-")[0]
                if item_category == category:
                    items_to_remove.append(outfit_item)
                    
            for item_to_remove in items_to_remove:
                outfit.remove(item_to_remove)
                
            # If it's a hair_front item, also handle hair_back
            if category == "hair_front" and hasattr(item, "link_ids") and item.link_ids:
                hair_back_id = item.link_ids[0]
                hair_back = Item(
                    type="clothing",
                    amount=1,
                    id=hair_back_id, 
                    account_bound=False,
                    active_palette=0
                )
                outfit.append(hair_back)
                
            # Add the new item
            new_item = Item(
                type="clothing",
                amount=1,
                id=item_id,
                account_bound=False,
                active_palette=0
            )
            outfit.append(new_item)
            
            # Apply the outfit
            await self.highrise.set_outfit(outfit)
            await self.highrise.chat(f"Equipped '{item_name}'!")
            
        except Exception as e:
            await self.highrise.chat(f"Error equipping item: {str(e)}")
    
    async def change_item_color(self, user: User, message: str):
        """Change the color palette of an item."""
        if not self.webapi:
            await self.highrise.chat("⚠️ Web API is not initialized. Outfit customization is disabled.")
            return
            
        try:
            parts = message.split(" ")
            if len(parts) != 3:
                await self.highrise.chat("Invalid format. Use /color [category] [palette_number]")
                return
                
            category = parts[1]
            try:
                color_palette = int(parts[2])
            except ValueError:
                await self.highrise.chat("Palette number must be an integer.")
                return
                
            # Get current outfit
            outfit_response = await self.highrise.get_my_outfit()
            outfit = outfit_response.outfit
            item_found = False
            
            # Find and update the item
            for outfit_item in outfit:
                item_category = outfit_item.id.split("-")[0]
                if item_category == category:
                    try:
                        outfit_item.active_palette = color_palette
                        item_found = True
                    except Exception as e:
                        await self.highrise.chat(f"Error changing color: {str(e)}")
                        return
                        
            if not item_found:
                await self.highrise.chat(f"No item of category '{category}' is currently equipped.")
                return
                
            # Apply the outfit
            await self.highrise.set_outfit(outfit)
            await self.highrise.chat(f"Changed {category} to color palette {color_palette}.")
            
        except Exception as e:
            await self.highrise.chat(f"Error changing item color: {str(e)}")
    
    async def remove_item(self, user: User, message: str):
        """Remove an item from the outfit."""
        if not self.webapi:
            await self.highrise.chat("⚠️ Web API is not initialized. Outfit customization is disabled.")
            return
            
        try:
            parts = message.split(" ")
            if len(parts) != 2:
                await self.highrise.chat("Invalid format. Use /remove [category]")
                return
                
            category = parts[1].lower()
            if category not in self.categories:
                await self.highrise.chat(f"Invalid category '{category}'. Use /outfit_categories to see available categories.")
                return
                
            # Get current outfit
            outfit_response = await self.highrise.get_my_outfit()
            outfit = outfit_response.outfit
            item_found = False
            
            # Find and remove the item
            for outfit_item in outfit:
                item_category = outfit_item.id.split("-")[0]
                if item_category == category:
                    outfit.remove(outfit_item)
                    item_found = True
                    break
                    
            if not item_found:
                await self.highrise.chat(f"No item of category '{category}' is currently equipped.")
                return
                
            # Apply the outfit
            await self.highrise.set_outfit(outfit)
            await self.highrise.chat(f"Removed {category} from outfit.")
            
        except Exception as e:
            await self.highrise.chat(f"Error removing item: {str(e)}")
    
    def load_admin_users(self):
        """Load admin users from JSON file"""
        try:
            if os.path.exists(self.admin_file):
                with open(self.admin_file, 'r') as f:
                    admin_data = json.load(f)
                    self.admin_users = set(admin_data.get('admins', []))
        except Exception as e:
            print(f"Error loading admin users: {e}")
            self.admin_users = set()
    
    def save_admin_users(self):
        """Save admin users to JSON file"""
        try:
            admin_data = {'admins': list(self.admin_users)}
            with open(self.admin_file, 'w') as f:
                json.dump(admin_data, f, indent=2)
        except Exception as e:
            print(f"Error saving admin users: {e}")
    
    def load_overlord_users(self):
        """Load overlord users from JSON file"""
        try:
            if os.path.exists(self.overlord_file):
                with open(self.overlord_file, 'r') as f:
                    overlord_data = json.load(f)
                    self.overlord_users = set(overlord_data.get('overlords', []))
        except Exception as e:
            print(f"Error loading overlord users: {e}")
            self.overlord_users = set()
    
    def save_overlord_users(self):
        """Save overlord users to JSON file"""
        try:
            overlord_data = {'overlords': list(self.overlord_users)}
            with open(self.overlord_file, 'w') as f:
                json.dump(overlord_data, f, indent=2)
        except Exception as e:
            print(f"Error saving overlord users: {e}")
    
    def is_overlord(self, user: User) -> bool:
        """Check if a user is an overlord"""
        return user.id in self.overlord_users
    
    def is_admin(self, user: User) -> bool:
        """Check if a user is an admin or overlord"""
        return user.id in self.admin_users or user.id in self.overlord_users
    
    async def summon_user(self, user: User, message: str):
        """Summon a user to the current location of the summoner"""
        try:
            parts = message.split(" ")
            if len(parts) != 2:
                await self.highrise.chat("Invalid format. Use /summon @username")
                return
            
            target_username = parts[1].strip()
            # Remove @ if present
            if target_username.startswith('@'):
                target_username = target_username[1:]
            
            # Get all users in the room
            room_users = await self.highrise.get_room_users()
            
            # Find the target user
            target_user = None
            for room_user, position in room_users.content:
                if room_user.username.lower() == target_username.lower():
                    target_user = room_user
                    break
            
            if not target_user:
                await self.highrise.chat(f"User '{target_username}' not found in the room.")
                return
            
            # Get the summoner's position
            summoner_position = None
            for room_user, position in room_users.content:
                if room_user.id == user.id:
                    summoner_position = position
                    break
            
            if not summoner_position:
                await self.highrise.chat("Could not determine your position.")
                return
            
            # Teleport the target user to the summoner's position
            await self.highrise.teleport(target_user.id, summoner_position)
            await self.highrise.chat(f"✨ {target_user.username} has been summoned by {user.username}!")
            
        except Exception as e:
            await self.highrise.chat(f"Error summoning user: {str(e)}")
    
    async def add_admin(self, user: User, message: str):
        """Add a user as admin (only existing admins/overlords can do this)"""
        if not self.is_admin(user):
            await self.highrise.chat("❌ Only admins or overlords can add other admins.")
            return
        
        try:
            parts = message.split(" ")
            if len(parts) != 2:
                await self.highrise.chat("Invalid format. Use /addadmin @username")
                return
            
            target_username = parts[1].strip()
            # Remove @ if present
            if target_username.startswith('@'):
                target_username = target_username[1:]
            
            # Get all users in the room
            room_users = await self.highrise.get_room_users()
            
            # Find the target user
            target_user = None
            for room_user, position in room_users.content:
                if room_user.username.lower() == target_username.lower():
                    target_user = room_user
                    break
            
            if not target_user:
                await self.highrise.chat(f"User '{target_username}' not found in the room.")
                return
            
            if target_user.id in self.admin_users:
                await self.highrise.chat(f"{target_user.username} is already an admin.")
                return
            
            self.admin_users.add(target_user.id)
            self.save_admin_users()
            await self.highrise.chat(f"👑 {target_user.username} has been added as an admin by {user.username}!")
            
        except Exception as e:
            await self.highrise.chat(f"Error adding admin: {str(e)}")
    
    async def remove_admin(self, user: User, message: str):
        """Remove a user from admin (only existing admins/overlords can do this)"""
        if not self.is_admin(user):
            await self.highrise.chat("❌ Only admins or overlords can remove other admins.")
            return
        
        # Overlords cannot be removed by regular admins
        try:
            parts = message.split(" ")
            if len(parts) != 2:
                await self.highrise.chat("Invalid format. Use /removeadmin @username")
                return
            
            target_username = parts[1].strip()
            if target_username.startswith('@'):
                target_username = target_username[1:]
            
            room_users = await self.highrise.get_room_users()
            target_user = None
            for room_user, position in room_users.content:
                if room_user.username.lower() == target_username.lower():
                    target_user = room_user
                    break
            
            if not target_user:
                await self.highrise.chat(f"User '{target_username}' not found in the room.")
                return
            
            # Check if target is an overlord and current user is not overlord
            if target_user.id in self.overlord_users and not self.is_overlord(user):
                await self.highrise.chat("❌ Only overlords can remove other overlords from admin status.")
                return
                
        except Exception as e:
            await self.highrise.chat(f"Error checking user permissions: {str(e)}")
            return
        
        try:
            parts = message.split(" ")
            if len(parts) != 2:
                await self.highrise.chat("Invalid format. Use /removeadmin @username")
                return
            
            target_username = parts[1].strip()
            # Remove @ if present
            if target_username.startswith('@'):
                target_username = target_username[1:]
            
            # Get all users in the room
            room_users = await self.highrise.get_room_users()
            
            # Find the target user
            target_user = None
            for room_user, position in room_users.content:
                if room_user.username.lower() == target_username.lower():
                    target_user = room_user
                    break
            
            if not target_user:
                await self.highrise.chat(f"User '{target_username}' not found in the room.")
                return
            
            if target_user.id not in self.admin_users:
                await self.highrise.chat(f"{target_user.username} is not an admin.")
                return
            
            self.admin_users.remove(target_user.id)
            self.save_admin_users()
            await self.highrise.chat(f"👑 {target_user.username} has been removed as an admin by {user.username}.")
            
        except Exception as e:
            await self.highrise.chat(f"Error removing admin: {str(e)}")
    
    async def list_admins(self, user: User):
        """List all current admins"""
        if not self.admin_users:
            await self.highrise.chat("No admins are currently set.")
            return
        
        try:
            # Get all users in the room to match IDs with usernames
            room_users = await self.highrise.get_room_users()
            admin_names = []
            
            for room_user, position in room_users.content:
                if room_user.id in self.admin_users:
                    admin_names.append(room_user.username)
            
            if admin_names:
                admin_list = "\n".join([f"👑 {name}" for name in admin_names])
                await self.highrise.send_whisper(user.id, f"Current Admins:\n{admin_list}")
            else:
                await self.highrise.chat("No admins are currently in the room.")
                
        except Exception as e:
            await self.highrise.chat(f"Error listing admins: {str(e)}")
    
    async def add_overlord(self, user: User, message: str):
        """Add a user as overlord (only existing overlords can do this)"""
        if not self.is_overlord(user):
            await self.highrise.chat("⚡ Only overlords can add other overlords.")
            return
        
        try:
            parts = message.split(" ")
            if len(parts) != 2:
                await self.highrise.chat("Invalid format. Use /addoverlord @username")
                return
            
            target_username = parts[1].strip()
            if target_username.startswith('@'):
                target_username = target_username[1:]
            
            room_users = await self.highrise.get_room_users()
            target_user = None
            for room_user, position in room_users.content:
                if room_user.username.lower() == target_username.lower():
                    target_user = room_user
                    break
            
            if not target_user:
                await self.highrise.chat(f"User '{target_username}' not found in the room.")
                return
            
            if target_user.id in self.overlord_users:
                await self.highrise.chat(f"{target_user.username} is already an overlord.")
                return
            
            self.overlord_users.add(target_user.id)
            # Also add as admin if not already
            if target_user.id not in self.admin_users:
                self.admin_users.add(target_user.id)
                self.save_admin_users()
            self.save_overlord_users()
            await self.highrise.chat(f"⚡ {target_user.username} has been granted OVERLORD status by {user.username}!")
            
        except Exception as e:
            await self.highrise.chat(f"Error adding overlord: {str(e)}")
    
    async def remove_overlord(self, user: User, message: str):
        """Remove a user from overlord (only existing overlords can do this)"""
        if not self.is_overlord(user):
            await self.highrise.chat("⚡ Only overlords can remove other overlords.")
            return
        
        try:
            parts = message.split(" ")
            if len(parts) != 2:
                await self.highrise.chat("Invalid format. Use /removeoverlord @username")
                return
            
            target_username = parts[1].strip()
            if target_username.startswith('@'):
                target_username = target_username[1:]
            
            room_users = await self.highrise.get_room_users()
            target_user = None
            for room_user, position in room_users.content:
                if room_user.username.lower() == target_username.lower():
                    target_user = room_user
                    break
            
            if not target_user:
                await self.highrise.chat(f"User '{target_username}' not found in the room.")
                return
            
            if target_user.id not in self.overlord_users:
                await self.highrise.chat(f"{target_user.username} is not an overlord.")
                return
            
            self.overlord_users.remove(target_user.id)
            self.save_overlord_users()
            await self.highrise.chat(f"⚡ {target_user.username} has been removed from OVERLORD status by {user.username}.")
            
        except Exception as e:
            await self.highrise.chat(f"Error removing overlord: {str(e)}")
    
    async def list_overlords(self, user: User):
        """List all current overlords"""
        if not self.overlord_users:
            await self.highrise.chat("No overlords are currently set.")
            return
        
        try:
            room_users = await self.highrise.get_room_users()
            overlord_names = []
            
            for room_user, position in room_users.content:
                if room_user.id in self.overlord_users:
                    overlord_names.append(room_user.username)
            
            if overlord_names:
                overlord_list = "\n".join([f"⚡ {name}" for name in overlord_names])
                await self.highrise.send_whisper(user.id, f"Current Overlords:\n{overlord_list}")
            else:
                await self.highrise.chat("No overlords are currently in the room.")
                
        except Exception as e:
            await self.highrise.chat(f"Error listing overlords: {str(e)}")
    
    async def show_bot_info(self, user: User):
        """Show detailed bot information (overlord only)"""
        if not self.is_overlord(user):
            await self.highrise.chat("⚡ Only overlords can view bot information.")
            return
        
        try:
            room_users = await self.highrise.get_room_users()
            user_count = len(room_users.content)
            admin_count = len(self.admin_users)
            overlord_count = len(self.overlord_users)
            teleport_count = len(self.teleport_points)
            
            info_text = (
                f"🤖 Bot Information:\n"
                f"Users in room: {user_count}\n"
                f"Total admins: {admin_count}\n"
                f"Total overlords: {overlord_count}\n"
                f"Teleport points: {teleport_count}\n"
                f"API Status: {'✅ Active' if self.webapi else '❌ Inactive'}"
            )
            await self.highrise.send_whisper(user.id, info_text)
            
        except Exception as e:
            await self.highrise.chat(f"Error getting bot info: {str(e)}")
    
    async def clear_room(self, user: User):
        """Clear all users from the room except overlords (overlord only)"""
        if not self.is_overlord(user):
            await self.highrise.chat("⚡ Only overlords can clear the room.")
            return
        
        try:
            room_users = await self.highrise.get_room_users()
            cleared_count = 0
            
            for room_user, position in room_users.content:
                # Don't kick overlords or the bot itself
                if room_user.id not in self.overlord_users and room_user.id != user.id:
                    try:
                        # Note: Highrise API might not have a direct kick method
                        # This is a placeholder for the concept
                        await self.highrise.chat(f"🚪 {room_user.username} would be cleared from room (kick functionality may need API support)")
                        cleared_count += 1
                    except Exception as e:
                        print(f"Could not clear user {room_user.username}: {e}")
            
            await self.highrise.chat(f"🧹 Room clear initiated by {user.username}. {cleared_count} users processed.")
            
        except Exception as e:
            await self.highrise.chat(f"Error clearing room: {str(e)}")
    
    async def announce_message(self, user: User, message: str):
        """Send an announcement message to all users (overlord only)"""
        if not self.is_overlord(user):
            await self.highrise.chat("⚡ Only overlords can make announcements.")
            return
        
        try:
            announcement = message[10:].strip()  # Remove '/announce '
            if not announcement:
                await self.highrise.chat("Invalid format. Use /announce [message]")
                return
            
            await self.highrise.chat(f"📢 ANNOUNCEMENT FROM {user.username.upper()}: {announcement}")
            
        except Exception as e:
            await self.highrise.chat(f"Error making announcement: {str(e)}")
    
    async def kick_user(self, user: User, message: str):
        """Kick a user from the room (overlord only)"""
        if not self.is_overlord(user):
            await self.highrise.chat("⚡ Only overlords can kick users.")
            return
        
        try:
            parts = message.split(" ")
            if len(parts) != 2:
                await self.highrise.chat("Invalid format. Use /kick @username")
                return
            
            target_username = parts[1].strip()
            if target_username.startswith('@'):
                target_username = target_username[1:]
            
            room_users = await self.highrise.get_room_users()
            target_user = None
            for room_user, position in room_users.content:
                if room_user.username.lower() == target_username.lower():
                    target_user = room_user
                    break
            
            if not target_user:
                await self.highrise.chat(f"User '{target_username}' not found in the room.")
                return
            
            # Cannot kick other overlords
            if target_user.id in self.overlord_users:
                await self.highrise.chat("⚡ Cannot kick other overlords.")
                return
            
            # Note: Actual kick functionality depends on Highrise API capabilities
            await self.highrise.chat(f"🚪 {target_user.username} has been kicked by overlord {user.username}!")
            # Placeholder for actual kick implementation when API supports it
            
        except Exception as e:
            await self.highrise.chat(f"Error kicking user: {str(e)}")
    
    async def shutdown_bot(self, user: User):
        """Shutdown the bot (overlord only)"""
        if not self.is_overlord(user):
            await self.highrise.chat("⚡ Only overlords can shutdown the bot.")
            return
        
        await self.highrise.chat(f"🔴 Bot shutdown initiated by overlord {user.username}. Goodbye!")
        # Save all data before shutdown
        self.save_admin_users()
        self.save_overlord_users()
        self.save_teleport_points()
        
        # Graceful shutdown
        import sys
        sys.exit(0)
            
    # These methods are removed as they're no longer needed with the human DJ approach