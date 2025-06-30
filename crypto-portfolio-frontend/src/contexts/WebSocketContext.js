import React, { createContext, useContext, useState, useEffect, useRef } from 'react';

const WebSocketContext = createContext();

export const useWebSocket = () => {
  const context = useContext(WebSocketContext);
  if (!context) {
    throw new Error('useWebSocket must be used within a WebSocketProvider');
  }
  return context;
};

export const WebSocketProvider = ({ children }) => {
  const [isConnected, setIsConnected] = useState(false);
  const [priceData, setPriceData] = useState({});
  const [error, setError] = useState(null);
  const ws = useRef(null);
  const reconnectTimer = useRef(null);

  const connect = () => {
    try {
      // Using a mock WebSocket for demo - replace with actual crypto exchange WebSocket
      ws.current = new WebSocket('wss://ws.coincap.io/prices?assets=bitcoin,ethereum,cardano');

      ws.current.onopen = () => {
        setIsConnected(true);
        setError(null);
        console.log('WebSocket connected');
      };

      ws.current.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          setPriceData(prev => ({ ...prev, ...data }));
        } catch (err) {
          console.error('Failed to parse WebSocket message:', err);
        }
      };

      ws.current.onerror = (error) => {
        setError('WebSocket connection error');
        console.error('WebSocket error:', error);
      };

      ws.current.onclose = () => {
        setIsConnected(false);
        // Attempt to reconnect after 5 seconds
        reconnectTimer.current = setTimeout(() => {
          connect();
        }, 5000);
      };
    } catch (error) {
      setError('Failed to connect to WebSocket');
      console.error('WebSocket connection failed:', error);
    }
  };

  const disconnect = () => {
    if (ws.current) {
      ws.current.close();
    }
    if (reconnectTimer.current) {
      clearTimeout(reconnectTimer.current);
    }
  };

  const sendMessage = (message) => {
    if (ws.current && ws.current.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify(message));
    }
  };

  useEffect(() => {
    connect();
    return () => disconnect();
  }, []);

  const value = {
    isConnected,
    priceData,
    error,
    sendMessage,
    connect,
    disconnect
  };

  return (
    <WebSocketContext.Provider value={value}>
      {children}
    </WebSocketContext.Provider>
  );
};