import requests
import json
import sys
import time
from datetime import datetime

class BrainBattleAPITester:
    def __init__(self, base_url="https://quiz-battle-arena-4.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.user_data = None
        self.game_data = None
        self.tests_run = 0
        self.tests_passed = 0
        self.critical_failures = []
        self.session = requests.Session()

    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        if headers:
            test_headers.update(headers)
        if self.token:
            test_headers['Authorization'] = f'Bearer {self.token}'

        self.tests_run += 1
        self.log(f"Testing {name}...")
        
        try:
            if method == 'GET':
                response = self.session.get(url, headers=test_headers, timeout=30)
            elif method == 'POST':
                response = self.session.post(url, json=data, headers=test_headers, timeout=30)
            elif method == 'PUT':
                response = self.session.put(url, json=data, headers=test_headers, timeout=30)
            elif method == 'DELETE':
                response = self.session.delete(url, headers=test_headers, timeout=30)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                self.log(f"✅ {name} - Status: {response.status_code}")
                try:
                    return success, response.json() if response.content else {}
                except:
                    return success, {"status": "success", "raw_response": response.text[:200]}
            else:
                error_msg = f"❌ {name} - Expected {expected_status}, got {response.status_code}"
                if response.content:
                    try:
                        error_detail = response.json().get('detail', response.text[:200])
                        error_msg += f" | Error: {error_detail}"
                    except:
                        error_msg += f" | Response: {response.text[:200]}"
                self.log(error_msg)
                if response.status_code >= 500:
                    self.critical_failures.append(f"{name}: {response.status_code}")
                return False, {}

        except requests.exceptions.Timeout:
            self.log(f"❌ {name} - Request timeout (30s)")
            self.critical_failures.append(f"{name}: Timeout")
            return False, {}
        except Exception as e:
            self.log(f"❌ {name} - Error: {str(e)}")
            if "Connection" in str(e):
                self.critical_failures.append(f"{name}: Connection Error")
            return False, {}

    def test_health_check(self):
        """Test API health endpoint"""
        success, response = self.run_test("Health Check", "GET", "", 200)
        if success:
            self.log(f"API running with {response.get('active_games', 0)} active games")
        return success

    def test_health_endpoint(self):
        """Test dedicated health endpoint"""
        success, response = self.run_test("Health Endpoint", "GET", "health", 200)
        if success:
            ai_enabled = response.get('ai_enabled', False)
            self.log(f"Health: AI enabled = {ai_enabled}")
        return success

    def test_register_user(self):
        """Test user registration"""
        timestamp = datetime.now().strftime("%H%M%S")
        user_data = {
            "username": f"testuser_{timestamp}",
            "email": f"test_{timestamp}@brainbattle.com",
            "password": "TestPass123!"
        }
        
        success, response = self.run_test("User Registration", "POST", "auth/register", 200, user_data)
        if success:
            self.token = response.get('token')
            self.user_data = response.get('user')
            self.log(f"Registered user: {self.user_data.get('username')} (ID: {self.user_data.get('id')})")
        return success

    def test_login_user(self):
        """Test user login with registered credentials"""
        if not self.user_data:
            return False
        
        login_data = {
            "email": self.user_data['email'],
            "password": "TestPass123!"
        }
        
        success, response = self.run_test("User Login", "POST", "auth/login", 200, login_data)
        if success:
            self.token = response.get('token')
            self.log("Login successful")
        return success

    def test_get_me(self):
        """Test get current user endpoint"""
        success, response = self.run_test("Get Current User", "GET", "auth/me", 200)
        if success:
            self.log(f"Current user: {response.get('username')} (Rating: {response.get('rating', 0)})")
        return success

    def test_create_game(self):
        """Test game creation"""
        game_data = {
            "topic": "Технологии",
            "num_questions": 5,
            "difficulty": "medium", 
            "mode": "teams",
            "time_per_question": 30
        }
        
        success, response = self.run_test("Create Game", "POST", "games/create", 200, game_data)
        if success:
            self.game_data = response
            self.log(f"Created game with PIN: {response.get('pin')} (ID: {response.get('game_id')})")
            self.log(f"Questions generated: {response.get('questions_count', 0)}, AI used: {response.get('ai_used', False)}")
        return success

    def test_get_game_by_pin(self):
        """Test retrieving game by PIN"""
        if not self.game_data:
            return False
        
        pin = self.game_data.get('pin')
        success, response = self.run_test("Get Game by PIN", "GET", f"games/{pin}", 200)
        if success:
            self.log(f"Retrieved game: {response.get('topic')} ({response.get('mode')}, {response.get('difficulty')})")
            self.log(f"Players: {len(response.get('players', []))}, State: {response.get('state')}")
        return success

    def test_join_game(self):
        """Test joining a game"""
        if not self.game_data:
            return False
        
        join_data = {
            "pin": self.game_data.get('pin'),
            "player_name": f"TestPlayer_{datetime.now().strftime('%S')}",
            "user_id": self.user_data.get('id') if self.user_data else None
        }
        
        success, response = self.run_test("Join Game", "POST", "games/join", 200, join_data)
        if success:
            self.log(f"Joined game as player {join_data['player_name']}")
            self.game_data.update({
                'player_id': response.get('player_id'),
                'player_name': join_data['player_name']
            })
        return success

    def test_choose_team(self):
        """Test team selection"""
        if not self.game_data or not self.game_data.get('player_id'):
            return False
        
        team_data = {
            "game_id": self.game_data.get('game_id'),
            "player_id": self.game_data.get('player_id'),
            "team": "B"
        }
        
        success, response = self.run_test("Choose Team", "POST", "games/choose-team", 200, team_data)
        if success:
            self.log("Successfully switched to Team B")
        return success

    def test_start_game(self):
        """Test starting a game (host only)"""
        if not self.game_data:
            return False
        
        # Use form data for POST request
        start_data = {
            "player_id": self.game_data.get('host_id')
        }
        
        game_id = self.game_data.get('game_id')
        success, response = self.run_test("Start Game", "POST", f"games/{game_id}/start?player_id={start_data['player_id']}", 200)
        if success:
            self.log("Game started successfully")
        return success

    def test_game_action_answer(self):
        """Test submitting an answer"""
        if not self.game_data:
            return False
        
        action_data = {
            "action": "answer",
            "player_id": self.game_data.get('host_id'),
            "data": {"answer_index": 0}
        }
        
        game_id = self.game_data.get('game_id')
        success, response = self.run_test("Submit Answer", "POST", f"games/{game_id}/action", 200, action_data)
        if success:
            self.log(f"Answer submitted. Correct: {response.get('is_correct', False)}")
        return success

    def test_game_pause_resume(self):
        """Test game pause/resume (host only)"""
        if not self.game_data:
            return False
        
        # Test pause
        pause_data = {
            "action": "pause",
            "player_id": self.game_data.get('host_id')
        }
        
        game_id = self.game_data.get('game_id')
        success, response = self.run_test("Pause Game", "POST", f"games/{game_id}/action", 200, pause_data)
        
        if success:
            self.log("Game paused")
            time.sleep(1)
            
            # Test resume
            resume_data = {
                "action": "resume", 
                "player_id": self.game_data.get('host_id')
            }
            
            success2, response2 = self.run_test("Resume Game", "POST", f"games/{game_id}/action", 200, resume_data)
            if success2:
                self.log("Game resumed")
            return success2
        return False

    def test_leaderboard(self):
        """Test leaderboard endpoint"""
        success, response = self.run_test("Get Leaderboard", "GET", "leaderboard", 200)
        if success:
            users = response if isinstance(response, list) else []
            self.log(f"Leaderboard retrieved with {len(users)} users")
        return success

    def test_get_game_stats(self):
        """Test game statistics"""
        if not self.game_data:
            return False
        
        game_id = self.game_data.get('game_id')
        success, response = self.run_test("Game Statistics", "GET", f"games/{game_id}/stats", 200)
        if success:
            self.log(f"Stats: Winner={response.get('winner')}, State={response.get('state')}")
        return success

    def run_all_tests(self):
        """Run comprehensive API test suite"""
        self.log("🚀 Starting BrainBattle API Tests", "START")
        
        # Core API tests
        test_results = {
            "basic": [
                ("Health Check", self.test_health_check),
                ("Health Endpoint", self.test_health_endpoint),
            ],
            "auth": [
                ("User Registration", self.test_register_user),
                ("User Login", self.test_login_user),
                ("Get Current User", self.test_get_me),
            ],
            "game_management": [
                ("Create Game", self.test_create_game),
                ("Get Game by PIN", self.test_get_game_by_pin),
                ("Join Game", self.test_join_game),
                ("Choose Team", self.test_choose_team),
            ],
            "gameplay": [
                ("Start Game", self.test_start_game),
                ("Submit Answer", self.test_game_action_answer),
                ("Pause/Resume Game", self.test_game_pause_resume),
            ],
            "stats": [
                ("Leaderboard", self.test_leaderboard),
                ("Game Statistics", self.test_get_game_stats),
            ]
        }

        category_results = {}
        
        for category, tests in test_results.items():
            self.log(f"\n📊 Testing {category.upper()} endpoints:", "CATEGORY")
            category_passed = 0
            category_total = len(tests)
            
            for test_name, test_func in tests:
                try:
                    result = test_func()
                    if result:
                        category_passed += 1
                    time.sleep(0.5)  # Brief pause between tests
                except Exception as e:
                    self.log(f"❌ {test_name} - Exception: {str(e)}", "ERROR")
            
            category_results[category] = (category_passed, category_total)
            success_rate = (category_passed / category_total) * 100 if category_total > 0 else 0
            self.log(f"✅ {category.upper()}: {category_passed}/{category_total} ({success_rate:.1f}%)", "RESULT")

        # Final results
        self.log(f"\n🏁 FINAL RESULTS:", "SUMMARY")
        self.log(f"Total Tests: {self.tests_run}", "SUMMARY")
        self.log(f"Passed: {self.tests_passed}", "SUMMARY")
        self.log(f"Failed: {self.tests_run - self.tests_passed}", "SUMMARY")
        overall_success = (self.tests_passed / self.tests_run) * 100 if self.tests_run > 0 else 0
        self.log(f"Success Rate: {overall_success:.1f}%", "SUMMARY")
        
        if self.critical_failures:
            self.log(f"⚠️  Critical Failures: {', '.join(self.critical_failures)}", "CRITICAL")
        
        # Return data for further analysis
        return {
            "total_tests": self.tests_run,
            "passed_tests": self.tests_passed,
            "success_rate": overall_success,
            "category_results": category_results,
            "critical_failures": self.critical_failures,
            "game_data": self.game_data
        }

def main():
    tester = BrainBattleAPITester()
    results = tester.run_all_tests()
    
    # Exit with error code if tests failed
    if results["success_rate"] < 80:
        sys.exit(1)
    return 0

if __name__ == "__main__":
    sys.exit(main())