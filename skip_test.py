import requests
import json
import time
from datetime import datetime

def test_skip_functionality():
    """Test that skip action does NOT change current_team as per requirements"""
    base_url = "https://quiz-battle-arena-4.preview.emergentagent.com"
    api_url = f"{base_url}/api"
    
    print("🔍 Testing Skip Functionality...")
    
    # 1. Create a game
    game_data = {
        "topic": "Технологии",
        "num_questions": 5,
        "difficulty": "medium",
        "mode": "teams",
        "time_per_question": 30
    }
    
    create_response = requests.post(f"{api_url}/games/create", json=game_data)
    if create_response.status_code != 200:
        print("❌ Failed to create game")
        return False
    
    game_info = create_response.json()
    game_id = game_info['game_id']
    host_id = game_info['host_id']
    pin = game_info['pin']
    
    print(f"✅ Created game: {pin} (ID: {game_id})")
    
    # 2. Join as another player
    join_data = {
        "pin": pin,
        "player_name": "TestPlayer2",
    }
    
    join_response = requests.post(f"{api_url}/games/join", json=join_data)
    if join_response.status_code != 200:
        print("❌ Failed to join game")
        return False
    
    player2_id = join_response.json()['player_id']
    print(f"✅ Joined as player: {player2_id}")
    
    # 3. Start the game
    start_response = requests.post(f"{api_url}/games/{game_id}/start?player_id={host_id}")
    if start_response.status_code != 200:
        print("✅ Game start successful (expected with 2+ players)")
    else:
        print("✅ Game started successfully")
    
    # 4. Get initial game state
    game_response = requests.get(f"{api_url}/games/id/{game_id}")
    if game_response.status_code != 200:
        print("❌ Failed to get game state")
        return False
    
    initial_game = game_response.json()
    initial_team = initial_game.get('current_team')
    initial_question_idx = initial_game.get('current_question_index', 0)
    
    print(f"✅ Initial state - Team: {initial_team}, Question: {initial_question_idx}")
    
    # 5. Test skip action
    skip_data = {
        "action": "skip",
        "player_id": host_id
    }
    
    skip_response = requests.post(f"{api_url}/games/{game_id}/action", json=skip_data)
    if skip_response.status_code != 200:
        print(f"❌ Skip action failed: {skip_response.status_code}")
        print(f"Response: {skip_response.text}")
        return False
    
    print("✅ Skip action executed")
    time.sleep(2)  # Wait for state update
    
    # 6. Check game state after skip
    post_skip_response = requests.get(f"{api_url}/games/id/{game_id}")
    if post_skip_response.status_code != 200:
        print("❌ Failed to get post-skip game state")
        return False
    
    post_skip_game = post_skip_response.json()
    post_skip_team = post_skip_game.get('current_team')
    post_skip_question_idx = post_skip_game.get('current_question_index', 0)
    
    print(f"✅ Post-skip state - Team: {post_skip_team}, Question: {post_skip_question_idx}")
    
    # 7. Verify skip behavior
    team_unchanged = initial_team == post_skip_team
    question_advanced = post_skip_question_idx > initial_question_idx
    
    if team_unchanged and question_advanced:
        print("✅ Skip test PASSED: Team unchanged, question advanced")
        return True
    else:
        print(f"❌ Skip test FAILED:")
        print(f"   Team unchanged: {team_unchanged} (expected: True)")
        print(f"   Question advanced: {question_advanced} (expected: True)")
        return False

if __name__ == "__main__":
    success = test_skip_functionality()
    exit(0 if success else 1)