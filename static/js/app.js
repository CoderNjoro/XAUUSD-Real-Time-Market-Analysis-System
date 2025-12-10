/**
 * XAUUSD Market Analysis Dashboard - Frontend Application
 * Real-time WebSocket communication and UI updates
 */

// Initialize Socket.IO connection
const socket = io();

// State management
let currentSnapshot = null;
let isConnected = false;

// DOM Elements
const elements = {
    // Connection status
    connectionStatus: document.getElementById('connectionStatus'),
    lastUpdate: document.querySelector('.update-time'),

    // Price overview
    currentPrice: document.getElementById('currentPrice'),
    priceChange: document.getElementById('priceChange'),
    sessionBadge: document.getElementById('sessionBadge'),
    nextOverlap: document.getElementById('nextOverlap'),

    // Market drivers
    primaryDriver: document.getElementById('primaryDriver'),
    momentum: document.getElementById('momentum'),

    // Correlations
    yieldValue: document.getElementById('yieldValue'),
    yieldChange: document.getElementById('yieldChange'),
    yieldPressure: document.getElementById('yieldPressure'),

    dxyValue: document.getElementById('dxyValue'),
    dxyChange: document.getElementById('dxyChange'),
    dxyPressure: document.getElementById('dxyPressure'),

    riskChange: document.getElementById('riskChange'),
    havenDemand: document.getElementById('havenDemand'),

    btcValue: document.getElementById('btcValue'),
    btcChange: document.getElementById('btcChange'),

    // New FRED indicators
    vixValue: document.getElementById('vixValue'),
    vixChange: document.getElementById('vixChange'),
    vixFearLevel: document.getElementById('vixFearLevel'),

    yield2yValue: document.getElementById('yield2yValue'),
    yield2yChange: document.getElementById('yield2yChange'),

    yield30yValue: document.getElementById('yield30yValue'),
    yield30yChange: document.getElementById('yield30yChange'),

    yieldCurveSpread: document.getElementById('yieldCurveSpread'),
    yieldCurveStatus: document.getElementById('yieldCurveStatus'),

    // Technical analysis
    nearestSupport: document.getElementById('nearestSupport'),
    nearestResistance: document.getElementById('nearestResistance'),
    maAlignment: document.getElementById('maAlignment'),
    rsiValue: document.getElementById('rsiValue'),

    // News & alerts
    catalystContainer: document.getElementById('catalystContainer'),
    alertsContainer: document.getElementById('alertsContainer'),

    // Manual update button
    manualUpdate: document.getElementById('manualUpdate')
};

// ===== Socket.IO Event Handlers =====

socket.on('connect', () => {
    console.log('Connected to server');
    isConnected = true;
    updateConnectionStatus(true);
});

socket.on('disconnect', () => {
    console.log('Disconnected from server');
    isConnected = false;
    updateConnectionStatus(false);
});

socket.on('market_update', (snapshot) => {
    console.log('Received market update:', snapshot);
    currentSnapshot = snapshot;
    updateDashboard(snapshot);
});

socket.on('error', (error) => {
    console.error('Socket error:', error);
    showNotification('Error: ' + error.message, 'error');
});

socket.on('status', (status) => {
    console.log('Status:', status);
    showNotification(status.message, 'info');
});

// ===== Manual Update Handler =====

elements.manualUpdate.addEventListener('click', () => {
    console.log('Manual update requested');
    elements.manualUpdate.disabled = true;
    elements.manualUpdate.textContent = 'Updating...';

    socket.emit('request_update');

    setTimeout(() => {
        elements.manualUpdate.disabled = false;
        elements.manualUpdate.textContent = 'Update Now';
    }, 3000);
});

// ===== UI Update Functions =====

function updateConnectionStatus(connected) {
    const indicator = elements.connectionStatus.querySelector('.status-indicator');
    const text = elements.connectionStatus.querySelector('span');

    if (connected) {
        indicator.classList.add('connected');
        indicator.classList.remove('disconnected');
        text.textContent = 'Connected';
    } else {
        indicator.classList.remove('connected');
        indicator.classList.add('disconnected');
        text.textContent = 'Disconnected';
    }
}

