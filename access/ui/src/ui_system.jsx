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
  Badge,
  Container
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
            <Route index element={<Dashboard />} />
            <Route path="expectations" element={<ExpectationsTab />} />
            <Route path="generations" element={<GenerationsTab />} />
            <Route path="validations" element={<ValidationsTab />} />
            <Route path="settings" element={<SettingsTab />} />
            <Route path="docs" element={<DocumentationTab />} />
          </Route>
          
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </AuthProvider>
    </ChakraProvider>
  );
}

function ExpectationsTab() {
  return (
    <Box>
      <Heading size="md" mb={6}>Expectations</Heading>
      <Text>Expectations interface would be implemented here</Text>
    </Box>
  );
}

function GenerationsTab() {
  return (
    <Box>
      <Heading size="md" mb={6}>Generations</Heading>
      <Text>Generations interface would be implemented here</Text>
    </Box>
  );
}

function ValidationsTab() {
  return (
    <Box>
      <Heading size="md" mb={6}>Validations</Heading>
      <Text>Validations interface would be implemented here</Text>
    </Box>
  );
}

function DocumentationTab() {
  return (
    <Box>
      <Heading size="md" mb={6}>Documentation</Heading>
      <Text>Documentation interface would be implemented here</Text>
    </Box>
  );
}

function Header() {
  return (
    <Box bg="blue.600" color="white" py={4} px={8} shadow="md">
      <Flex maxW="1200px" mx="auto" justify="space-between" align="center">
        <Heading size="lg">Expeta 2.0</Heading>
        <Text>Semantic-Driven Software Development</Text>
      </Flex>
    </Box>
  );
}

function Footer() {
  return (
    <Box bg="gray.100" color="gray.600" py={4} px={8} mt={8}>
      <Flex maxW="1200px" mx="auto" justify="space-between" align="center">
        <Text fontSize="sm">© 2025 Expeta 2.0</Text>
        <Text fontSize="sm">Version 0.1.0</Text>
      </Flex>
    </Box>
  );
}

function Dashboard() {
  const [stats, setStats] = useState({
    requirements: 0,
    expectations: 0,
    generations: 0,
    validations: 0
  });
  
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    setTimeout(() => {
      setStats({
        requirements: 12,
        expectations: 28,
        generations: 15,
        validations: 10
      });
      setLoading(false);
    }, 1000);
  }, []);
  
  if (loading) {
    return (
      <Box textAlign="center" py={10}>
        <Spinner size="xl" />
        <Text mt={4}>Loading dashboard...</Text>
      </Box>
    );
  }
  
  return (
    <Box>
      <Heading size="md" mb={6}>Dashboard</Heading>
      
      <Flex mb={8} gap={4} flexWrap="wrap">
        <StatCard title="Requirements" value={stats.requirements} color="blue" />
        <StatCard title="Expectations" value={stats.expectations} color="green" />
        <StatCard title="Generations" value={stats.generations} color="purple" />
        <StatCard title="Validations" value={stats.validations} color="orange" />
      </Flex>
    </Box>
  );
}

function StatCard({ title, value, color }) {
  return (
    <Box 
      bg="white" 
      p={6} 
      borderRadius="md" 
      shadow="md" 
      flex="1"
      minW={{ base: "100%", sm: "200px" }}
    >
      <Flex justify="space-between" align="center">
        <Box>
          <Text color="gray.500">{title}</Text>
          <Text fontSize="3xl" fontWeight="bold">{value}</Text>
        </Box>
        <Box color={`${color}.500`} />
      </Flex>
    </Box>
  );
}

function ProcessTab() {
  const [requirement, setRequirement] = useState('');
  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState(null);
  const toast = useToast();
  
  const handleProcess = async () => {
    if (!requirement.trim()) {
      toast({
        title: 'Error',
        description: 'Please enter a requirement',
        status: 'error',
        duration: 3000,
        isClosable: true
      });
      return;
    }
    
    setProcessing(true);
    setError(null);
    
    try {
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      toast({
        title: 'Success',
        description: 'Requirement processed successfully',
        status: 'success',
        duration: 3000,
        isClosable: true
      });
    } catch (err) {
      setError(err.message || 'An error occurred while processing the requirement');
      
      toast({
        title: 'Error',
        description: err.message || 'An error occurred while processing the requirement',
        status: 'error',
        duration: 5000,
        isClosable: true
      });
    } finally {
      setProcessing(false);
    }
  };
  
  return (
    <Box>
      <Heading size="md" mb={6}>Process Requirement</Heading>
      
      <Box bg="white" p={6} borderRadius="md" shadow="md" mb={6}>
        <Text mb={2}>Enter your requirement:</Text>
        <Textarea
          value={requirement}
          onChange={(e) => setRequirement(e.target.value)}
          placeholder="Describe what you want to build..."
          size="lg"
          rows={5}
          mb={4}
        />
        <Button
          colorScheme="blue"
          onClick={handleProcess}
          isLoading={processing}
          loadingText="Processing"
        >
          Process Requirement
        </Button>
      </Box>
      
      {error && (
        <Alert status="error" mb={6}>
          <AlertIcon />
          {error}
        </Alert>
      )}
    </Box>
  );
}

