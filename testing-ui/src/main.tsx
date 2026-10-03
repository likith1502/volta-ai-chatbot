import React from 'react'
import ReactDOM from 'react-dom/client'
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { OriginalApp } from './App'
import { CustomerChatbot } from './customer/CustomerChatbot'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter>
      <Routes>
        {/* Public customer-facing chatbot — default route */}
        <Route path="/" element={<CustomerChatbot />} />

        {/*
          Admin Console — the existing full-featured developer console.
          NOTE: This application does not currently implement authentication.
          The /admin route is NOT protected by an authentication gate.
          Anyone who knows the URL can access it.
          This is a known limitation documented in the final report.
          Do not rely on URL obscurity as security.
        */}
        <Route path="/admin" element={<OriginalApp />} />

        {/* Redirect any unknown paths to the chatbot */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  </React.StrictMode>,
)
