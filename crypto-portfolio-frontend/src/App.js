import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import './App.css';

// Import all pages
import HomePage from './pages/HomePage';
import DashboardPage from './pages/DashboardPage';
import PortfolioPage from './pages/PortfolioPage';
import TradingPage from './pages/TradingPage';
import AnalyticsPage from './pages/AnalyticsPage';
import NewsPage from './pages/NewsPage';
import SettingsPage from './pages/SettingsPage';

// Import layout components
import Header from './components/layout/Header';
import Sidebar from './components/layout/Sidebar';
import Footer from './components/layout/Footer';

// Import contexts
import { ThemeProvider } from './components/contexts/ThemeContext';
import { PortfolioProvider } from './components/contexts/PortfolioContext';
import { AuthProvider } from './components/contexts/AuthContext';
import { WebSocketProvider } from './components/contexts/WebSocketContext';
import { SettingsProvider } from './components/settings/context/SettingsContext';

function App() {
  return (
    <AuthProvider>
      <ThemeProvider>
        <WebSocketProvider>
          <PortfolioProvider>
            <SettingsProvider>
              <Router>
              <div className="App min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors duration-300">
                <Header />
                <div className="flex">
                  <Sidebar />
                  <main className="flex-1 min-h-screen pt-16 lg:pl-64">
                    <AnimatePresence mode="wait">
                      <Routes>
                        <Route 
                          path="/" 
                          element={
                            <motion.div
                              initial={{ opacity: 0, y: 20 }}
                              animate={{ opacity: 1, y: 0 }}
                              exit={{ opacity: 0, y: -20 }}
                              transition={{ duration: 0.3 }}
                            >
                              <HomePage />
                            </motion.div>
                          } 
                        />
                        <Route 
                          path="/dashboard" 
                          element={
                            <motion.div
                              initial={{ opacity: 0, y: 20 }}
                              animate={{ opacity: 1, y: 0 }}
                              exit={{ opacity: 0, y: -20 }}
                              transition={{ duration: 0.3 }}
                            >
                              <DashboardPage />
                            </motion.div>
                          } 
                        />
                        <Route 
                          path="/portfolio" 
                          element={
                            <motion.div
                              initial={{ opacity: 0, y: 20 }}
                              animate={{ opacity: 1, y: 0 }}
                              exit={{ opacity: 0, y: -20 }}
                              transition={{ duration: 0.3 }}
                            >
                              <PortfolioPage />
                            </motion.div>
                          } 
                        />
                        <Route 
                          path="/trading" 
                          element={
                            <motion.div
                              initial={{ opacity: 0, y: 20 }}
                              animate={{ opacity: 1, y: 0 }}
                              exit={{ opacity: 0, y: -20 }}
                              transition={{ duration: 0.3 }}
                            >
                              <TradingPage />
                            </motion.div>
                          } 
                        />
                        <Route 
                          path="/analytics" 
                          element={
                            <motion.div
                              initial={{ opacity: 0, y: 20 }}
                              animate={{ opacity: 1, y: 0 }}
                              exit={{ opacity: 0, y: -20 }}
                              transition={{ duration: 0.3 }}
                            >
                              <AnalyticsPage />
                            </motion.div>
                          } 
                        />
                        <Route 
                          path="/news" 
                          element={
                            <motion.div
                              initial={{ opacity: 0, y: 20 }}
                              animate={{ opacity: 1, y: 0 }}
                              exit={{ opacity: 0, y: -20 }}
                              transition={{ duration: 0.3 }}
                            >
                              <NewsPage />
                            </motion.div>
                          } 
                        />
                        <Route 
                          path="/settings" 
                          element={
                            <motion.div
                              initial={{ opacity: 0, y: 20 }}
                              animate={{ opacity: 1, y: 0 }}
                              exit={{ opacity: 0, y: -20 }}
                              transition={{ duration: 0.3 }}
                            >
                              <SettingsPage />
                            </motion.div>
                          } 
                        />
                      </Routes>
                    </AnimatePresence>
                  </main>
                </div>
                <Footer />
                              </div>
              </Router>
            </SettingsProvider>
          </PortfolioProvider>
        </WebSocketProvider>
      </ThemeProvider>
    </AuthProvider>
  );
}

// Add to any component temporarily
// api check
// console.log('API Key exists:', !!process.env.REACT_APP_NEWS_API_KEY);
// console.log('API URL:', process.env.REACT_APP_CRYPTO_NEWS_API_URL);

// Test in browser console or component
// fetch(`https://newsapi.org/v2/everything?q=bitcoin&apiKey=${process.env.REACT_APP_NEWS_API_KEY}`)
//   .then(response => response.json())
//   .then(data => console.log('API Response:', data))
//   .catch(error => console.error('API Error:', error));


export default App;