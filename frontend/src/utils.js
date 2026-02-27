// Shared utilities and constants
export const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
export const API = `${BACKEND_URL}/api`;
export const WS_URL = BACKEND_URL.replace(/^https/, 'wss').replace(/^http/, 'ws');

// Local storage keys
export const STORAGE_KEYS = {
  TOKEN: 'bb_token',
  USER: 'bb_user',
  PLAYER_ID: 'bb_player_id',
  PLAYER_NAME: 'bb_player_name',
  GAME_ID: 'bb_game_id',
  PIN: 'bb_pin',
};

// Team colors
export const TEAM_COLORS = {
  A: { text: '#FF6B35', bg: 'rgba(255,107,53,0.1)', border: 'rgba(255,107,53,0.4)', name: 'КОМАНДА А' },
  B: { text: '#00B4D8', bg: 'rgba(0,180,216,0.1)', border: 'rgba(0,180,216,0.4)', name: 'КОМАНДА Б' },
};

export const DIFFICULTY_LABELS = {
  easy: 'ЛЁГКИЙ',
  medium: 'СРЕДНИЙ',
  hard: 'СЛОЖНЫЙ',
};

export const MODE_LABELS = {
  teams: 'КОМАНДНЫЙ',
  ffa: 'КАЖДЫЙ ЗА СЕБЯ',
};

// Format time mm:ss
export function formatTime(seconds) {
  const s = Math.max(0, Math.floor(seconds));
  return s > 0 ? `${s}` : '0';
}

// Get player's current turn in team
export function getCurrentTurnPlayer(game) {
  if (!game || game.mode !== 'teams') return null;
  const team = game.current_team;
  const teamPlayers = game.teams?.[team] || [];
  if (!teamPlayers.length) return null;
  const idx = (game.current_player_index?.[team] || 0) % teamPlayers.length;
  return teamPlayers[idx];
}

// Storage helpers
export const storage = {
  get: (key) => {
    try { return JSON.parse(localStorage.getItem(key)); } catch { return null; }
  },
  set: (key, val) => {
    try { localStorage.setItem(key, JSON.stringify(val)); } catch {}
  },
  remove: (key) => {
    try { localStorage.removeItem(key); } catch {}
  },
};
