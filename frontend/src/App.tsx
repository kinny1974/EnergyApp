import React from 'react'
import EnergyDashboard from './components/EnergyDashboard'
import EnergyChatbot from './components/EnergyChatbot'

function App() {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-800">
      <EnergyDashboard />
      <EnergyChatbot />
    </div>
  )
}

export default App