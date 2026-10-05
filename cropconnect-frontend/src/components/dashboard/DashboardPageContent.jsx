// Renders the active dashboard page content and local page widgets.
import {
  AlertTriangle,
  CloudSun,
  Droplets,
  LayoutDashboard,
  Radio,
  Sprout,
  TrendingDown,
  TrendingUp,
  Wifi,
  Zap,
} from "lucide-react";
import { useDashboard } from "../../contexts/DashboardContext";
import CropPlanner from "../../pages/CropPlanner";
import { Button } from "../ui/button";
import AiSection from "./AiSection";
import MarketSection from "./MarketSection";
import ProfileSection from "./ProfileSection";
import PumpSection from "./PumpSection";
import SensorSection from "./SensorSection";
import SettingsSection from "./SettingsSection";
import WeatherSection from "./WeatherSection";

export default function DashboardPageContent() {
  const ctx = useDashboard();
  const {
    EMPTY_DISPLAY,
    activePage,
    activeSensorAlerts,
    apiLogs,
    chatContainerRef,
    chatInput,
    chatMessages,
    closeTimerModal,
    colors,
    copyToClipboard,
    cropZones,
    ct,
    displayValue,
    editData,
    formatTime,
    formatTimerStartTime,
    getUserMarketLocation,
    handleAddTimer,
    handleSendMessage,
    handleSuggestionClick,
    isDark,
    isEditingProfile,
    isListening,
    isPresent,
    isTyping,
    language,
    loadMarketInsight,
    loadMarketPrices,
    loadSensorApiKey,
    logContainerRef,
    marketData,
    marketError,
    marketInsight,
    marketInsightError,
    marketInsightLoading,
    marketLoading,
    newTimer,
    numericOrNull,
    openTimerModal,
    percentValue,
    protectedFetch,
    pumps,
    pumpControlMode,
    pumpDirectHost,
    pumpUpdating,
    removeTimer,
    saveSensorSetup,
    saveUserToMysql,
    scheduledTimers,
    sensorApiKey,
    sensorApiKeyError,
    sensorApiKeyLoading,
    sensorConnection,
    sensorData,
    sensorHistory,
    sensorDeviceId,
    sensorIngestUrl,
    sensorSetupForm,
    setChatInput,
    setEditData,
    setIsEditingProfile,
    setActivePage,
    setLanguage,
    setNewTimer,
    setPumpControlMode,
    setPumpDirectHost,
    setSensorSetupForm,
    setTheme,
    setUserData,
    setupCheckResult,
    setupChecking,
    showSuggestions,
    showTimerModal,
    startListening,
    stopListening,
    suggestionChips,
    t,
    telemetryPacket,
    testSensorConnection,
    theme,
    togglePump,
    userData,
    weatherData,
    weatherError,
  } = ctx;

  // Line chart component
  const LineChart = ({ data, color, height = 120 }) => {
    if (!Array.isArray(data) || data.length < 2) {
      return (
        <div className="flex items-center justify-center text-sm" style={{ height, color: colors.textLight }}>
          {EMPTY_DISPLAY}
        </div>
      );
    }
    const values = data
      .map((item) => typeof item === "number" ? item : item?.value)
      .filter((value) => Number.isFinite(value));
    if (values.length < 2) {
      return (
        <div className="flex items-center justify-center text-sm" style={{ height, color: colors.textLight }}>
          {EMPTY_DISPLAY}
        </div>
      );
    }
    const max = Math.max(...values);
    const min = Math.min(...values);
    const range = max - min || 1;
    const points = values.map((value, i) => ({
      x: (i / (values.length - 1)) * 100,
      y: 100 - ((value - min) / range) * 80 - 10,
    }));
    const pathD = points.map((p, i) => `${i === 0 ? "M" : "L"} ${p.x} ${p.y}`).join(" ");
    const areaD = `${pathD} L 100 100 L 0 100 Z`;

    return (
      <svg viewBox="0 0 100 100" className="w-full" style={{ height }} preserveAspectRatio="none">
        <defs>
          <linearGradient id={`gradient-${color}`} x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={color} stopOpacity="0.3" />
            <stop offset="100%" stopColor={color} stopOpacity="0.05" />
          </linearGradient>
        </defs>
        <path d={areaD} fill={`url(#gradient-${color})`} />
        <path d={pathD} fill="none" stroke={color} strokeWidth="2" vectorEffect="non-scaling-stroke" />
      </svg>
    );
  };

  // Semicircle gauge component
  const SemicircleGauge = ({ value, max = 100, size = 140 }) => {
    const radius = size / 2 - 8;
    const circumference = Math.PI * radius;
    const numericValue = numericOrNull(value);
    const offset = circumference - ((numericValue || 0) / max) * circumference;

    return (
      <div className="relative inline-block" style={{ width: size, height: size / 2 }}>
        <svg width={size} height={size / 2} viewBox={`0 0 ${size} ${size / 2}`}>
          <defs>
            <linearGradient id="gaugeGradient" x1="0" y1="0" x2="1" y2="0">
              <stop offset="0%" stopColor={colors.red} />
              <stop offset="50%" stopColor={colors.gold} />
              <stop offset="100%" stopColor={colors.greenLight} />
            </linearGradient>
          </defs>
          <path
            d={`M 8 ${size / 2} A ${radius} ${radius} 0 0 1 ${size - 8} ${size / 2}`}
            fill="none"
            stroke={colors.creamDark}
            strokeWidth="8"
          />
          <path
            d={`M 8 ${size / 2} A ${radius} ${radius} 0 0 1 ${size - 8} ${size / 2}`}
            fill="none"
            stroke="url(#gaugeGradient)"
            strokeWidth="8"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            strokeLinecap="round"
          />
        </svg>
        <div className="absolute bottom-1 left-1/2 -translate-x-1/2 text-center">
          <span className="text-2xl font-mono font-bold" style={{ color: colors.textDark }}>{displayValue(numericValue)}</span>
          {numericValue !== null && <span className="text-xs" style={{ color: colors.textLight }}>/{max}</span>}
        </div>
      </div>
    );
  };

  // Status chip component
  const StatusChip = ({ status }) => {
    const styles = {
      OK: { bg: "bg-green-100", text: "text-green-700", border: "border-green-200" },
      WARN: { bg: "bg-amber-100", text: "text-amber-700", border: "border-amber-200" },
      CRIT: { bg: "bg-red-100", text: "text-red-700", border: "border-red-200" },
    };
    const s = styles[status] || styles.OK;
    return (
      <span className={`px-2 py-0.5 text-xs font-medium rounded-full border ${s.bg} ${s.text} ${s.border}`}>
        {status}
      </span>
    );
  };

  // Metric card component
  const MetricCard = ({ icon: Icon, title, value, unit, color, trend, trendValue, progress }) => {
    const colorStyles = {
      green: { bg: "bg-green-50", border: "border-green-200", text: "text-green-600", fill: colors.greenLight },
      orange: { bg: "bg-orange-50", border: "border-orange-200", text: "text-orange-600", fill: colors.terracotta },
      blue: { bg: "bg-blue-50", border: "border-blue-200", text: "text-blue-600", fill: colors.blue },
      gold: { bg: "bg-amber-50", border: "border-amber-200", text: "text-amber-600", fill: colors.gold },
    };
    const style = colorStyles[color] || colorStyles.green;
    const numericProgress = numericOrNull(progress);

    return (
      <div className={`relative p-4 rounded-xl border ${style.border} shadow-sm overflow-hidden`} style={{ background: colors.cream }}>
        <div className="absolute -right-4 -top-4 w-16 h-16 rounded-full opacity-8" style={{ background: style.fill }} />
        <div className="flex items-start justify-between">
          <div className={`p-2 rounded-lg ${style.bg}`}>
            <Icon className="w-5 h-5" style={{ color: style.fill }} />
          </div>
          {trend && isPresent(trendValue) && (
            <div className={`flex items-center gap-1 text-xs ${trend === "up" ? "text-green-600" : "text-red-600"}`}>
              {trend === "up" ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
              {trendValue}
            </div>
          )}
        </div>
        <div className="mt-3">
          <p className="text-sm" style={{ color: colors.textLight }}>{title}</p>
          <p className="text-2xl font-mono font-bold mt-1" style={{ color: colors.textDark }}>
            {displayValue(value)}
            {isPresent(value) && <span className="text-sm font-normal ml-1" style={{ color: colors.textLight }}>{unit}</span>}
          </p>
        </div>
        {numericProgress !== null && (
          <div className="mt-3 h-1.5 rounded-full bg-gray-100 overflow-hidden">
            <div className="h-full rounded-full transition-all duration-500" style={{ width: `${Math.max(0, Math.min(100, numericProgress))}%`, background: style.fill }} />
          </div>
        )}
      </div>
    );
  };

  const FarmLocationCard = ({ userData, colors, displayValue }) => {
    const location = [
      userData.village || userData.city,
      userData.district,
      userData.state,
    ].filter(Boolean).join(", ");

    return (
      <div className="p-5 rounded-xl border shadow-sm flex flex-col gap-4" style={{ background: colors.cream, borderColor: colors.creamDark }}>
        <h3 className="font-semibold" style={{ color: colors.textDark }}>Farm Location</h3>
        {location ? (
          <>
            <div className="flex items-center gap-2">
              <div className="w-9 h-9 rounded-full bg-[#EDF6F0] flex items-center justify-center">
                <span className="text-[#1B4332] text-base">Pin</span>
              </div>
              <div>
                <p className="text-sm font-medium" style={{ color: colors.textDark }}>{location}</p>
                <p className="text-xs" style={{ color: colors.textLight }}>
                  {displayValue(userData.landSize, " acres")} farm
                </p>
              </div>
            </div>
            <a
              href={`https://maps.google.com/?q=${encodeURIComponent(location)}`}
              target="_blank"
              rel="noopener noreferrer"
              className="text-xs underline"
              style={{ color: colors.textLight }}
            >
              View on Google Maps -&gt;
            </a>
          </>
        ) : (
          <p className="text-sm" style={{ color: colors.textLight }}>
            Add your farm location in Profile to see it here.
          </p>
        )}
      </div>
    );
  };

  const MoistureTrendEmptyState = () => (
    <div className="h-[200px] flex flex-col items-center justify-center gap-2 text-center">
      <div className="w-12 h-12 rounded-full bg-[#F4F1EA] flex items-center justify-center">
        <span className="text-xl">Chart</span>
      </div>
      <p className="text-sm" style={{ color: colors.textLight }}>
        Historical trend data will appear here once the backend collects readings over time.
      </p>
    </div>
  );

  const ActiveAlertsEmptyState = () => (
    <div className="space-y-2">
      <div className="flex items-center gap-2 text-sm py-3 px-2 rounded-lg bg-green-50 border border-green-100 text-green-700">
        <span>OK</span>
        <span>No active alerts - all readings are within safe range.</span>
      </div>
      <p className="text-xs px-2" style={{ color: colors.textLight }}>
        Alerts appear here when sensor values cross crop safety thresholds.
      </p>
    </div>
  );

  const CropHealthEmptyState = () => (
    <div className="flex flex-col items-center justify-center py-6 gap-2 text-center">
      <div className="w-16 h-16 rounded-full bg-[#F4F1EA] flex items-center justify-center text-2xl font-display text-[#1B4332]/40">
        --
      </div>
      <p className="text-sm" style={{ color: colors.textLight }}>
        Health score will appear once live sensor data is received from your field node.
      </p>
    </div>
  );

  // Render active page content
  const renderPage = () => {
    switch (activePage) {
      case "dashboard":
        return (
          <div className="space-y-6">
            {userData.sensorSetupStatus === "waiting" && (
              <div className="p-4 rounded-xl border border-amber-200 bg-amber-50 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
                <div className="flex items-start gap-3">
                  <Wifi className="w-5 h-5 text-amber-700 flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="font-semibold text-amber-900">Waiting for first sensor packet</p>
                    <p className="text-sm text-amber-800">Device <span className="font-mono">{userData.sensorDeviceId}</span> is configured. The dashboard will switch to ESP32 Live after readings arrive.</p>
                  </div>
                </div>
                <Button type="button" variant="outline" className="bg-white" onClick={testSensorConnection}>
                  Check now
                </Button>
              </div>
            )}
            {/* Metric Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <MetricCard icon={Droplets} title="Soil Moisture" value={sensorData.soilMoisture} unit="%" color="green" progress={sensorData.soilMoisture} />
              <MetricCard icon={CloudSun} title="Temperature" value={sensorData.temperature} unit={"\u00b0C"} color="orange" progress={isPresent(sensorData.temperature) ? percentValue(sensorData.temperature, 40) : null} />
              <MetricCard icon={Radio} title="Humidity" value={sensorData.humidity} unit="%" color="blue" progress={sensorData.humidity} />
              <MetricCard icon={Sprout} title="Soil pH" value={displayValue(sensorData.soilPh)} unit="" color="gold" progress={isPresent(sensorData.soilPh) ? percentValue(sensorData.soilPh, 10) : null} />
            </div>

            {/* Field Map and Charts Row */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <FarmLocationCard userData={userData} colors={colors} displayValue={displayValue} />
              <div className="p-5 rounded-xl border shadow-sm" style={{ background: colors.cream, borderColor: colors.creamDark }}>
                <h3 className="font-semibold mb-4" style={{ color: colors.textDark }}>Moisture Trend (24h)</h3>
                {sensorHistory.length > 0 ? (
                  <LineChart
                    data={sensorHistory
                      .map((reading) => ({
                        value: reading.soil_moisture ?? null,
                        label: reading.recorded_at ? new Date(reading.recorded_at).toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" }) : "",
                      }))
                      .filter((reading) => reading.value !== null)}
                    color={colors.greenLight}
                    height={200}
                  />
                ) : (
                  <MoistureTrendEmptyState />
                )}
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="p-5 rounded-xl border shadow-sm" style={{ background: colors.cream, borderColor: colors.creamDark }}>
                <h3 className="font-semibold mb-4" style={{ color: colors.textDark }}>Active Alerts</h3>
                {activeSensorAlerts.length > 0 ? (
                  <div className="space-y-2">
                    {activeSensorAlerts.slice(0, 3).map((alert) => (
                      <div
                        key={alert.key}
                        className="flex items-start gap-3 p-3 rounded-lg"
                        style={{
                          background: alert.tone === "critical" ? "#FEF2F2" : "#FFFBEB",
                          borderLeft: `3px solid ${alert.tone === "critical" ? "#EF4444" : "#F59E0B"}`,
                        }}
                      >
                        <alert.icon
                          className="w-4 h-4 mt-0.5 shrink-0"
                          style={{ color: alert.tone === "critical" ? "#EF4444" : "#F59E0B" }}
                        />
                        <div>
                          <p className="text-sm font-medium" style={{ color: "#111827" }}>{alert.title}</p>
                          <p className="text-xs mt-0.5" style={{ color: "#6B7280" }}>{alert.body}</p>
                        </div>
                      </div>
                    ))}
                    {activeSensorAlerts.length > 3 && (
                      <p className="text-xs text-center pt-1" style={{ color: colors.textLight }}>
                        +{activeSensorAlerts.length - 3} more alerts - check Notifications
                      </p>
                    )}
                  </div>
                ) : (
                  <ActiveAlertsEmptyState />
                )}
              </div>

              <div className="p-5 rounded-xl border shadow-sm" style={{ background: colors.cream, borderColor: colors.creamDark }}>
                <h3 className="font-semibold mb-4" style={{ color: colors.textDark }}>Crop Health Score</h3>
                <CropHealthEmptyState />
              </div>
            </div>
          </div>
        );

      case "sensors":
        return (
          <SensorSection
            colors={colors}
            sensorConnection={sensorConnection}
            sensorData={sensorData}
            userData={userData}
            onGoToSettings={() => setActivePage("settings")}
          />
        );

      case "pump":
        return (
          <PumpSection
            colors={colors}
            isDark={isDark}
            userData={userData}
            pumps={pumps}
            pumpControlMode={pumpControlMode}
            pumpDirectHost={pumpDirectHost}
            pumpUpdating={pumpUpdating}
            setPumpControlMode={setPumpControlMode}
            setPumpDirectHost={setPumpDirectHost}
            scheduledTimers={scheduledTimers}
            showTimerModal={showTimerModal}
            newTimer={newTimer}
            setNewTimer={setNewTimer}
            t={t}
            togglePump={togglePump}
            openTimerModal={openTimerModal}
            closeTimerModal={closeTimerModal}
            removeTimer={removeTimer}
            handleAddTimer={handleAddTimer}
            formatTime={formatTime}
            formatTimerStartTime={formatTimerStartTime}
          />
        );

      case "weather":
        return (
          <WeatherSection
            colors={colors}
            weatherData={weatherData}
            weatherError={weatherError}
            userData={userData}
          />
        );

      case "notifications":
        const notificationItems = [
          ...activeSensorAlerts.map((alert) => ({
            icon: alert.icon || AlertTriangle,
            title: alert.title,
            body: alert.body,
            tone: alert.tone === "critical" ? colors.red : colors.terracotta,
            time: alert.time || "Now",
          })),
        ];

        return (
          <div className="space-y-4">
            {notificationItems.length === 0 && (
              <div className="p-6 rounded-xl border shadow-sm text-center text-sm" style={{ background: colors.cream, borderColor: colors.creamDark, color: colors.textLight }}>
                No notifications yet.
              </div>
            )}
            {notificationItems.map((item) => (
              <div key={item.title} className="p-4 sm:p-5 rounded-xl border shadow-sm flex items-start gap-4" style={{ background: colors.cream, borderColor: colors.creamDark }}>
                <span className="w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0" style={{ background: `${item.tone}18`, color: item.tone }}>
                  <item.icon className="w-5 h-5" />
                </span>
                <div className="min-w-0 flex-1">
                  <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-1">
                    <h3 className="font-semibold" style={{ color: colors.textDark }}>{item.title}</h3>
                    <span className="text-xs" style={{ color: colors.textLight }}>{item.time}</span>
                  </div>
                  <p className="mt-1 text-sm" style={{ color: colors.textMid }}>{item.body}</p>
                </div>
              </div>
            ))}
          </div>
        );

      case "market":
        return (
          <MarketSection
            colors={colors}
            marketData={marketData}
            marketError={marketError}
            marketLoading={marketLoading}
            marketInsight={marketInsight}
            marketInsightError={marketInsightError}
            marketInsightLoading={marketInsightLoading}
            getUserMarketLocation={getUserMarketLocation}
            loadMarketPrices={loadMarketPrices}
            loadMarketInsight={loadMarketInsight}
          />
        );

      case "flow":
        return (
          <div className="space-y-6">
            <div className="mb-6 p-4 rounded-xl bg-[#F4F1EA] border border-[#D5D1C5]">
              <h2 className="font-display text-lg text-[#1A201C]">System data flow</h2>
              <p className="mt-1 text-sm text-[#1A201C]/60">
                This shows how data moves from your ESP32 field node through to the dashboard.
                Use this to check if your device is sending readings correctly.
              </p>
            </div>
            <div className="p-6 rounded-xl" style={{ background: `linear-gradient(135deg, ${colors.greenDark}, #0f2a1f)` }}>
              <h3 className="font-semibold mb-6" style={{ color: colors.cream }}>Data Pipeline</h3>
              <div className="flex items-center justify-between flex-wrap gap-4">
                {[
                  { icon: Radio, title: "Soil Sensors", desc: "Moisture, pH, NPK and climate readings", note: "Field input" },
                  { icon: Zap, title: "Main ESP32", desc: "SIM800L telemetry and relay polling", note: "Cellular" },
                  { icon: CloudSun, title: "FastAPI + MySQL", desc: "Stores latest sensor rows and pump timers", note: "Backend" },
                  { icon: LayoutDashboard, title: "Web Dashboard", desc: "Shows latest data and queues commands", note: "Browser" },
                  { icon: Radio, title: "Pump ESP32", desc: "Receives relay commands from the main ESP32", note: "Serial link" },
                ].map((node, idx) => (
                  <div key={node.title} className="flex items-center gap-2">
                    <div className={`p-4 rounded-xl ${idx < 2 ? "ring-2 ring-amber-400" : ""}`} style={{ background: idx < 2 ? "rgba(200, 168, 75, 0.2)" : "rgba(255,255,255,0.1)" }}>
                      <node.icon className={`w-6 h-6 ${idx < 2 ? "text-amber-400" : "text-cream"}`} />
                    </div>
                    <div className={idx < 2 ? "text-amber-400" : "text-cream"}>
                      <p className="font-medium text-sm">{node.title}</p>
                      <p className="text-xs opacity-70">{node.desc}</p>
                      <p className="text-xs font-mono opacity-50 mt-1">{node.note}</p>
                    </div>
                    {idx < 4 && <span className="text-2xl text-cream animate-pulse" style={{ animationDuration: "2s" }}>{"->"}</span>}
                  </div>
                ))}
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
              {Object.entries(telemetryPacket).map(([key, value]) => (
                <div key={key} className="p-3 rounded-lg text-center" style={{ background: "rgba(30, 58, 47, 0.9)" }}>
                  <p className="text-xs font-mono mb-1" style={{ color: colors.textLight }}>{key}</p>
                  <p className="font-mono font-bold" style={{ color: colors.greenLight }}>{isPresent(value) ? value : EMPTY_DISPLAY}</p>
                </div>
              ))}
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="p-5 rounded-xl" style={{ background: "#0d1f17" }}>
                <h3 className="font-semibold mb-4" style={{ color: colors.greenLight }}>API Endpoint Log</h3>
                <div ref={logContainerRef} className="space-y-2 max-h-64 overflow-y-auto font-mono text-sm">
                  {apiLogs.map((log) => (
                    <div key={log.id} className="flex items-center gap-2">
                      <span className="text-xs" style={{ color: colors.textLight }}>{new Date(log.timestamp).toLocaleTimeString()}</span>
                      <span className={log.method === "GET" ? "text-blue-400" : log.method === "POST" ? "text-green-400" : "text-amber-400"}>{log.method}</span>
                      <span style={{ color: colors.cream }}>{log.path}</span>
                      <span className={log.status === 200 ? "text-green-400" : "text-amber-400"}>{log.status}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="p-5 rounded-xl" style={{ background: "#0d1f17" }}>
                <h3 className="font-semibold mb-4" style={{ color: colors.greenLight }}>Latest Telemetry Packet</h3>
                <pre className="font-mono text-sm overflow-x-auto" style={{ color: colors.cream }}>{JSON.stringify(telemetryPacket, null, 2)}</pre>
              </div>
            </div>
          </div>
        );

      case "ai":
        return (
          <AiSection
            colors={colors}
            chatContainerRef={chatContainerRef}
            chatMessages={chatMessages}
            userName={userData.name}
            isTyping={isTyping}
            showSuggestions={showSuggestions}
            suggestionChips={suggestionChips}
            ct={ct}
            handleSuggestionClick={handleSuggestionClick}
            chatInput={chatInput}
            setChatInput={setChatInput}
            handleSendMessage={handleSendMessage}
            isListening={isListening}
            startListening={startListening}
            stopListening={stopListening}
            language={language}
          />
        );

      case "cropPlanner":
        return (
          <div className="-m-3 sm:-m-5 md:-m-6">
            <CropPlanner
              key={language}
              sensorData={sensorData}
              sensorConnection={sensorConnection}
              userProfile={userData}
              protectedFetch={protectedFetch}
              language={language}
              embedded
            />
          </div>
        );

      case "settings":
        return <SettingsSection ctx={ctx} />;

      case "profile":
        return <ProfileSection ctx={ctx} />;

      default:
        return null;
    }
  };

  return renderPage();
}
