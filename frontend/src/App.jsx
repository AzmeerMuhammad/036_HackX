import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './contexts/AuthContext'
import AuthGuard from './components/AuthGuard'
import Landing from './pages/Landing'
import Login from './pages/Login'
import Register from './pages/Register'
import ProfessionalRegister from './pages/ProfessionalRegister'
import Home from './pages/Home'
import JournalNew from './pages/JournalNew'
import JournalHistory from './pages/JournalHistory'
import Insights from './pages/Insights'
import Chat from './pages/Chat'
import Professionals from './pages/Professionals'
import ProfessionalDashboard from './pages/ProfessionalDashboard'
import HistoryShare from './pages/HistoryShare'

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/professional/register" element={<ProfessionalRegister />} />
          <Route path="/home" element={<AuthGuard><Home /></AuthGuard>} />
          <Route path="/journal/new" element={<AuthGuard><JournalNew /></AuthGuard>} />
          <Route path="/journal/history" element={<AuthGuard><JournalHistory /></AuthGuard>} />
          <Route path="/insights" element={<AuthGuard><Insights /></AuthGuard>} />
          <Route path="/chat" element={<AuthGuard><Chat /></AuthGuard>} />
          <Route path="/professionals" element={<AuthGuard><Professionals /></AuthGuard>} />
          <Route path="/professional/dashboard" element={<AuthGuard><ProfessionalDashboard /></AuthGuard>} />
          <Route path="/history/share" element={<AuthGuard><HistoryShare /></AuthGuard>} />
        </Routes>
      </Router>
    </AuthProvider>
  )
}

export default App