function ClarifyTab() {
  const [requirement, setRequirement] = useState('');
  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState(null);
  const toast = useToast();
  
  const handleClarify = async () => {
    if (!requirement.trim()) {
      toast({
        title: 'Error',
        description: 'Please enter a requirement',
        status: 'error',
        duration: 3000,
        isClosable: true
      });
      return;
    }
    
    setProcessing(true);
    setError(null);
    
    try {
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      toast({
        title: 'Success',
        description: 'Requirement clarified successfully',
        status: 'success',
        duration: 3000,
        isClosable: true
      });
    } catch (err) {
      setError(err.message || 'An error occurred while clarifying the requirement');
      
      toast({
        title: 'Error',
        description: err.message || 'An error occurred while clarifying the requirement',
        status: 'error',
        duration: 5000,
        isClosable: true
      });
    } finally {
      setProcessing(false);
    }
  };
  
  return (
    <Box>
      <Heading size="md" mb={6}>Clarify Requirement</Heading>
      
      <Box bg="white" p={6} borderRadius="md" shadow="md" mb={6}>
        <Text mb={2}>Enter your requirement:</Text>
        <Textarea
          value={requirement}
          onChange={(e) => setRequirement(e.target.value)}
          placeholder="Describe what you want to build..."
          size="lg"
          rows={5}
          mb={4}
        />
        <Button
          colorScheme="green"
          onClick={handleClarify}
          isLoading={processing}
          loadingText="Clarifying"
        >
          Clarify Requirement
        </Button>
      </Box>
      
      {error && (
        <Alert status="error" mb={6}>
          <AlertIcon />
          {error}
        </Alert>
      )}
    </Box>
  );
}

function GenerateTab() {
  const [expectationId, setExpectationId] = useState('');
  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState(null);
  const toast = useToast();
  
  const handleGenerate = async () => {
    if (!expectationId.trim()) {
      toast({
        title: 'Error',
        description: 'Please enter an expectation ID',
        status: 'error',
        duration: 3000,
        isClosable: true
      });
      return;
    }
    
    setProcessing(true);
    setError(null);
    
    try {
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      toast({
        title: 'Success',
        description: 'Code generated successfully',
        status: 'success',
        duration: 3000,
        isClosable: true
      });
    } catch (err) {
      setError(err.message || 'An error occurred while generating code');
      
      toast({
        title: 'Error',
        description: err.message || 'An error occurred while generating code',
        status: 'error',
        duration: 5000,
        isClosable: true
      });
    } finally {
      setProcessing(false);
    }
  };
  
  return (
    <Box>
      <Heading size="md" mb={6}>Generate Code</Heading>
      
      <Box bg="white" p={6} borderRadius="md" shadow="md" mb={6}>
        <Text mb={2}>Enter expectation ID:</Text>
        <Input
          value={expectationId}
          onChange={(e) => setExpectationId(e.target.value)}
          placeholder="e.g., exp-12345678"
          mb={4}
        />
        
        <Button
          colorScheme="purple"
          onClick={handleGenerate}
          isLoading={processing}
          loadingText="Generating"
        >
          Generate Code
        </Button>
      </Box>
      
      {error && (
        <Alert status="error" mb={6}>
          <AlertIcon />
          {error}
        </Alert>
      )}
    </Box>
  );
}

function ValidateTab() {
  return (
    <Box>
      <Heading size="md" mb={6}>Validate Code</Heading>
      <Text>Validation interface would be implemented here</Text>
    </Box>
  );
}

function SettingsTab() {
  return (
    <Box>
      <Heading size="md" mb={6}>Settings</Heading>
      <Text>Settings interface would be implemented here</Text>
    </Box>
  );
}

export default App;
