import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Navbar from './components/Layout/Navbar'
import HeroSection from './components/Home/HeroSection'
import ChatScene from './components/LegalQA/ChatScene'
import MapScene from './components/Matching/MapScene'
import ManifestScene from './components/Manifest/ManifestScene'

export default function App() {
  return (
    <BrowserRouter>
      <Navbar />
      <main style={{ paddingTop: 'var(--nav-h)' }}>
        <Routes>
          <Route path="/"          element={<HeroSection />} />
          <Route path="/chat"      element={<ChatScene />} />
          <Route path="/map"       element={<MapScene />} />
          <Route path="/manifest"  element={<ManifestScene />} />
          <Route path="*"          element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </BrowserRouter>
  )
}
