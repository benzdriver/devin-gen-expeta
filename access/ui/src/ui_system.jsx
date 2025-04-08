/**
 * UI System Access Layer for Expeta 2.0
 * 
 * This module provides a web-based user interface for Expeta system.
 */

import React, { useState, useEffect, createContext, useContext } from 'react';
import {
  ChakraProvider,
  Box,
  Flex,
  Heading,
  Text,
  Input,
  Button,
  Textarea,
  Alert,
  AlertIcon,
  Spinner,
  useToast,
  Container,
  Card,
  CardBody,
  CardHeader,
  Stack,
  Divider
} from '@chakra-ui/react';
import { Routes, Route, useLocation, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import { AuthProvider, useAuth } from './context/AuthContext';

import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import NotFoundPage from './pages/NotFoundPage';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

export { AuthProvider, useAuth } from './context/AuthContext';

function ProtectedRoute({ children }) {
  const { currentUser, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="100vh">
        <Spinner size="xl" />
      </Box>
    );
  }

  if (!currentUser) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return children;
}

function App() {
  return (
    <ChakraProvider>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          
          <Route path="/" element={
            <ProtectedRoute>
              <Layout />
            </ProtectedRoute>
          }>
            <Route index element={<ChatInterface />} />
            <Route path="settings" element={<SettingsPage />} />
          </Route>
          
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </AuthProvider>
    </ChakraProvider>
  );
}

function ChatInterface() {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const toast = useToast();
  
  const handleSendMessage = async () => {
    if (!input.trim()) return;
    
    const userMessage = {
      id: Date.now(),
      text: input,
      sender: 'user',
      timestamp: new Date().toISOString()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsProcessing(true);
    
    try {
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      const aiMessage = {
        id: Date.now() + 1,
        text: "I'm analyzing your request. Could you provide more details about what you're trying to build?",
        sender: 'ai',
        timestamp: new Date().toISOString()
      };
      
      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to process your message',
        status: 'error',
        duration: 3000,
        isClosable: true
      });
    } finally {
      setIsProcessing(false);
    }
  };
  
  return (
    <Box height="calc(100vh - 140px)" display="flex" flexDirection="column">
      <Heading size="md" mb={4}>Expeta Clarifier</Heading>
      
      {/* Messages area */}
      <Box 
        flex="1" 
        bg="white" 
        borderRadius="md" 
        shadow="sm" 
        mb={4} 
        overflowY="auto"
        p={4}
      >
        {messages.length === 0 ? (
          <Flex 
            height="100%" 
            alignItems="center" 
            justifyContent="center" 
            flexDirection="column"
            color="gray.500"
          >
            <Text fontSize="lg" mb={2}>Welcome to Expeta 2.0</Text>
            <Text>Start a conversation to clarify your software requirements</Text>
          </Flex>
        ) : (
          <Stack spacing={4}>
            {messages.map(message => (
              <Card 
                key={message.id} 
                bg={message.sender === 'user' ? 'blue.50' : 'white'}
                borderWidth={1}
                borderColor={message.sender === 'user' ? 'blue.200' : 'gray.200'}
                alignSelf={message.sender === 'user' ? 'flex-end' : 'flex-start'}
                maxW="80%"
              >
                <CardBody py={2} px={4}>
                  <Text>{message.text}</Text>
                </CardBody>
              </Card>
            ))}
            {isProcessing && (
              <Flex justify="flex-start">
                <Card bg="white" borderWidth={1} borderColor="gray.200" maxW="80%">
                  <CardBody py={2} px={4} display="flex" alignItems="center">
                    <Spinner size="sm" mr={2} />
                    <Text>Thinking...</Text>
                  </CardBody>
                </Card>
              </Flex>
            )}
          </Stack>
        )}
      </Box>
      
      {/* Input area */}
      <Flex>
        <Textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Describe what you want to build..."
          size="md"
          resize="none"
          mr={2}
          onKeyPress={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault();
              handleSendMessage();
            }
          }}
        />
        <Button
          colorScheme="blue"
          onClick={handleSendMessage}
          isLoading={isProcessing}
          loadingText="Sending"
          alignSelf="flex-end"
        >
          Send
        </Button>
      </Flex>
    </Box>
  );
}

function SettingsPage() {
  return (
    <Box>
      <Heading size="md" mb={6}>Settings</Heading>
      <Card>
        <CardHeader>
          <Heading size="sm">User Settings</Heading>
        </CardHeader>
        <CardBody>
          <Text>Settings interface would be implemented here</Text>
        </CardBody>
      </Card>
    </Box>
  );
}

export default App;
