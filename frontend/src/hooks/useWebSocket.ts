import { useEffect, useRef, useState } from 'react';

interface WebSocketMessage {
  type: string;
  symbol?: string;
  data?: any;
  timestamp?: string;
}

interface UseWebSocketOptions {
  onMessage?: (message: WebSocketMessage) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
  onError?: (error: Event) => void;
}

export const useWebSocket = (url: string, options: UseWebSocketOptions = {}) => {
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectAttempts = useRef(0);
  const maxReconnectAttempts = 5;

  const { onMessage, onConnect, onDisconnect, onError } = options;

  const connect = () => {
    try {
      const wsUrl = url.startsWith('ws') ? url : `ws://${url}`;
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
  console.log("WS OPEN");

  setIsConnected(true);

  reconnectAttempts.current = 0;

  onConnect?.();
};

      ws.onmessage = (event) => {
        const message: WebSocketMessage = JSON.parse(event.data);
        setLastMessage(message);
        onMessage?.(message);
      };

      ws.onclose = () => {
        console.log("WS CLOSED");
        setIsConnected(false);
        onDisconnect?.();
        
        // Attempt to reconnect
        if (reconnectAttempts.current < maxReconnectAttempts) {
          reconnectAttempts.current++;
          setTimeout(connect, 3000 * reconnectAttempts.current);
        }
      };

      ws.onerror = (error) => {
        console.log("WS ERROR", error);
        onError?.(error);
      };
    } catch (error) {
      console.error('WebSocket connection error:', error);
      onError?.(error as Event);
    }
  };

  const disconnect = () => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
  };

  const sendMessage = (message: any) => {
  if (
    wsRef.current &&
    wsRef.current.readyState === WebSocket.OPEN
  ) {
    wsRef.current.send(
      JSON.stringify(message)
    );
  } else {
    console.warn(
      "WebSocket not ready. Message skipped:",
      message
    );
  }
};

  const subscribe = (symbol: string) => {
    sendMessage({
      action: 'subscribe',
      symbol: symbol
    });
  };

  const unsubscribe = (symbol: string) => {
    sendMessage({
      action: 'unsubscribe',
      symbol: symbol
    });
  };

  const ping = () => {
    sendMessage({ action: 'ping' });
  };

  useEffect(() => {
    connect();
    return () => {
      disconnect();
    };
  }, [url]);

  return {
    isConnected,
    lastMessage,
    sendMessage,
    subscribe,
    unsubscribe,
    ping,
    connect,
    disconnect
  };
};
