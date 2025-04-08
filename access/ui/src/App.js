import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ChakraProvider, Box } from '@chakra-ui/react';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ExpetaProvider } from './context/ExpetaContext';

// 导入页面
import {
  Dashboard,
  GenerationsPage,
  LoginPage,
  RegisterPage,
  NotFoundPage,
  ConversationPage
} from './pages';

// 导入布局组件
import Layout from './components/layout/Layout';

// 受保护的路由包装器
const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();
  
  if (loading) {
    return <div>Loading...</div>;
  }
  
  if (!isAuthenticated) {
    return <Navigate to="/login" />;
  }
  
  return children;
};

function App() {
  return (
    <ChakraProvider>
      <AuthProvider>
        <ExpetaProvider>
          <Router>
            <Routes>
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />
              
              <Route 
                path="/" 
                element={
                  <ProtectedRoute>
                    <Layout />
                  </ProtectedRoute>
                }
              >
                <Route index element={<Dashboard />} />
                <Route path="conversation/:conversationId?" element={<ConversationPage />} />
                <Route path="generations/:generationId?" element={<GenerationsPage />} />
              </Route>
              
              <Route path="*" element={<NotFoundPage />} />
            </Routes>
          </Router>
        </ExpetaProvider>
      </AuthProvider>
    </ChakraProvider>
  );
}

export default App; 