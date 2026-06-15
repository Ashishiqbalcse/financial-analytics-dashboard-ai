from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from app.websocket.connection_manager import manager
from app.services.market_data import market_data_service
from datetime import datetime
import logging
import asyncio
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/ws/{symbol}")
async def websocket_symbol_endpoint(websocket: WebSocket, symbol: str):
    """WebSocket endpoint for real-time data for a specific symbol"""
    await manager.connect(websocket, symbol)
    
    try:
        # Send initial data
        price_data = await market_data_service.get_realtime_price(symbol)
        if price_data:
            await manager.broadcast_price(symbol, price_data)
        
        # Send periodic updates
        while True:
            try:
                # Wait for client messages or send periodic updates
                data = await asyncio.wait_for(websocket.receive_text(), timeout=5.0)
                
                # Handle client messages
                message = json.loads(data)
                
                if message.get("action") == "subscribe":
                    new_symbol = message.get("symbol", symbol)
                    await manager.subscribe_symbol(websocket, new_symbol)
                elif message.get("action") == "unsubscribe":
                    unsub_symbol = message.get("symbol")
                    await manager.unsubscribe_symbol(websocket, unsub_symbol)
                elif message.get("action") == "ping":
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat()
                    })
                elif message.get("action") == "get_price":
                    requested_symbol = message.get("symbol", symbol)
                    price = await market_data_service.get_realtime_price(requested_symbol)
                    if price:
                        await websocket.send_json({
                            "type": "price_update",
                            "symbol": requested_symbol,
                            "data": price,
                            "timestamp": datetime.utcnow().isoformat()
                        })
                
            except asyncio.TimeoutError:
                # Send periodic price update
                price_data = await market_data_service.get_realtime_price(symbol)
                if price_data:
                    await manager.broadcast_price(symbol, price_data)
                
                # Send heartbeat
                await websocket.send_json({
                    "type": "heartbeat",
                    "timestamp": datetime.utcnow().isoformat()
                })
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info(f"Client disconnected from {symbol} websocket")
    except Exception as e:
        logger.error(f"Error in websocket for {symbol}: {e}")
        manager.disconnect(websocket)


@router.websocket("/ws/live")
async def websocket_live_endpoint(websocket: WebSocket):
    """WebSocket endpoint for live market data streaming"""
    await manager.connect(websocket)
    
    try:
        # Send connection confirmation
        await websocket.send_json({
            "type": "connected",
            "message": "Connected to live data stream",
            "timestamp": datetime.utcnow().isoformat(),
            "available_symbols": manager.get_active_symbols()
        })
        
        while True:
            try:
                # Wait for client messages
                data = await asyncio.wait_for(websocket.receive_text(), timeout=10.0)
                message = json.loads(data)
                
                if message.get("action") == "subscribe":
                    symbol = message.get("symbol")
                    if symbol:
                        await manager.subscribe_symbol(websocket, symbol)
                        
                        # Send current price for the symbol
                        price_data = await market_data_service.get_realtime_price(symbol)
                        if price_data:
                            await manager.broadcast_price(symbol, price_data)
                
                elif message.get("action") == "unsubscribe":
                    symbol = message.get("symbol")
                    if symbol:
                        await manager.unsubscribe_symbol(websocket, symbol)
                
                elif message.get("action") == "ping":
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat()
                    })
                
                elif message.get("action") == "get_symbols":
                    await websocket.send_json({
                        "type": "symbols_list",
                        "symbols": manager.get_active_symbols(),
                        "timestamp": datetime.utcnow().isoformat()
                    })
                
                elif message.get("action") == "get_status":
                    await websocket.send_json({
                        "type": "status",
                        "connection_count": manager.get_connection_count(),
                        "active_symbols": manager.get_active_symbols(),
                        "subscriptions": list(manager.connection_subscriptions.get(websocket, set())),
                        "timestamp": datetime.utcnow().isoformat()
                    })
                
            except asyncio.TimeoutError:
                # Send heartbeat
                await websocket.send_json({
                    "type": "heartbeat",
                    "timestamp": datetime.utcnow().isoformat()
                })
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("Client disconnected from live websocket")
    except Exception as e:
        logger.error(f"Error in live websocket: {e}")
        manager.disconnect(websocket)


@router.get("/ws/status")
async def websocket_status():
    """Get WebSocket connection status"""
    return {
        "status": "active",
        "connection_count": manager.get_connection_count(),
        "active_symbols": manager.get_active_symbols(),
        "symbol_subscribers": {
            symbol: manager.get_symbol_subscribers(symbol)
            for symbol in manager.get_active_symbols()
        }
    }
