"""
Flask Web Application - Real-time XAUUSD Market Analysis Dashboard
"""

from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import threading
import time
from datetime import datetime
import pytz
import config
from market_analysis import MarketAnalysisEngine

app = Flask(__name__)
app.config['SECRET_KEY'] = 'xauusd-market-analysis-secret-key'
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Global analysis engine
analysis_engine = MarketAnalysisEngine()
current_snapshot = None
update_thread = None
running = False


def background_update_task():
    """Background task to update market data"""
    global current_snapshot, running
    
    while running:
        try:
            print(f"[{datetime.now(pytz.UTC).strftime('%H:%M:%S')}] Fetching market data...")
            snapshot = analysis_engine.generate_market_snapshot()
            current_snapshot = snapshot
            
            # Emit to all connected clients
            socketio.emit('market_update', snapshot, namespace='/')
            
            print(f"[{datetime.now(pytz.UTC).strftime('%H:%M:%S')}] Market data updated and broadcasted")
            
        except Exception as e:
            print(f"Error in background update: {e}")
            import traceback
            traceback.print_exc()
        
        # Wait for next update
        time.sleep(config.UPDATE_INTERVAL)


@app.route('/')
def index():
    """Serve main dashboard"""
    return render_template('index.html')


@app.route('/api/fred/history/<series_id>')
def get_fred_history(series_id):
    """API endpoint to get historical data for a FRED series"""
    try:
        # Default to 30 data points (about 6 weeks of daily data)
        limit = 30
        history = analysis_engine.data_aggregator.fred.get_series_history(series_id, limit)
        return jsonify(history)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/snapshot')
def get_snapshot():
    """API endpoint to get current market snapshot"""
    if current_snapshot:
        return jsonify(current_snapshot)
    else:
        return jsonify({"error": "No data available yet"}), 503


@app.route('/api/config')
def get_config():
    """API endpoint to get system configuration"""
    return jsonify({
        "update_interval": config.UPDATE_INTERVAL,
        "symbol": config.SYMBOL,
        "timeframes": config.TIMEFRAMES
    })


@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print(f"Client connected: {datetime.now(pytz.UTC).strftime('%H:%M:%S')}")
    
    # Send current snapshot immediately
    if current_snapshot:
        emit('market_update', current_snapshot)
    else:
        emit('status', {'message': 'Waiting for first data update...'})


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print(f"Client disconnected: {datetime.now(pytz.UTC).strftime('%H:%M:%S')}")


@socketio.on('request_update')
def handle_manual_update():
    """Handle manual update request from client"""
    try:
        snapshot = analysis_engine.generate_market_snapshot()
        emit('market_update', snapshot)
    except Exception as e:
        emit('error', {'message': str(e)})


def start_background_updates():
    """Start background update thread"""
    global update_thread, running
    
    if update_thread is None or not update_thread.is_alive():
        running = True
        update_thread = threading.Thread(target=background_update_task, daemon=True)
        update_thread.start()
        print("Background update thread started")


if __name__ == '__main__':
    print("=" * 80)
    print("XAUUSD Real-Time Market Analysis System")
    print("=" * 80)
    print(f"Starting server at http://localhost:5000")
    print(f"Update interval: {config.UPDATE_INTERVAL} seconds ({config.UPDATE_INTERVAL/60:.1f} minutes)")
    print("=" * 80)
    
    # Start background updates
    start_background_updates()
    
    # Run Flask app with SocketIO
    socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)