function updateDashboard(snapshot) {
    try {
        // Update timestamp
        const timestamp = new Date(snapshot.timestamp);
        elements.lastUpdate.textContent = timestamp.toLocaleTimeString('en-US', { hour12: false });

        // Update price overview
        updatePriceOverview(snapshot);

        // Update market drivers
        updateMarketDrivers(snapshot);

        // Update correlations
        updateCorrelations(snapshot);

        // Update technical analysis
        updateTechnicalAnalysis(snapshot);

        // Update news/catalyst
        updateCatalyst(snapshot);

        // Update alerts
        updateAlerts(snapshot);

    } catch (error) {
        console.error('Error updating dashboard:', error);
    }
}

function updatePriceOverview(snapshot) {
    const { xauusd, session, next_session_overlap } = snapshot;

    // Price
    const price = xauusd.price || 0;
    elements.currentPrice.textContent = `$${price.toFixed(2)}`;

    // Price change
    const change = xauusd.change_1h || 0;
    const changeElement = elements.priceChange.querySelector('.change-value');
    changeElement.textContent = `${change >= 0 ? '+' : ''}${change.toFixed(2)}%`;
    changeElement.className = 'change-value ' + (change >= 0 ? 'positive' : 'negative');

    // Session
    const sessionIcons = {
        'ASIAN': '🌏',
        'LONDON': '🇬🇧',
        'NY': '🇺🇸',
        'LONDON/NY': '🌍'
    };

    const sessionIcon = elements.sessionBadge.querySelector('.session-icon');
    const sessionName = elements.sessionBadge.querySelector('.session-name');

    sessionIcon.textContent = sessionIcons[session] || '🌍';
    sessionName.textContent = session;

    // Next overlap
    if (next_session_overlap) {
        const minutes = next_session_overlap.minutes_until;
        if (next_session_overlap.active) {
            elements.nextOverlap.innerHTML = '<strong>Session overlap active</strong>';
        } else {
            elements.nextOverlap.innerHTML = `Next overlap in <strong>${minutes}</strong> min`;
        }
    }
}

function updateMarketDrivers(snapshot) {
    const { primary_driver, momentum } = snapshot;

    elements.primaryDriver.textContent = primary_driver;
    elements.momentum.textContent = momentum.description;

    // Color coding
    const driverColors = {
        'Technical': '#3b82f6',
        'Fundamental': '#f59e0b',
        'Sentiment': '#8b5cf6',
        'Liquidity': '#10b981'
    };

    elements.primaryDriver.style.borderLeftColor = driverColors[primary_driver] || '#FFD700';
}

