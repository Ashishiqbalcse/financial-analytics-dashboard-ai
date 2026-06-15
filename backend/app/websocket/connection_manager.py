from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List, Set
import json
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConnectionManager:
    """WebSocket connection manager for real-time data streaming"""
    
    def __init__(self):
        # Dictionary to store active connections by symbol
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # Dictionary to store which symbols each connection is subscribed to
        self.connection_subscriptions: Dict[WebSocket, Set[str]] = {}
    
    async def connect(self, websocket: WebSocket, symbol: str = None):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        
        if symbol:
            symbol = symbol.upper()
            if symbol not in self.active_connections:
                self.active_connections[symbol] = set()
            self.active_connections[symbol].add(websocket)
            
            if websocket not in self.connection_subscriptions:
                self.connection_subscriptions[websocket] = set()
            self.connection_subscriptions[websocket].add(symbol)
            
            logger.info(f"WebSocket connected for symbol: {symbol}")
        else:
            logger.info("WebSocket connected without symbol subscription")
    
    def disconnect(self, websocket: WebSocket):
        """Handle WebSocket disconnection"""
        # Remove from all symbol subscriptions
        if websocket in self.connection_subscriptions:
            for symbol in self.connection_subscriptions[websocket]:
                if symbol in self.active_connections:
                    self.active_connections[symbol].discard(websocket)
                    if not self.active_connections[symbol]:
                        del self.active_connections[symbol]
            del self.connection_subscriptions[websocket]
        
        logger.info("WebSocket disconnected")
    
    async def broadcast_price(self, symbol: str, price_data: dict):
        """Broadcast price update to all subscribers of a symbol"""
        if symbol.upper() in self.active_connections:
            message = {
                "type": "price_update",
                "symbol": symbol.upper(),
                "data": price_data,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Create a copy of the set to avoid modification during iteration
            connections = self.active_connections[symbol.upper()].copy()
            
            for connection in connections:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Error sending price update to client: {e}")
                    self.disconnect(connection)
    
    async def broadcast_indicator(self, symbol: str, indicator_data: dict):
        """Broadcast indicator update to all subscribers of a symbol"""
        if symbol.upper() in self.active_connections:
            message = {
                "type": "indicator_update",
                "symbol": symbol.upper(),
                "data": indicator_data,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            connections = self.active_connections[symbol.upper()].copy()
            
            for connection in connections:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Error sending indicator update to client: {e}")
                    self.disconnect(connection)
    
    async def broadcast_alert(self, user_id: str, alert_data: dict):
        """Broadcast alert to specific user (if connected)"""
        # This would require user authentication and connection mapping
        # For now, we'll broadcast to all connections (simplified)
        message = {
            "type": "alert",
            "user_id": user_id,
            "data": alert_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        for symbol_connections in self.active_connections.values():
            connections = symbol_connections.copy()
            for connection in connections:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Error sending alert to client: {e}")
                    self.disconnect(connection)
    
    async def subscribe_symbol(self, websocket: WebSocket, symbol: str):
        """Subscribe a connection to a specific symbol"""
        symbol = symbol.upper()
        
        # Add to symbol connections
        if symbol not in self.active_connections:
            self.active_connections[symbol] = set()
        self.active_connections[symbol].add(websocket)
        
        # Add to connection subscriptions
        if websocket not in self.connection_subscriptions:
            self.connection_subscriptions[websocket] = set()
        self.connection_subscriptions[websocket].add(symbol)
        
        logger.info(f"WebSocket subscribed to symbol: {symbol}")
        
        # Send confirmation
        await websocket.send_json({
            "type": "subscription_confirmed",
            "symbol": symbol,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def unsubscribe_symbol(self, websocket: WebSocket, symbol: str):
        """Unsubscribe a connection from a specific symbol"""
        symbol = symbol.upper()
        
        # Remove from symbol connections
        if symbol in self.active_connections:
            self.active_connections[symbol].discard(websocket)
            if not self.active_connections[symbol]:
                del self.active_connections[symbol]
        
        # Remove from connection subscriptions
        if websocket in self.connection_subscriptions:
            self.connection_subscriptions[websocket].discard(symbol)
        
        logger.info(f"WebSocket unsubscribed from symbol: {symbol}")
        
        # Send confirmation
        await websocket.send_json({
            "type": "unsubscription_confirmed",
            "symbol": symbol,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def get_connection_count(self) -> int:
        """Get total number of active connections"""
        return len(self.connection_subscriptions)
    
    def get_symbol_subscribers(self, symbol: str) -> int:
        """Get number of subscribers for a specific symbol"""
        return len(self.active_connections.get(symbol.upper(), set()))
    
    def get_active_symbols(self) -> List[str]:
        """Get list of symbols with active subscribers"""
        return list(self.active_connections.keys())


# Global connection manager instance
manager = ConnectionManager()
