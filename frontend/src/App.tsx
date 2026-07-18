import React, { useEffect, useMemo, useRef, useState } from 'react'
import {
  Plane,
  AlertTriangle,
  CheckCircle,
  Info,
  MapPin,
  Coffee,
  Utensils,
  BatteryCharging,
  Briefcase,
  Users,
  CloudRain,
  Sun as SunIcon,
  Moon,
  Bell,
  MessageSquare,
  Send,
  Mic,
  Clock,
  Shield,
  Armchair,
  X,
  Train,
  Sparkles,
  RefreshCw,
  Luggage,
} from 'lucide-react'

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------
interface Weather {
  temp_c: number
  condition: string
  icon: string
}

interface Airport {
  iata: string
  name: string
  airport: string
  terminal: string
  gate: string
  weather?: Weather
}

interface Flight {
  flight_number: string
  airline: string
  airline_code: string
  origin: Airport
  destination: Airport
  aircraft: string
  departure_scheduled: string
  departure_estimated: string
  arrival_scheduled: string
  arrival_estimated: string
  boarding_starts: string
  gate: string
  status: string
  delay_minutes: number
  delay_reason: string
  seat: string
  class: string
  booking_ref: string
  duration?: string
}

interface TimelineItem {
  label: string
  time: string
  status: 'completed' | 'in_progress' | 'pending'
  location: string
}

interface Insight {
  type: 'warning' | 'success' | 'info'
  icon: string
  title: string
  detail: string
}

interface Alternative {
  id: string
  type: 'flight' | 'rail' | 'upgrade'
  title: string
  departure: string
  arrival: string
  origin: string
  destination: string
  stops: number
  price: number
  currency: string
  duration: string
  confidence: number
  recommendation: string
  reason: string
  co2_g: number
}

interface Service {
  id: string
  category: string
  name: string
  location: string
  distance_m: number
  rating: number
  open: boolean
}

interface AgentAction {
  step: number
  title: string
  detail: string
  status: string
}

interface Alert {
  id: string
  severity: 'high' | 'medium' | 'low'
  title: string
  time: string
  read: boolean
}

interface Recommendation {
  id: string
  title: string
  reasons: string[]
  confidence: number
  saves_minutes: number
}

interface MapPoint {
  id: string
  label: string
  x: number
  y: number
  type: string
}

interface DashboardData {
  traveler: {
    id: string
    name: string
    tier: string
    seat: string
    frequent_flyer: string
  }
  flight: Flight
  current_journey: Flight
  weather: { origin: Weather; destination: Weather }
  timeline: TimelineItem[]
  proactive_insights: Insight[]
  alternatives: Alternative[]
  services: Service[]
  agent_actions: AgentAction[]
  alerts: Alert[]
  recommendations: Recommendation[]
  map_points: MapPoint[]
}

interface Message {
  role: 'user' | 'assistant'
  text: string
  source?: string
  time: string
}

interface Toast {
  id: string
  message: string
  type: 'success' | 'info' | 'error'
}