function updateCorrelations(snapshot) {
    const { correlations } = snapshot;

    // Yield Watch
    if (correlations.yield) {
        const y = correlations.yield;
        elements.yieldValue.textContent = `${y.price.toFixed(3)}%`;

        const arrow = y.direction;
        const bps = Math.abs(y.change_bps).toFixed(1);
        elements.yieldChange.innerHTML = `
            <span class="arrow ${arrow === '▲' ? 'up' : arrow === '▼' ? 'down' : ''}">${arrow}</span>
            <span class="bps">${bps} bps</span>
        `;

        elements.yieldPressure.textContent = y.pressure;
        elements.yieldPressure.style.color = y.pressure === 'Up' ? '#10b981' : y.pressure === 'Down' ? '#ef4444' : '#9ca3af';
    }

    // DXY Watch
    if (correlations.dxy) {
        const d = correlations.dxy;
        elements.dxyValue.textContent = d.price.toFixed(2);

        const arrow = d.direction;
        const pct = Math.abs(d.percent_change).toFixed(2);
        elements.dxyChange.innerHTML = `
            <span class="arrow ${arrow === '▲' ? 'up' : arrow === '▼' ? 'down' : ''}">${arrow}</span>
            <span class="percent">${pct}%</span>
        `;

        elements.dxyPressure.textContent = d.pressure;
    }

    // Risk Gauge
    if (correlations.risk) {
        const r = correlations.risk;
        const arrow = r.direction;
        const pct = Math.abs(r.percent_change).toFixed(2);

        elements.riskChange.innerHTML = `
            <span class="arrow ${arrow === '▲' ? 'up' : arrow === '▼' ? 'down' : ''}">${arrow}</span>
            <span class="percent">${pct}%</span>
        `;

        elements.havenDemand.textContent = r.haven_demand;
        elements.havenDemand.style.color = r.haven_demand === 'High' ? '#ef4444' : r.haven_demand === 'Low' ? '#10b981' : '#9ca3af';
    }

    // Bitcoin
    if (correlations.btc) {
        const b = correlations.btc;
        elements.btcValue.textContent = `$${b.price.toLocaleString('en-US', { maximumFractionDigits: 0 })}`;

        const arrow = b.direction;
        const pct = Math.abs(b.percent_change).toFixed(2);
        elements.btcChange.innerHTML = `
            <span class="arrow ${arrow === '▲' ? 'up' : arrow === '▼' ? 'down' : ''}">${arrow}</span>
            <span class="percent">${pct}%</span>
        `;
    }

    // VIX (Fear Gauge)
    if (correlations.vix) {
        const v = correlations.vix;
        elements.vixValue.textContent = v.price.toFixed(2);

        const arrow = v.direction;
        const pct = Math.abs(v.percent_change).toFixed(2);
        elements.vixChange.innerHTML = `
            <span class="arrow ${arrow === '▲' ? 'up' : arrow === '▼' ? 'down' : ''}">${arrow}</span>
            <span class="percent">${pct}%</span>
        `;

        elements.vixFearLevel.textContent = v.fear_level;
        // Color code fear level
        const fearColors = {
            'Extreme Fear': '#ef4444',
            'High Fear': '#f97316',
            'Moderate': '#9ca3af',
            'Low Fear': '#10b981'
        };
        elements.vixFearLevel.style.color = fearColors[v.fear_level] || '#9ca3af';
    }

    // 2-Year Treasury
    if (correlations.yield_2y) {
        const y2 = correlations.yield_2y;
        elements.yield2yValue.textContent = `${y2.price.toFixed(3)}%`;

        const arrow = y2.direction;
        const bps = Math.abs(y2.change_bps).toFixed(1);
        elements.yield2yChange.innerHTML = `
            <span class="arrow ${arrow === '▲' ? 'up' : arrow === '▼' ? 'down' : ''}">${arrow}</span>
            <span class="bps">${bps} bps</span>
        `;
    }

    // 30-Year Treasury
    if (correlations.yield_30y) {
        const y30 = correlations.yield_30y;
        elements.yield30yValue.textContent = `${y30.price.toFixed(3)}%`;

        const arrow = y30.direction;
        const bps = Math.abs(y30.change_bps).toFixed(1);
        elements.yield30yChange.innerHTML = `
            <span class="arrow ${arrow === '▲' ? 'up' : arrow === '▼' ? 'down' : ''}">${arrow}</span>
            <span class="bps">${bps} bps</span>
        `;
    }

    // Yield Curve
    if (correlations.yield_curve) {
        const yc = correlations.yield_curve;
        const spread = yc.spread * 100; // Convert to basis points
        elements.yieldCurveSpread.textContent = `${spread >= 0 ? '+' : ''}${spread.toFixed(1)} bps`;

        elements.yieldCurveStatus.textContent = yc.status;
        // Color code yield curve status
        const statusColors = {
            'Normal': '#10b981',
            'Flat': '#f59e0b',
            'Inverted': '#ef4444'
        };
        elements.yieldCurveStatus.style.color = statusColors[yc.status] || '#9ca3af';
    }
}

