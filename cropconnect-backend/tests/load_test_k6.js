import http from 'k6/http';
import { check, sleep } from 'k6';

// k6 Load Test Configuration for CropConnect (Layer 15a of SaaS Playbook)
// Simulates concurrent users ramping up against staging/production
export const options = {
  stages: [
    { duration: '2m', target: 20 },  // Ramp-up to 20 users
    { duration: '5m', target: 50 },  // Steady state at 50 users
    { duration: '2m', target: 100 }, // Peak burst to 100 users
    { duration: '1m', target: 0 },   // Cool-down
  ],
  thresholds: {
    http_req_failed: ['rate<0.01'],     // Error rate must be under 1%
    http_req_duration: ['p(95)<300'],  // p95 latency must be under 300ms
  },
};

const BASE_URL = __ENV.TARGET_URL || 'https://cropconnect01-production.up.railway.app';

export default function () {
  // 1. Lightweight Health Check (/api/health/live)
  let liveRes = http.get(`${BASE_URL}/api/health/live`);
  check(liveRes, {
    'liveness status is 200': (r) => r.status === 200,
  });

  // 2. Deep Health & DB Status Check (/api/health)
  let healthRes = http.get(`${BASE_URL}/api/health`);
  check(healthRes, {
    'health status is 200': (r) => r.status === 200,
  });

  // 3. Mandi Market Commodities Query (/api/market/crops)
  let marketRes = http.get(`${BASE_URL}/api/market/crops`);
  check(marketRes, {
    'market crops status is 200': (r) => r.status === 200,
  });

  // 4. Weather Forecast Endpoint (/api/weather?latitude=28.61&longitude=77.20)
  let weatherRes = http.get(`${BASE_URL}/api/weather?latitude=28.61&longitude=77.20`);
  check(weatherRes, {
    'weather endpoint status is 200': (r) => r.status === 200 || r.status === 429,
  });

  // 5. ESP32 Relay Command Poll (/api/esp32/relay-command)
  let relayRes = http.get(`${BASE_URL}/api/esp32/relay-command`);
  check(relayRes, {
    'relay command endpoint responds cleanly': (r) => r.status === 200 || r.status === 401,
  });

  sleep(1);
}
