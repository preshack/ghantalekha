import { useEffect, useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { PinPad } from './components/PinPad'
import { AlertCircle, CheckCircle2, Factory, History, Timer, Users, XCircle, LogOut, ArrowRight, ShieldCheck } from 'lucide-react'

// Types based on backend responses
interface ClockSuccess {
  status: 'ok'
  action: 'clock_in' | 'clock_out'
  employee: string
  time: string
}

interface ApprovalRequired {
  status: 'approval_required'
  employee: { id: number; name: string }
  active_record: {
    id: number
    employee_id: number
    employee_name: string
    clock_in: string
  }
}

type ApiResponse = ClockSuccess | ApprovalRequired | { error: string }

export default function App() {
  const [now, setNow] = useState(new Date())
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | undefined>()
  const [success, setSuccess] = useState<ClockSuccess | undefined>()
  const [approval, setApproval] = useState<ApprovalRequired | undefined>()
  
  // Update time
  useEffect(() => {
    const timer = setInterval(() => setNow(new Date()), 1000)
    return () => clearInterval(timer)
  }, [])

  // Auto-clear success message
  useEffect(() => {
    if (success) {
      const timer = setTimeout(() => {
        setSuccess(undefined)
      }, 5000)
      return () => clearTimeout(timer)
    }
  }, [success])

  const handleClock = async (pin: string) => {
    setLoading(true)
    setError(undefined)
    
    try {
      const res = await fetch('/clock', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({ pin })
      })
      
      const data = await res.json()
      
      if (!res.ok) {
        throw new Error(data.error || 'Request failed')
      }
      
      if (data.status === 'approval_required') {
        setApproval(data)
      } else if (data.status === 'ok') {
        setSuccess(data)
      }
    } catch (err: any) {
      setError(err.message || 'Connection error')
      // Clear error after 3s
      setTimeout(() => setError(undefined), 3000)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-slate-900 text-white selection:bg-teal-500/30 overflow-hidden font-sans flex flex-col relative">
      
      {/* Dynamic Background */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-[20%] -left-[10%] w-[70vw] h-[70vw] rounded-full bg-blue-600/10 blur-3xl animate-pulse" />
        <div className="absolute top-[40%] -right-[10%] w-[60vw] h-[60vw] rounded-full bg-teal-600/10 blur-3xl animate-pulse delay-1000" />
      </div>

      {/* Header */}
      <header className="relative z-10 px-8 py-6 flex justify-between items-center border-b border-white/5 backdrop-blur-md bg-slate-900/50">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-gradient-to-br from-teal-400 to-blue-500 rounded-lg shadow-lg shadow-teal-500/20">
            <Factory className="text-white w-6 h-6" />
          </div>
          <div>
            <h1 className="text-lg font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-teal-200 to-blue-200">
              Ghanta Haan
            </h1>
            <p className="text-xs text-slate-400 font-medium tracking-wide uppercase">Employee Kiosk</p>
          </div>
        </div>

        <div className="text-right">
          <div className="text-3xl font-bold font-mono tracking-tight text-white drop-shadow-sm">
            {now.toLocaleTimeString('en-US', { hour12: true, hour: '2-digit', minute: '2-digit' })}
          </div>
          <div className="text-sm font-medium text-slate-400">
            {now.toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 relative z-10 flex items-center justify-center p-4">
        <AnimatePresence mode="wait">
          
          {success ? (
            <SuccessView key="success" data={success} onDismiss={() => setSuccess(undefined)} />
          ) : approval ? (
            <ApprovalView 
              key="approval" 
              data={approval} 
              onCancel={() => setApproval(undefined)}
              onSuccess={(msg) => {
                setApproval(undefined)
                // We fake a success message for now, or could re-fetch status
                setSuccess({ status: 'ok', action: 'clock_in', employee: approval.employee.name, time: 'Now' }) 
              }}
            />
          ) : (
            <motion.div
              key="clock"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 1.05 }}
              transition={{ duration: 0.3 }}
              className="w-full max-w-sm"
            >
              <div className="text-center mb-8">
                <h2 className="text-2xl font-semibold text-slate-100 mb-2">Enter Your PIN</h2>
                <p className="text-slate-400 text-sm">Use your unique 4-digit code to clock in or out.</p>
              </div>

              <PinPad 
                length={4}
                onSubmit={handleClock}
                loading={loading}
                error={error}
              />
            </motion.div>
          )}

        </AnimatePresence>
      </main>

      {/* Footer */}
      <footer className="relative z-10 py-4 text-center text-xs text-slate-500 border-t border-white/5 bg-slate-900/80 backdrop-blur-sm">
        <p>&copy; {now.getFullYear()} Ghanta Haan System. Secure Connection.</p>
      </footer>
    </div>
  )
}

// --- Sub Components ---

function SuccessView({ data, onDismiss }: { data: ClockSuccess; onDismiss: () => void }) {
  const isClockIn = data.action === 'clock_in'
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="max-w-md w-full text-center"
      onClick={onDismiss}
    >
      <div className={`mx-auto w-24 h-24 rounded-full flex items-center justify-center mb-6 shadow-2xl ${
        isClockIn ? 'bg-gradient-to-br from-green-400 to-emerald-600 shadow-emerald-500/30' : 'bg-gradient-to-br from-orange-400 to-red-600 shadow-orange-500/30'
      }`}>
        <CheckCircle2 className="w-12 h-12 text-white" />
      </div>
      
      <h2 className="text-3xl font-bold text-white mb-2">
        {isClockIn ? 'Hello,' : 'Goodbye,'} <span className={isClockIn ? "text-emerald-400" : "text-orange-400"}>{data.employee}</span>
      </h2>
      
      <div className="bg-white/5 rounded-2xl p-6 mt-8 border border-white/10 backdrop-blur-md">
        <div className="text-sm text-slate-400 uppercase tracking-widest font-semibold mb-1">
          {isClockIn ? 'Clock In Recorded' : 'Clock Out Recorded'}
        </div>
        <div className="text-4xl font-mono text-white font-medium">
          {data.time}
        </div>
      </div>

      <p className="mt-8 text-slate-500 text-sm animate-pulse">Redirecting in a few seconds...</p>
    </motion.div>
  )
}

