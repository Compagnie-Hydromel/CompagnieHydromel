import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import App from './App.tsx'
import './index.css'
import { Images } from './assets/index';

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <div
      className="bg-black text-white"
      style={{ backgroundImage: 'url(' + Images.TAVERNE + ')', backgroundSize: 'cover', backgroundPosition: 'center', backgroundAttachment: 'fixed' }}
    >
      <App />
    </div>
  </StrictMode>,
)
