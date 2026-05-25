import React from 'react'
import { Link, Outlet } from 'react-router-dom'

export default function Layout(){
  return (
    <div className="min-h-screen flex">
      <aside className="w-64 bg-gray-800 text-white p-4">
        <h3 className="text-lg font-bold mb-4">DefectIQ</h3>
        <nav className="flex flex-col gap-2">
          <Link to="/" className="hover:underline">Dashboard</Link>
          <Link to="/explorer" className="hover:underline">Defect Explorer</Link>
          <Link to="/insights" className="hover:underline">AI Insights</Link>
          <Link to="/predictions" className="hover:underline">Predictions</Link>
          <Link to="/similar" className="hover:underline">Similar Defects</Link>
          <Link to="/chat" className="hover:underline">Chat Assistant</Link>
          <Link to="/settings" className="hover:underline">Settings</Link>
        </nav>
      </aside>
      <main className="flex-1 p-6 bg-gray-50">
        <Outlet />
      </main>
    </div>
  )
}