function updateTechnicalAnalysis(snapshot) {
    const { technical } = snapshot;

    // Support & Resistance
    const nearest = technical.nearest_levels || {};

    if (nearest.support) {
        const [price, pips] = nearest.support;
        elements.nearestSupport.innerHTML = `
            <span class="price">$${price.toFixed(2)}</span>
            <span class="pips">(${pips.toFixed(1)} pips below)</span>
        `;
    } else {
        elements.nearestSupport.innerHTML = '<span class="price">N/A</span>';
    }

    if (nearest.resistance) {
        const [price, pips] = nearest.resistance;
        elements.nearestResistance.innerHTML = `
            <span class="price">$${price.toFixed(2)}</span>
            <span class="pips">(${pips.toFixed(1)} pips above)</span>
        `;
    } else {
        elements.nearestResistance.innerHTML = '<span class="price">N/A</span>';
    }

    // MA Alignment
    const maAlignment = technical.ma_alignment || 'Neutral';
    elements.maAlignment.textContent = maAlignment;
    elements.maAlignment.style.color =
        maAlignment === 'Bullish' ? '#10b981' :
            maAlignment === 'Bearish' ? '#ef4444' :
                '#9ca3af';

    // RSI
    const rsi = technical.rsi;
    const rsiStatus = technical.rsi_status || 'N/A';

    if (rsi !== null && rsi !== undefined) {
        elements.rsiValue.innerHTML = `
            <span class="rsi-number">${rsi.toFixed(1)}</span>
            <span class="rsi-status">[${rsiStatus}]</span>
        `;

        // Color code RSI
        const rsiNumber = elements.rsiValue.querySelector('.rsi-number');
        if (rsiStatus === 'Overbought') {
            rsiNumber.style.color = '#ef4444';
        } else if (rsiStatus === 'Oversold') {
            rsiNumber.style.color = '#10b981';
        } else {
            rsiNumber.style.color = '#FFD700';
        }
    } else {
        elements.rsiValue.innerHTML = '<span class="rsi-number">--</span><span class="rsi-status">[N/A]</span>';
    }
}

function updateCatalyst(snapshot) {
    const { next_catalyst } = snapshot;

    if (next_catalyst) {
        elements.catalystContainer.innerHTML = `
            <div class="catalyst-item">
                <div class="catalyst-time">${next_catalyst.minutes_until} min</div>
                <div class="catalyst-details">
                    <h4>${next_catalyst.event}</h4>
                    <p>${next_catalyst.time}</p>
                </div>
                <div class="catalyst-badge">${next_catalyst.impact}</div>
            </div>
        `;
    } else {
        elements.catalystContainer.innerHTML = `
            <div class="catalyst-empty">
                <span>No upcoming high-impact events</span>
            </div>
        `;
    }
}

function updateAlerts(snapshot) {
    const { alerts } = snapshot;

    if (!alerts || alerts.length === 0 || (alerts.length === 1 && alerts[0] === 'None')) {
        elements.alertsContainer.innerHTML = `
            <div class="alert-item alert-none">
                <span class="alert-icon">✓</span>
                <span class="alert-text">None</span>
            </div>
        `;
        return;
    }

    elements.alertsContainer.innerHTML = alerts.map(alert => {
        let alertClass = 'alert-warning';
        let icon = '⚠️';

        if (alert.includes('Approaching') || alert.includes('High-Impact News')) {
            alertClass = 'alert-danger';
            icon = '🚨';
        }

        return `
            <div class="alert-item ${alertClass}">
                <span class="alert-icon">${icon}</span>
                <span class="alert-text">${alert}</span>
            </div>
        `;
    }).join('');
}

function showNotification(message, type = 'info') {
    // Simple console notification for now
    // Could be enhanced with toast notifications
    console.log(`[${type.toUpperCase()}] ${message}`);
}

// ===== Utility Functions =====

function formatNumber(num, decimals = 2) {
    return num.toFixed(decimals);
}

function formatCurrency(num) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }).format(num);
}

// ===== Chart Management =====

const charts = {
    yield30y: null,
    yieldCurve: null
};

