#!/usr/bin/env python3
"""
Setup script to add the first overlord to the lilybud420 bot.
This script helps set up YooNeqK as the initial overlord.
"""

import json
import os

def setup_overlord_by_id():
    """Setup overlord using Highrise User ID"""
    print("🔧 Lilybud420 Bot - Overlord Setup (by User ID)")
    print("=" * 50)
    
    # Get user ID
    user_id = input("Enter your Highrise User ID: ").strip()
    
    if not user_id:
        print("❌ User ID cannot be empty!")
        return False
    
    return create_overlord_files(user_id, "User ID: " + user_id)

def setup_overlord_placeholder():
    """Setup placeholder for YooNeqK to be promoted when bot runs"""
    print("🔧 Lilybud420 Bot - Overlord Setup (by Username)")
    print("=" * 50)
    print("Setting up YooNeqK as overlord...")
    
    # Create a special marker file that the bot can check
    marker_data = {
        'pending_overlord': 'YooNeqK',
        'note': 'This user should be automatically promoted to overlord when they join'
    }
    
    try:
        with open('pending_overlord.json', 'w') as f:
            json.dump(marker_data, f, indent=2)
        
        print("✅ Created pending overlord marker for YooNeqK")
        print("📁 Created file: pending_overlord.json")
        print("\n🤖 The bot will automatically promote YooNeqK to overlord when they first join the room!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating marker file: {e}")
        return False

def create_overlord_files(user_id, identifier):
    """Create the overlord and admin JSON files"""
    # Create overlord data
    overlord_data = {
        'overlords': [user_id]
    }
    
    # Create admin data (overlords are also admins)
    admin_data = {
        'admins': [user_id]
    }
    
    try:
        # Save overlord file
        with open('overlord_users.json', 'w') as f:
            json.dump(overlord_data, f, indent=2)
        
        # Save admin file
        with open('admin_users.json', 'w') as f:
            json.dump(admin_data, f, indent=2)
        
        print(f"✅ Successfully set up overlord access for: {identifier}")
        print("📁 Created files:")
        print("   - overlord_users.json")
        print("   - admin_users.json")
        print("\n🚀 You can now start the bot and use overlord commands!")
        print("\n⚡ Available Overlord Commands:")
        print("   - /addoverlord @username: Grant overlord status")
        print("   - /removeoverlord @username: Remove overlord status") 
        print("   - /overlords: List all overlords")
        print("   - /botinfo: Show detailed bot information")
        print("   - /announce [message]: Broadcast announcement")
        print("   - /kick @username: Kick user from room")
        print("   - /clearroom: Clear all non-overlords")
        print("   - /shutdown: Gracefully shutdown bot")
        return True
        
    except Exception as e:
        print(f"❌ Error setting up overlord: {e}")
        return False

def main():
    print("🎮 Lilybud420 Bot - Overlord Setup")
    print("=" * 40)
    print("Choose setup method:")
    print("1. Setup by User ID (if you know your Highrise User ID)")
    print("2. Setup for YooNeqK (auto-promote when joining room)")
    print("3. Exit")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == '1':
        setup_overlord_by_id()
    elif choice == '2':
        setup_overlord_placeholder()
    elif choice == '3':
        print("👋 Goodbye!")
    else:
        print("❌ Invalid choice. Please run the script again.")

if __name__ == "__main__":
    main()