// ---------------------------------------------------------------------------
// Utilities
// ---------------------------------------------------------------------------
function formatTime(iso: string) {
  const d = new Date(iso)
  return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

function formatDuration(minutes: number) {
  const h = Math.floor(minutes / 60)
  const m = minutes % 60
  return `${h}h ${m}m`
}

function cn(...classes: (string | boolean | undefined)[]) {
  return classes.filter(Boolean).join(' ')
}

function useInterval(callback: () => void, delay: number | null) {
  const savedRef = useRef(callback)
  useEffect(() => { savedRef.current = callback }, [callback])
  useEffect(() => {
    if (delay === null) return
    const id = setInterval(() => savedRef.current(), delay)
    return () => clearInterval(id)
  }, [delay])
}

// ---------------------------------------------------------------------------
// UI primitives
// ---------------------------------------------------------------------------
function SkeletonCard({ className }: { className?: string }) {
  return (
    <div className={cn('card animate-pulse', className)}>
      <div className="h-4 w-1/3 bg-slate-200 dark:bg-slate-700 rounded mb-4" />
      <div className="h-20 bg-slate-200 dark:bg-slate-700 rounded" />
    </div>
  )
}

function Badge({ children, tone = 'neutral' }: { children: React.ReactNode; tone?: 'neutral' | 'warning' | 'success' | 'info' }) {
  const toneStyles = {
    neutral: 'bg-slate-100 text-slate-700 dark:bg-slate-700 dark:text-slate-300',
    warning: 'bg-amber-100 text-amber-800 dark:bg-amber-900/40 dark:text-amber-300',
    success: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-300',
    info: 'bg-brand-100 text-brand-800 dark:bg-brand-900/40 dark:text-brand-300',
  }
  return <span className={cn('badge', toneStyles[tone])}>{children}</span>
}

function ToastContainer({ toasts, remove }: { toasts: Toast[]; remove: (id: string) => void }) {
  return (
    <div className="fixed bottom-5 right-5 z-50 flex flex-col gap-2">
      {toasts.map((t) => (
        <div
          key={t.id}
          className={cn(
            'flex items-center gap-3 rounded-xl px-4 py-3 shadow-lg text-white min-w-[18rem]',
            t.type === 'success' ? 'bg-emerald-600' : t.type === 'error' ? 'bg-rose-600' : 'bg-brand-600'
          )}
        >
          <span className="text-sm font-medium">{t.message}</span>
          <button onClick={() => remove(t.id)} className="ml-auto hover:opacity-80"><X size={16} /></button>
        </div>
      ))}
    </div>
  )
}

// ---------------------------------------------------------------------------
// Components
// ---------------------------------------------------------------------------
function Header({ dark, toggleDark, unread }: { dark: boolean; toggleDark: () => void; unread: number }) {
  return (
    <header className="sticky top-0 z-30 bg-white/80 dark:bg-slate-900/80 backdrop-blur border-b border-slate-200 dark:border-slate-800">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-3 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-xl bg-brand-600 text-white"><Sparkles size={22} /></div>
          <div>
            <h1 className="text-lg font-bold text-slate-900 dark:text-white tracking-tight">JourneyMind AI</h1>
            <p className="text-xs text-slate-500 dark:text-slate-400 hidden sm:block">Proactive AI Travel Disruption Assistant</p>
          </div>
        </div>
        <div className="flex items-center gap-2 sm:gap-4">
          <button className="relative p-2 rounded-full hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-600 dark:text-slate-300">
            <Bell size={20} />
            {unread > 0 && <span className="absolute top-1 right-1 h-2.5 w-2.5 rounded-full bg-rose-500 ring-2 ring-white dark:ring-slate-900" />}
          </button>
          <button onClick={toggleDark} className="p-2 rounded-full hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-600 dark:text-slate-300">
            {dark ? <SunIcon size={20} /> : <Moon size={20} />}
          </button>
          <div className="hidden sm:flex items-center gap-2 pl-2 border-l border-slate-200 dark:border-slate-700">
            <div className="h-8 w-8 rounded-full bg-gradient-to-tr from-brand-500 to-violet-500 flex items-center justify-center text-white text-xs font-bold">SJ</div>
            <div className="text-sm"><span className="font-medium text-slate-900 dark:text-white">Sarah Johnson</span><span className="text-slate-500 dark:text-slate-400 block text-xs">Star Gold</span></div>
          </div>
        </div>
      </div>
    </header>
  )
}

function FlightCard({ flight }: { flight: Flight }) {
  const dep = new Date(flight.departure_estimated)
  const now = new Date()
  const minutesToDep = Math.max(0, Math.floor((dep.getTime() - now.getTime()) / 60000))
  const hasDelay = flight.delay_minutes > 0

  const statusTone = flight.status === 'Delayed' ? 'warning' : flight.status === 'Cancelled' ? 'error' : 'success'
  const statusColor = statusTone === 'warning' ? 'text-amber-600 bg-amber-50 dark:bg-amber-900/20 dark:text-amber-400' : 'text-emerald-600 bg-emerald-50 dark:bg-emerald-900/20 dark:text-emerald-400'

  return (
    <div className="card bg-gradient-to-br from-white to-slate-50 dark:from-slate-800 dark:to-slate-900">
      <div className="flex items-start justify-between">
        <div>
          <p className="section-title">Current Journey</p>
          <div className="flex items-center gap-2 mt-1">
            <span className="text-2xl font-bold text-slate-900 dark:text-white">{flight.flight_number}</span>
            <span className="text-sm text-slate-500 dark:text-slate-400">{flight.airline} · {flight.aircraft}</span>
          </div>
        </div>
        <div className={cn('px-3 py-1 rounded-full text-sm font-semibold', statusColor)}>{flight.status}</div>
      </div>

      <div className="mt-6 flex items-center justify-between gap-4">
        <div className="text-left">
          <p className="text-3xl font-bold text-slate-900 dark:text-white">{flight.origin.iata}</p>
          <p className="text-sm text-slate-500 dark:text-slate-400">{flight.origin.airport}</p>
          <p className="text-lg font-semibold text-slate-800 dark:text-slate-200 mt-1">{formatTime(flight.departure_estimated)}</p>
          {flight.departure_scheduled !== flight.departure_estimated && (
            <p className="text-xs text-slate-400 line-through">{formatTime(flight.departure_scheduled)}</p>
          )}
        </div>

        <div className="flex-1 flex flex-col items-center px-4">
          {hasDelay ? (
            <div className="text-xs text-amber-600 dark:text-amber-400 mb-1">{formatDuration(flight.delay_minutes)} delay</div>
          ) : (
            <div className="text-xs text-emerald-600 dark:text-emerald-400 mb-1">On time</div>
          )}
          <div className="w-full h-1 bg-slate-200 dark:bg-slate-700 rounded relative overflow-hidden">
            <div className={cn('absolute top-0 left-0 h-full bg-brand-500 rounded', hasDelay ? 'w-3/4' : 'w-full')} />
            <Plane className={cn('absolute top-1/2 -translate-y-1/2 text-brand-600', hasDelay ? 'left-3/4' : 'left-full -translate-x-full')} size={18} />
          </div>
          <p className="text-xs text-slate-500 mt-2">{flight.duration || '2h 15m'}</p>
        </div>

        <div className="text-right">
          <p className="text-3xl font-bold text-slate-900 dark:text-white">{flight.destination.iata}</p>
          <p className="text-sm text-slate-500 dark:text-slate-400">{flight.destination.airport}</p>
          <p className="text-lg font-semibold text-slate-800 dark:text-slate-200 mt-1">{formatTime(flight.arrival_estimated)}</p>
          {flight.arrival_scheduled !== flight.arrival_estimated && (
            <p className="text-xs text-slate-400 line-through">{formatTime(flight.arrival_scheduled)}</p>
          )}
        </div>
      </div>

      <div className="mt-6 grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div className="rounded-xl bg-slate-100 dark:bg-slate-700/50 p-3">
          <p className="text-xs text-slate-500 dark:text-slate-400">Gate</p>
          <p className="text-lg font-bold text-slate-900 dark:text-white">{flight.gate}</p>
        </div>
        <div className="rounded-xl bg-slate-100 dark:bg-slate-700/50 p-3">
          <p className="text-xs text-slate-500 dark:text-slate-400">Boarding</p>
          <p className="text-lg font-bold text-slate-900 dark:text-white">{formatTime(flight.boarding_starts)}</p>
        </div>
        <div className="rounded-xl bg-slate-100 dark:bg-slate-700/50 p-3">
          <p className="text-xs text-slate-500 dark:text-slate-400">Seat</p>
          <p className="text-lg font-bold text-slate-900 dark:text-white">{flight.seat}</p>
        </div>
        <div className="rounded-xl bg-slate-100 dark:bg-slate-700/50 p-3">
          <p className="text-xs text-slate-500 dark:text-slate-400">Countdown</p>
          <p className="text-lg font-bold text-slate-900 dark:text-white">{minutesToDep > 0 ? `${minutesToDep}m` : 'Due'}</p>
        </div>
      </div>

      {hasDelay && (
        <div className="mt-4 flex items-center gap-2 text-sm text-amber-700 dark:text-amber-400">
          <AlertTriangle size={16} />
          <span>{flight.delay_reason} — {flight.delay_minutes} min delay</span>
        </div>
      )}
    </div>
  )
}

function Timeline({ items }: { items: TimelineItem[] }) {
  return (
    <div className="card">
      <p className="section-title">Journey Timeline</p>
      <div className="relative">
        <div className="absolute left-3.5 top-2 bottom-2 w-0.5 bg-slate-200 dark:bg-slate-700" />
        <div className="space-y-5">
          {items.map((item, idx) => (
            <div key={idx} className="relative flex items-start gap-4">
              <div className={cn(
                'z-10 mt-0.5 h-3 w-3 rounded-full border-2',
                item.status === 'completed' ? 'bg-emerald-500 border-emerald-500' : item.status === 'in_progress' ? 'bg-brand-500 border-brand-500 ring-4 ring-brand-200 dark:ring-brand-900/50' : 'bg-white dark:bg-slate-800 border-slate-300 dark:border-slate-600'
              )} />
              <div className="flex-1">
                <div className="flex items-center justify-between">
                  <span className={cn('font-semibold', item.status === 'pending' ? 'text-slate-400 dark:text-slate-500' : 'text-slate-900 dark:text-white')}>{item.label}</span>
                  <span className="text-sm text-slate-500 dark:text-slate-400">{item.time}</span>
                </div>
                <p className={cn('text-sm', item.status === 'pending' ? 'text-slate-400 dark:text-slate-500' : 'text-slate-500 dark:text-slate-400')}>{item.location}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

function ProactivePanel({ insights }: { insights: Insight[] }) {
  const iconMap: Record<string, React.ReactNode> = {
    alert: <AlertTriangle size={18} />,
    route: <RefreshCw size={18} />,
    hotel: <Luggage size={18} />,
    lounge: <Armchair size={18} />,
    walk: <MapPin size={18} />,
    shield: <Shield size={18} />,
    clock: <Clock size={18} />,
  }

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <p className="section-title mb-0">Proactive AI Insights</p>
        <Badge tone="info">Live</Badge>
      </div>
      <div className="space-y-3">
        {insights.map((insight, idx) => (
          <div key={idx} className={cn(
            'flex items-start gap-3 rounded-xl p-3 border-l-4 animate-slide-in',
            insight.type === 'warning' ? 'bg-amber-50/60 dark:bg-amber-900/20 border-amber-500 text-amber-900 dark:text-amber-100' :
            insight.type === 'success' ? 'bg-emerald-50/60 dark:bg-emerald-900/20 border-emerald-500 text-emerald-900 dark:text-emerald-100' :
            'bg-brand-50/60 dark:bg-brand-900/20 border-brand-500 text-slate-900 dark:text-slate-100'
          )} style={{ animationDelay: `${idx * 80}ms` }}>
            <div className={cn('p-1.5 rounded-lg shrink-0', insight.type === 'warning' ? 'bg-amber-200 dark:bg-amber-800/40' : insight.type === 'success' ? 'bg-emerald-200 dark:bg-emerald-800/40' : 'bg-brand-200 dark:bg-brand-800/40')}>
              {iconMap[insight.icon] || <Info size={18} />}
            </div>
            <div>
              <p className="font-semibold text-sm">{insight.title}</p>
              <p className="text-xs opacity-90 mt-0.5">{insight.detail}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

function AirportMap({ points }: { points: MapPoint[] }) {
  const colorMap: Record<string, string> = {
    current: '#2563eb',
    gate: '#f59e0b',
    lounge: '#10b981',
    restaurant: '#ef4444',
    coffee: '#8b5cf6',
  }
  return (
    <div className="card">
      <p className="section-title">Airport Map</p>
      <div className="relative w-full aspect-video rounded-xl overflow-hidden border border-slate-200 dark:border-slate-700 bg-slate-100 dark:bg-slate-900">
        <svg viewBox="0 0 100 100" className="w-full h-full">
          {/* Terminal outline */}
          <rect x="10" y="10" width="85" height="80" rx="4" fill="#f1f5f9" stroke="#cbd5e1" className="dark:fill-slate-800 dark:stroke-slate-700" />
          <rect x="25" y="10" width="8" height="80" fill="#e2e8f0" className="dark:fill-slate-700/50" />
          {/* Walking path */}
          <path d="M 35 60 L 55 25 L 65 35" fill="none" stroke="#3b82f6" strokeWidth="1.2" strokeDasharray="2 1" className="opacity-80" />
          {points.map((p) => (
            <g key={p.id}>
              <circle cx={p.x} cy={p.y} r="3" fill={colorMap[p.type] || '#64748b'} stroke="white" strokeWidth="1" className="dark:stroke-slate-900" />
              <text x={p.x + 4} y={p.y + 1} fontSize="3" fill="currentColor" className="text-slate-700 dark:text-slate-300">{p.label}</text>
            </g>
          ))}
        </svg>
        <div className="absolute bottom-2 left-2 flex flex-wrap gap-2 text-[10px]">
          {Object.entries(colorMap).map(([k, c]) => (
            <span key={k} className="flex items-center gap-1 rounded bg-white/90 dark:bg-slate-800/90 px-1.5 py-0.5">
              <span className="h-2 w-2 rounded-full" style={{ background: c }} /> {k}
            </span>
          ))}
        </div>
      </div>
    </div>
  )
}

function Services({ services }: { services: Service[] }) {
  const [filter, setFilter] = useState('all')
  const categories = ['all', 'lounge', 'restaurant', 'coffee', 'charging', 'workspace', 'family']
  const filtered = filter === 'all' ? services : services.filter((s) => s.category === filter)

  const iconMap: Record<string, React.ReactNode> = {
    lounge: <Armchair size={18} />,
    restaurant: <Utensils size={18} />,
    coffee: <Coffee size={18} />,
    charging: <BatteryCharging size={18} />,
    workspace: <Briefcase size={18} />,
    family: <Users size={18} />,
  }

  return (
    <div className="card">
      <p className="section-title">Airport Services</p>
      <div className="flex flex-wrap gap-2 mb-4">
        {categories.map((c) => (
          <button
            key={c}
            onClick={() => setFilter(c)}
            className={cn(
              'px-3 py-1 rounded-full text-xs font-medium capitalize transition-colors',
              filter === c ? 'bg-brand-600 text-white' : 'bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-600'
            )}
          >
            {c}
          </button>
        ))}
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {filtered.map((svc) => (
          <div key={svc.id} className="rounded-xl border border-slate-100 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/50 p-3 flex items-start gap-3">
            <div className="p-2 rounded-lg bg-white dark:bg-slate-700 text-brand-600 dark:text-brand-400">{iconMap[svc.category] || <MapPin size={18} />}</div>
            <div className="flex-1 min-w-0">
              <p className="font-semibold text-sm truncate text-slate-900 dark:text-white">{svc.name}</p>
              <p className="text-xs text-slate-500 dark:text-slate-400 truncate">{svc.location}</p>
              <div className="mt-1 flex items-center gap-2 text-xs">
                <span className="text-emerald-600 dark:text-emerald-400 font-medium">{svc.open ? 'Open' : 'Closed'}</span>
                <span className="text-slate-400">·</span>
                <span className="text-slate-500 dark:text-slate-400">{svc.distance_m}m</span>
                <span className="text-slate-400">·</span>
                <span className="text-amber-600 dark:text-amber-400">★ {svc.rating}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

function RebookingPanel({ alternatives, onRebook, loading }: { alternatives: Alternative[]; onRebook: (id: string) => void; loading: string | null }) {
  const typeIcon = {
    flight: <Plane size={18} />,
    rail: <Train size={18} />,
    upgrade: <Sparkles size={18} />,
  }

  const badgeTone: Record<string, 'success' | 'info' | 'neutral'> = {
    Recommended: 'success',
    Alternative: 'info',
    Backup: 'neutral',
    Comfort: 'info',
  }

  return (
    <div className="card">
      <p className="section-title">AI Rebooking Engine</p>
      <div className="space-y-3">
        {alternatives.map((alt) => (
          <div key={alt.id} className="group rounded-xl border border-slate-200 dark:border-slate-700 p-4 hover:border-brand-300 dark:hover:border-brand-500 transition-colors bg-white dark:bg-slate-800">
            <div className="flex items-start justify-between gap-3">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-200">{typeIcon[alt.type]}</div>
                <div>
                  <p className="font-semibold text-slate-900 dark:text-white">{alt.title}</p>
                  <p className="text-xs text-slate-500 dark:text-slate-400">{formatTime(alt.departure)} – {formatTime(alt.arrival)} · {alt.duration} · {alt.stops === 0 ? 'Non-stop' : `${alt.stops} stop`}</p>
                </div>
              </div>
              <Badge tone={badgeTone[alt.recommendation] || 'neutral'}>{alt.recommendation}</Badge>
            </div>

            <div className="mt-3 grid grid-cols-3 gap-2 text-center">
              <div className="rounded-lg bg-slate-50 dark:bg-slate-700/50 p-2">
                <p className="text-xs text-slate-500 dark:text-slate-400">Price</p>
                <p className="text-sm font-bold text-slate-900 dark:text-white">{alt.price === 0 ? 'Free' : `${alt.price} ${alt.currency}`}</p>
              </div>
              <div className="rounded-lg bg-slate-50 dark:bg-slate-700/50 p-2">
                <p className="text-xs text-slate-500 dark:text-slate-400">Confidence</p>
                <p className="text-sm font-bold text-slate-900 dark:text-white">{(alt.confidence * 100).toFixed(0)}%</p>
              </div>
              <div className="rounded-lg bg-slate-50 dark:bg-slate-700/50 p-2">
                <p className="text-xs text-slate-500 dark:text-slate-400">CO₂</p>
                <p className="text-sm font-bold text-slate-900 dark:text-white">{alt.co2_g}g</p>
              </div>
            </div>

            <div className="mt-3 flex items-center gap-2 text-sm text-brand-700 dark:text-brand-300">
              <Sparkles size={14} />
              <span>Recommended because: <span className="font-medium">{alt.reason}</span></span>
            </div>

            <button
              disabled={loading === alt.id}
              onClick={() => onRebook(alt.id)}
              className="mt-3 w-full rounded-xl bg-brand-600 px-4 py-2 text-sm font-medium text-white hover:bg-brand-700 disabled:opacity-60 flex items-center justify-center gap-2"
            >
              {loading === alt.id ? <RefreshCw size={16} className="animate-spin" /> : <CheckCircle size={16} />}
              {loading === alt.id ? 'Rebooking...' : `Select ${alt.recommendation}`}
            </button>
          </div>
        ))}
      </div>
    </div>
  )
}

function Recommendations({ recommendations }: { recommendations: Recommendation[] }) {
  return (
    <div className="card">
      <p className="section-title">Smart AI Reasoning</p>
      <div className="space-y-3">
        {recommendations.map((rec) => (
          <div key={rec.id} className="rounded-xl border border-slate-200 dark:border-slate-700 p-4">
            <div className="flex items-start justify-between">
              <p className="font-semibold text-sm text-slate-900 dark:text-white">{rec.title}</p>
              <Badge tone={rec.confidence > 0.9 ? 'success' : 'info'}>{(rec.confidence * 100).toFixed(0)}% confidence</Badge>
            </div>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">{rec.saves_minutes >= 0 ? `Saves ${rec.saves_minutes} minutes` : `Adds ${Math.abs(rec.saves_minutes)} minutes`}</p>
            <div className="mt-2 flex flex-wrap gap-2">
              {rec.reasons.map((reason, i) => (
                <span key={i} className="inline-flex items-center gap-1 rounded-full bg-emerald-50 dark:bg-emerald-900/30 text-emerald-700 dark:text-emerald-300 px-2.5 py-0.5 text-xs font-medium">
                  <CheckCircle size={12} /> {reason}
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

function AgentPanel({ actions }: { actions: AgentAction[] }) {
  return (
    <div className="card">
      <p className="section-title">AI Agent Workflow</p>
      <div className="space-y-0">
        {actions.map((action, idx) => (
          <div key={idx} className="relative pl-7 pb-5 last:pb-0">
            <div className="absolute left-0 top-0 flex flex-col items-center h-full">
              <div className="z-10 h-5 w-5 rounded-full bg-emerald-500 flex items-center justify-center text-white"><CheckCircle size={12} /></div>
              {idx !== actions.length - 1 && <div className="flex-1 w-0.5 bg-emerald-200 dark:bg-emerald-800 mt-1" />}
            </div>
            <div>
              <p className="text-sm font-semibold text-slate-900 dark:text-white">{action.title}</p>
              <p className="text-xs text-slate-500 dark:text-slate-400">{action.detail}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

function PassengerCard({ traveler, flight }: { traveler: DashboardData['traveler']; flight: Flight }) {
  return (
    <div className="card">
      <p className="section-title">Traveler</p>
      <div className="flex items-center gap-4">
        <div className="h-14 w-14 rounded-full bg-gradient-to-tr from-brand-500 to-violet-500 flex items-center justify-center text-white text-lg font-bold">{traveler.name.split(' ').map((n) => n[0]).join('')}</div>
        <div>
          <p className="text-lg font-bold text-slate-900 dark:text-white">{traveler.name}</p>
          <p className="text-sm text-slate-500 dark:text-slate-400">{traveler.tier}</p>
        </div>
      </div>
      <div className="mt-4 grid grid-cols-2 gap-3">
        <div className="rounded-xl bg-slate-50 dark:bg-slate-700/50 p-2">
          <p className="text-xs text-slate-500 dark:text-slate-400">Seat</p>
          <p className="font-semibold text-slate-900 dark:text-white">{flight.seat}</p>
        </div>
        <div className="rounded-xl bg-slate-50 dark:bg-slate-700/50 p-2">
          <p className="text-xs text-slate-500 dark:text-slate-400">Booking</p>
          <p className="font-semibold text-slate-900 dark:text-white">{flight.booking_ref}</p>
        </div>
        <div className="rounded-xl bg-slate-50 dark:bg-slate-700/50 p-2">
          <p className="text-xs text-slate-500 dark:text-slate-400">FF #</p>
          <p className="font-semibold text-slate-900 dark:text-white truncate">{traveler.frequent_flyer}</p>
        </div>
        <div className="rounded-xl bg-slate-50 dark:bg-slate-700/50 p-2">
          <p className="text-xs text-slate-500 dark:text-slate-400">Class</p>
          <p className="font-semibold text-slate-900 dark:text-white">{flight.class}</p>
        </div>
      </div>
    </div>
  )
}

function WeatherCard({ origin, destination }: { origin: Weather; destination: Weather }) {
  return (
    <div className="card">
      <p className="section-title">Weather</p>
      <div className="space-y-3">
        <div className="flex items-center justify-between rounded-xl bg-slate-50 dark:bg-slate-700/50 p-3">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-white dark:bg-slate-600 text-amber-500"><SunIcon size={20} /></div>
            <div>
              <p className="font-semibold text-sm text-slate-900 dark:text-white">Munich (MUC)</p>
              <p className="text-xs text-slate-500 dark:text-slate-400">{origin.condition}</p>
            </div>
          </div>
          <span className="text-xl font-bold text-slate-900 dark:text-white">{origin.temp_c}°</span>
        </div>
        <div className="flex items-center justify-between rounded-xl bg-slate-50 dark:bg-slate-700/50 p-3">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-white dark:bg-slate-600 text-sky-500"><CloudRain size={20} /></div>
            <div>
              <p className="font-semibold text-sm text-slate-900 dark:text-white">London (LHR)</p>
              <p className="text-xs text-slate-500 dark:text-slate-400">{destination.condition}</p>
            </div>
          </div>
          <span className="text-xl font-bold text-slate-900 dark:text-white">{destination.temp_c}°</span>
        </div>
      </div>
    </div>
  )
}

function AlertsPanel({ alerts }: { alerts: Alert[] }) {
  return (
    <div className="card">
      <p className="section-title">Travel Alerts</p>
      <div className="space-y-2">
        {alerts.map((alert) => (
          <div key={alert.id} className={cn('flex items-start gap-3 rounded-xl p-3 border-l-4', alert.severity === 'high' ? 'border-rose-500 bg-rose-50 dark:bg-rose-900/20' : alert.severity === 'medium' ? 'border-amber-500 bg-amber-50 dark:bg-amber-900/20' : 'border-slate-300 bg-slate-50 dark:bg-slate-800/50')}>
            <div className={cn('mt-0.5 h-2 w-2 rounded-full shrink-0', alert.severity === 'high' ? 'bg-rose-500' : alert.severity === 'medium' ? 'bg-amber-500' : 'bg-slate-400')} />
            <div className="flex-1">
              <p className={cn('text-sm font-medium', !alert.read ? 'text-slate-900 dark:text-white' : 'text-slate-500 dark:text-slate-400')}>{alert.title}</p>
              <p className="text-xs text-slate-400">{alert.time}</p>
            </div>
            {!alert.read && <span className="h-2 w-2 rounded-full bg-brand-500" />}
          </div>
        ))}
      </div>
    </div>
  )
}

function CopilotChat({ flight, onShowToast }: { flight: Flight; onShowToast: (msg: string, type: 'success' | 'info' | 'error') => void }) {
  const [messages, setMessages] = useState<Message[]>([
    { role: 'assistant', text: `Hi Sarah — I see LH762 is delayed 95 minutes. I've already evaluated rebooking options and can answer any questions.`, source: 'mock', time: nowTime() },
  ])
  const [input, setInput] = useState('')
  const [typing, setTyping] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)

  const quickPrompts = [
    'My flight is delayed.',
    'What are my options?',
    'Can I still make my meeting?',
    'Find another route.',
    'Which lounge should I use?',
    'What restaurants are nearby?',
    'When should I leave for boarding?',
    "What's the fastest alternative?",
  ]

  function nowTime() {
    return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages, typing])

  async function send(text: string) {
    if (!text.trim()) return
    const userMsg: Message = { role: 'user', text, time: nowTime() }
    setMessages((prev) => [...prev, userMsg])
    setInput('')
    setTyping(true)
    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text }),
      })
      const data = await res.json()
      setTimeout(() => {
        setTyping(false)
        setMessages((prev) => [...prev, { role: 'assistant', text: data.reply, source: data.source, time: data.timestamp || nowTime() }])
      }, 800)
    } catch {
      setTyping(false)
      setMessages((prev) => [...prev, { role: 'assistant', text: 'I lost connection for a moment — please try again.', time: nowTime() }])
    }
  }

  function mockVoice() {
    onShowToast('Listening for voice input... (mock)', 'info')
    setTimeout(() => onShowToast('Voice input captured: "What are my options?"', 'success'), 1500)
    setTimeout(() => send('What are my options?'), 2200)
  }

  return (
    <div className="card flex flex-col h-[36rem] lg:h-[calc(100vh-8rem)] lg:sticky lg:top-28">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <div className="p-1.5 rounded-lg bg-brand-600 text-white"><MessageSquare size={18} /></div>
          <p className="font-bold text-slate-900 dark:text-white">JourneyMind Copilot</p>
        </div>
        <Badge tone={flight.status === 'Delayed' ? 'warning' : 'success'}>{flight.status}</Badge>
      </div>

      <div className="flex-1 overflow-y-auto space-y-3 pr-1">
        {messages.map((m, idx) => (
          <div key={idx} className={cn('flex', m.role === 'user' ? 'justify-end' : 'justify-start')}>
            <div className={cn('max-w-[90%] rounded-2xl px-4 py-2.5 text-sm', m.role === 'user' ? 'bg-brand-600 text-white rounded-br-none' : 'bg-slate-100 dark:bg-slate-700 text-slate-800 dark:text-slate-100 rounded-bl-none')}>
              <p>{m.text}</p>
              <div className={cn('flex items-center gap-1 mt-1 text-[10px] opacity-70', m.role === 'user' ? 'justify-end' : 'justify-start')}>
                <span>{m.time}</span>
                {m.source && m.role === 'assistant' && <span>· {m.source === 'openai' ? 'GPT-4o' : 'JourneyMind'}</span>}
              </div>
            </div>
          </div>
        ))}
        {typing && (
          <div className="flex justify-start">
            <div className="bg-slate-100 dark:bg-slate-700 rounded-2xl rounded-bl-none px-4 py-3 flex gap-1.5">
              <span className="h-2 w-2 rounded-full bg-slate-400 animate-bounce" style={{ animationDelay: '0ms' }} />
              <span className="h-2 w-2 rounded-full bg-slate-400 animate-bounce" style={{ animationDelay: '120ms' }} />
              <span className="h-2 w-2 rounded-full bg-slate-400 animate-bounce" style={{ animationDelay: '240ms' }} />
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <div className="mt-3">
        <div className="flex flex-wrap gap-2 mb-2">
          {quickPrompts.slice(0, 4).map((p) => (
            <button key={p} onClick={() => send(p)} className="text-[11px] px-2.5 py-1 rounded-full bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-600 transition-colors">{p}</button>
          ))}
        </div>
        <div className="flex items-center gap-2">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && send(input)}
            placeholder="Ask JourneyMind AI..."
            className="flex-1 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900 px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 text-slate-900 dark:text-white"
          />
          <button onClick={() => mockVoice()} className="p-2.5 rounded-xl bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-600"><Mic size={18} /></button>
          <button onClick={() => send(input)} disabled={!input.trim()} className="p-2.5 rounded-xl bg-brand-600 text-white hover:bg-brand-700 disabled:opacity-60"><Send size={18} /></button>
        </div>
      </div>
    </div>
  )
}

// ---------------------------------------------------------------------------
// Main app
// ---------------------------------------------------------------------------
function App() {
  const [dark, setDark] = useState(false)
  const [data, setData] = useState<DashboardData | null>(null)
  const [loading, setLoading] = useState(true)
  const [rebooking, setRebooking] = useState<string | null>(null)
  const [toasts, setToasts] = useState<Toast[]>([])

  useEffect(() => {
    if (dark) document.documentElement.classList.add('dark')
    else document.documentElement.classList.remove('dark')
  }, [dark])

  async function loadDashboard() {
    try {
      const res = await fetch('/api/dashboard')
      const json = await res.json()
      setData(json)
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { loadDashboard() }, [])

  useInterval(() => { loadDashboard() }, 60000)

  async function handleRebook(id: string) {
    setRebooking(id)
    try {
      const res = await fetch('/api/rebook', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ option_id: id }),
      })
      const json = await res.json()
      if (json.success) {
        showToast(json.message, 'success')
        await loadDashboard()
      } else {
        showToast(json.message || 'Rebooking failed', 'error')
      }
    } catch {
      showToast('Rebooking failed', 'error')
    } finally {
      setRebooking(null)
    }
  }

  function showToast(message: string, type: 'success' | 'info' | 'error' = 'info') {
    const id = Math.random().toString(36).slice(2)
    setToasts((prev) => [...prev, { id, message, type }])
    setTimeout(() => setToasts((prev) => prev.filter((t) => t.id !== id)), 4000)
  }

  const unread = useMemo(() => (data?.alerts || []).filter((a) => !a.read).length, [data])

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 transition-colors">
      <Header dark={dark} toggleDark={() => setDark((d) => !d)} unread={unread} />

      <main className="max-w-7xl mx-auto px-4 sm:px-6 py-6">
        {loading || !data ? (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            <div className="lg:col-span-8 space-y-6">
              <SkeletonCard className="h-64" />
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <SkeletonCard className="h-56" />
                <SkeletonCard className="h-56" />
              </div>
              <SkeletonCard className="h-64" />
            </div>
            <div className="lg:col-span-4">
              <SkeletonCard className="h-[36rem]" />
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Left column */}
            <div className="lg:col-span-8 space-y-6">
              <FlightCard flight={data.current_journey || data.flight} />

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <ProactivePanel insights={data.proactive_insights} />
                <Timeline items={data.timeline} />
              </div>

              <AirportMap points={data.map_points} />

              <RebookingPanel alternatives={data.alternatives} onRebook={handleRebook} loading={rebooking} />

              <Recommendations recommendations={data.recommendations} />

              <Services services={data.services} />

              <AgentPanel actions={data.agent_actions} />
            </div>

            {/* Right column */}
            <div className="lg:col-span-4 space-y-6 order-first lg:order-last">
              <CopilotChat flight={data.current_journey || data.flight} onShowToast={showToast} />
              <PassengerCard traveler={data.traveler} flight={data.current_journey || data.flight} />
              <WeatherCard origin={data.weather.origin} destination={data.weather.destination} />
              <AlertsPanel alerts={data.alerts} />
            </div>
          </div>
        )}
      </main>

      <ToastContainer toasts={toasts} remove={(id) => setToasts((t) => t.filter((x) => x.id !== id))} />
    </div>
  )
}

export default App
