import React, { createContext, useContext, useState, useEffect } from 'react';

const PortfolioContext = createContext();

export const usePortfolio = () => {
  const context = useContext(PortfolioContext);
  if (!context) {
    throw new Error('usePortfolio must be used within a PortfolioProvider');
  }
  return context;
};

export const PortfolioProvider = ({ children }) => {
  const [portfolio, setPortfolio] = useState({
    totalValue: 0,
    totalChange: 0,
    totalChangePercent: 0,
    holdings: []
  });

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  // Mock portfolio data
  useEffect(() => {
    const mockHoldings = [
      {
        id: 1,
        symbol: 'BTC',
        name: 'Bitcoin',
        amount: 0.5,
        currentPrice: 42000,
        averagePrice: 38000,
        change24h: 2.5,
        logo: '₿'
      },
      {
        id: 2,
        symbol: 'ETH',
        name: 'Ethereum',
        amount: 5.2,
        currentPrice: 2800,
        averagePrice: 2600,
        change24h: -1.2,
        logo: 'Ξ'
      },
      {
        id: 3,
        symbol: 'ADA',
        name: 'Cardano',
        amount: 1000,
        currentPrice: 0.85,
        averagePrice: 0.75,
        change24h: 5.8,
        logo: '₳'
      }
    ];

    const totalValue = mockHoldings.reduce((sum, holding) => 
      sum + (holding.amount * holding.currentPrice), 0);

    const totalCost = mockHoldings.reduce((sum, holding) => 
      sum + (holding.amount * holding.averagePrice), 0);

    const totalChange = totalValue - totalCost;
    const totalChangePercent = ((totalChange / totalCost) * 100);

    setPortfolio({
      totalValue,
      totalChange,
      totalChangePercent,
      holdings: mockHoldings
    });
  }, []);

  const addHolding = (holding) => {
    setPortfolio(prev => ({
      ...prev,
      holdings: [...prev.holdings, { ...holding, id: Date.now() }]
    }));
  };

  const updateHolding = (id, updates) => {
    setPortfolio(prev => ({
      ...prev,
      holdings: prev.holdings.map(holding =>
        holding.id === id ? { ...holding, ...updates } : holding
      )
    }));
  };

  const removeHolding = (id) => {
    setPortfolio(prev => ({
      ...prev,
      holdings: prev.holdings.filter(holding => holding.id !== id)
    }));
  };

  const value = {
    portfolio,
    isLoading,
    error,
    addHolding,
    updateHolding,
    removeHolding
  };

  return (
    <PortfolioContext.Provider value={value}>
      {children}
    </PortfolioContext.Provider>
  );
};