import { createContext, useContext, useState, useEffect, useRef, useCallback } from 'react';
import { WS_URL, API, storage, STORAGE_KEYS } from '../utils';
import axios from 'axios';

const GameContext = createContext(null);

export function GameProvider({ children }) {
  const [game, setGame] = useState(null);
  const [playerId, setPlayerId] = useState(null);
  const [playerName, setPlayerName] = useState(null);
  const [connected, setConnected] = useState(false);
  const [event, setEvent] = useState(null);
  const wsRef = useRef(null);
  const reconnectTimer = useRef(null);
  const pingInterval = useRef(null);

  // Load from storage on mount
  useEffect(() => {
    const savedPlayerId = storage.get(STORAGE_KEYS.PLAYER_ID);
    const savedPlayerName = storage.get(STORAGE_KEYS.PLAYER_NAME);
    if (savedPlayerId) setPlayerId(savedPlayerId);
    if (savedPlayerName) setPlayerName(savedPlayerName);
  }, []);

  const connectWS = useCallback((gameId, pId) => {
    if (wsRef.current) {
      wsRef.current.close();
    }

    const wsUrl = `${WS_URL}/ws/${gameId}/${pId}`;
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      setConnected(true);
      // Start ping
      pingInterval.current = setInterval(() => {
        if (ws.readyState === WebSocket.OPEN) {
          ws.send(JSON.stringify({ type: 'ping' }));
        }
      }, 15000);
    };

    ws.onmessage = (e) => {
      try {
        const msg = JSON.parse(e.data);
        if (msg.type === 'game_state') {
          const data = msg.data;
          if (data._event) {
            setEvent(data._event);
          }
          setGame({ ...data });
        }
      } catch {}
    };

    ws.onclose = () => {
      setConnected(false);
      clearInterval(pingInterval.current);
      // Reconnect after 3s
      reconnectTimer.current = setTimeout(() => {
        connectWS(gameId, pId);
      }, 3000);
    };

    ws.onerror = () => {
      ws.close();
    };
  }, []);

  const disconnectWS = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    clearInterval(pingInterval.current);
    clearTimeout(reconnectTimer.current);
    setConnected(false);
  }, []);

  const fetchGame = useCallback(async (gameId) => {
    try {
      const res = await axios.get(`${API}/games/id/${gameId}`);
      setGame(res.data);
      return res.data;
    } catch (e) {
      return null;
    }
  }, []);

  const joinGame = useCallback(async (pin, name, password, userId) => {
    const res = await axios.post(`${API}/games/join`, {
      pin,
      player_name: name,
      password: password || undefined,
      user_id: userId || undefined,
    });
    const { game_id, player_id, game: gameData } = res.data;

    setGame(gameData);
    setPlayerId(player_id);
    setPlayerName(name);
    storage.set(STORAGE_KEYS.PLAYER_ID, player_id);
    storage.set(STORAGE_KEYS.PLAYER_NAME, name);
    storage.set(STORAGE_KEYS.GAME_ID, game_id);
    storage.set(STORAGE_KEYS.PIN, pin);

    connectWS(game_id, player_id);
    return { game_id, player_id, game: gameData };
  }, [connectWS]);

  const startGame = useCallback(async (gameId, pId) => {
    const res = await axios.post(`${API}/games/${gameId}/start?player_id=${pId}`);
    return res.data;
  }, []);

  const sendAction = useCallback(async (gameId, action, pId, data) => {
    const res = await axios.post(`${API}/games/${gameId}/action`, {
      action,
      player_id: pId,
      data: data || null,
    });
    return res.data;
  }, []);

  const chooseTeam = useCallback(async (gameId, pId, team) => {
    const res = await axios.post(`${API}/games/choose-team`, {
      game_id: gameId,
      player_id: pId,
      team,
    });
    return res.data;
  }, []);

  const clearGame = useCallback(() => {
    disconnectWS();
    setGame(null);
    setPlayerId(null);
    setPlayerName(null);
    setEvent(null);
    storage.remove(STORAGE_KEYS.PLAYER_ID);
    storage.remove(STORAGE_KEYS.PLAYER_NAME);
    storage.remove(STORAGE_KEYS.GAME_ID);
    storage.remove(STORAGE_KEYS.PIN);
  }, [disconnectWS]);

  // Rejoin on refresh
  const rejoin = useCallback(async () => {
    const savedGameId = storage.get(STORAGE_KEYS.GAME_ID);
    const savedPlayerId = storage.get(STORAGE_KEYS.PLAYER_ID);
    const savedPlayerName = storage.get(STORAGE_KEYS.PLAYER_NAME);
    const savedPin = storage.get(STORAGE_KEYS.PIN);

    if (!savedGameId || !savedPlayerId) return null;

    try {
      const res = await axios.get(`${API}/games/id/${savedGameId}`);
      const gameData = res.data;
      setGame(gameData);
      setPlayerId(savedPlayerId);
      setPlayerName(savedPlayerName);
      connectWS(savedGameId, savedPlayerId);
      return { game: gameData, playerId: savedPlayerId, playerName: savedPlayerName, pin: savedPin };
    } catch {
      storage.remove(STORAGE_KEYS.GAME_ID);
      storage.remove(STORAGE_KEYS.PLAYER_ID);
      return null;
    }
  }, [connectWS]);

  return (
    <GameContext.Provider value={{
      game, playerId, playerName, connected, event,
      setGame, setPlayerId, setPlayerName, setEvent,
      joinGame, startGame, sendAction, chooseTeam,
      connectWS, disconnectWS, clearGame, fetchGame, rejoin,
    }}>
      {children}
    </GameContext.Provider>
  );
}

export function useGame() {
  return useContext(GameContext);
}