function ApprovalView({ data, onCancel, onSuccess }: { 
  data: ApprovalRequired
  onCancel: () => void
  onSuccess: (msg: string) => void
}) {
  const [step, setStep] = useState<'decision' | 'approve'>('decision')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | undefined>()
  const [reason, setReason] = useState('')

  const handleForceClockout = async () => {
    setLoading(true)
    setError(undefined)
    try {
      const res = await fetch('/force_clockout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
        body: JSON.stringify({ active_record_id: data.active_record.id })
      })
      if (!res.ok) throw new Error('Failed to force clock out')
      onSuccess('Forced clock out successful')
    } catch (e) {
      setError('Failed to clock out user.')
    } finally {
      setLoading(false)
    }
  }

  const handleApprove = async (pin: string) => {
    if (!reason.trim()) {
      setError('Please enter a reason first')
      return; // Stop PinPad submission
    }
    // We don't await here directly inside PinPad callback if we want to handle loading state slightly differently, 
    // but PinPad expects a promise to show loading state.
    
    // We will return the promise of the fetch
    const p = (async () => {
        const res = await fetch('/approve_shift', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
            body: JSON.stringify({
                approver_id: data.active_record.employee_id, // The person currently clocked in must approve
                new_employee_id: data.employee.id,
                approver_pin: pin,
                reason: reason
            })
        })
        const d = await res.json()
        if(!res.ok) throw new Error(d.error || 'Approval failed')
        onSuccess('Dual shift started')
    })()
    return p;
  }

  if (step === 'decision') {
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        className="w-full max-w-lg bg-slate-800/90 border border-yellow-600/30 p-8 rounded-3xl shadow-2xl backdrop-blur-xl"
      >
        <div className="flex items-center gap-4 mb-6 text-yellow-500">
          <AlertCircle className="w-10 h-10" />
          <h2 className="text-2xl font-bold text-white">Approval Required</h2>
        </div>
        
        <p className="text-slate-300 text-lg mb-4">
          <strong className="text-white font-semibold">{data.active_record.employee_name}</strong> is currently clocked in.
        </p>
        <p className="text-slate-400 text-sm mb-8">
          To start your shift, they must approve a dual shift, or you can clock them out.
        </p>
      
        <div className="grid gap-3">
          <button 
            onClick={() => setStep('approve')}
            className="w-full py-4 bg-yellow-600 hover:bg-yellow-500 text-white rounded-xl font-bold flex items-center justify-center gap-2 transition-all"
          >
            <ShieldCheck className="w-5 h-5" />
            Approve Dual Shift
          </button>
          
          <button 
            onClick={handleForceClockout}
            disabled={loading}
            className="w-full py-4 bg-slate-700 hover:bg-red-900/50 hover:text-red-200 text-slate-300 rounded-xl font-semibold flex items-center justify-center gap-2 transition-all"
          >
            <LogOut className="w-5 h-5" />
            {loading ? 'Processing...' : `Clock Them Out (${data.active_record.employee_name})`}
          </button>
          
          <button 
            onClick={onCancel}
            className="mt-2 text-slate-500 hover:text-white text-sm font-medium p-2"
          >
            Cancel
          </button>
        </div>
        
        {error && (
            <div className="mt-4 p-3 bg-red-900/50 border border-red-500/20 text-red-200 rounded-lg text-sm text-center">
                {error}
            </div>
        )}
      </motion.div>
    )
  }

  // Approval Step
  return (
    <motion.div
       initial={{ opacity: 0, x: 20 }}
       animate={{ opacity: 1, x: 0 }}
       className="w-full max-w-md"
    >
        <button onClick={() => setStep('decision')} className="text-slate-400 hover:text-white mb-4 flex items-center gap-2 text-sm">
            <ArrowRight className="w-4 h-4 rotate-180" /> Back
        </button>

        <h3 className="text-xl font-bold text-white mb-2">Dual Shift Approval</h3>
        <p className="text-slate-400 text-sm mb-6">Enter PIN for <strong>{data.active_record.employee_name}</strong> to approve.</p>

        <div className="mb-6">
            <label className="block text-xs uppercase text-slate-500 font-bold tracking-wider mb-2">Reason</label>
            <textarea 
                value={reason}
                onChange={(e) => setReason(e.target.value)}
                placeholder="Why are two shifts overlapping?"
                className="w-full bg-slate-800 border-slate-700 rounded-xl px-4 py-3 text-white focus:ring-2 focus:ring-teal-500 outline-none resize-none h-24"
            />
        </div>

        <PinPad 
            label="Approver PIN"
            loading={loading}
            error={error}
            onSubmit={handleApprove}
        />
    </motion.div>
  )
}