async function initCharts() {
    try {
        console.log('Initializing charts...');

        // Initialize 30Y Treasury Chart
        const ctx30y = document.getElementById('yield30yChart').getContext('2d');
        charts.yield30y = createSparklineChart(ctx30y, '30Y Yield', '#3b82f6');

        // Initialize Yield Curve Chart
        const ctxCurve = document.getElementById('yieldCurveChart').getContext('2d');
        charts.yieldCurve = createSparklineChart(ctxCurve, '10Y-2Y Spread', '#f59e0b');

        // Fetch initial data
        await updateCharts();

        // Update charts periodically (every hour)
        setInterval(updateCharts, 3600000);

    } catch (error) {
        console.error('Error initializing charts:', error);
    }
}

function createSparklineChart(ctx, label, color) {
    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: label,
                data: [],
                borderColor: color,
                borderWidth: 2,
                pointRadius: 0,
                pointHoverRadius: 4,
                fill: true,
                backgroundColor: (context) => {
                    const ctx = context.chart.ctx;
                    const gradient = ctx.createLinearGradient(0, 0, 0, 60);
                    gradient.addColorStop(0, color + '33'); // 20% opacity
                    gradient.addColorStop(1, color + '00'); // 0% opacity
                    return gradient;
                },
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    callbacks: {
                        label: function (context) {
                            return context.parsed.y.toFixed(2) + (label.includes('Spread') ? ' bps' : '%');
                        }
                    }
                }
            },
            scales: {
                x: { display: false },
                y: {
                    display: false,
                    grace: '10%'
                }
            },
            interaction: {
                mode: 'nearest',
                axis: 'x',
                intersect: false
            }
        }
    });
}

async function updateCharts() {
    try {
        // Fetch 30Y Data
        const res30y = await fetch('/api/fred/history/DGS30');
        const data30y = await res30y.json();

        if (data30y && Array.isArray(data30y)) {
            const labels = data30y.map(d => formatDate(d.date));
            const values = data30y.map(d => d.value);

            updateChartData(charts.yield30y, labels, values);
        }

        // Fetch 10Y and 2Y for Yield Curve
        const [res10y, res2y] = await Promise.all([
            fetch('/api/fred/history/DGS10'),
            fetch('/api/fred/history/DGS2')
        ]);

        const data10y = await res10y.json();
        const data2y = await res2y.json();

        if (Array.isArray(data10y) && Array.isArray(data2y)) {
            // Match dates to calculate spread
            const spreadData = calculateSpreadValues(data10y, data2y);

            updateChartData(charts.yieldCurve, spreadData.labels, spreadData.values);

            // Color code yield curve chart based on latest value
            const latestSpread = spreadData.values[spreadData.values.length - 1];
            const color = latestSpread < 0 ? '#ef4444' : '#10b981'; // Red if inverted, Green if normal
            charts.yieldCurve.data.datasets[0].borderColor = color;
            charts.yieldCurve.data.datasets[0].backgroundColor = (context) => {
                const ctx = context.chart.ctx;
                const gradient = ctx.createLinearGradient(0, 0, 0, 60);
                gradient.addColorStop(0, color + '33');
                gradient.addColorStop(1, color + '00');
                return gradient;
            };
            charts.yieldCurve.update();
        }

    } catch (error) {
        console.error('Error updating charts:', error);
    }
}

function updateChartData(chart, labels, data) {
    if (!chart) return;

    chart.data.labels = labels;
    chart.data.datasets[0].data = data;
    chart.update();
}

function calculateSpreadValues(data10y, data2y) {
    // specific logic to match dates
    const map2y = new Map(data2y.map(d => [d.date, d.value]));
    const labels = [];
    const values = [];

    // Iterate 10y and find matching 2y
    data10y.forEach(d10 => {
        if (map2y.has(d10.date)) {
            labels.push(formatDate(d10.date));
            const val10 = d10.value;
            const val2 = map2y.get(d10.date);
            // Spread in bps
            values.push((val10 - val2) * 100);
        }
    });

    return { labels, values };
}

function formatDate(dateStr) {
    const d = new Date(dateStr);
    return `${d.getMonth() + 1}/${d.getDate()}`;
}


// ===== Initialize =====

console.log('XAUUSD Market Analysis Dashboard initialized');
console.log('Waiting for market data...');

// Initialize charts after DOM load
document.addEventListener('DOMContentLoaded', () => {
    initCharts();
});
