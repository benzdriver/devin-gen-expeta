/**
 * UI System Access Layer for Expeta 2.0
 * 
 * This module provides a web-based user interface for Expeta system.
 */

import React, { useState, useEffect } from 'react';
import {
  ChakraProvider,
  Box,
  Flex,
  Heading,
  Text,
  Input,
  Button,
  Textarea,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  Alert,
  AlertIcon,
  Spinner,
  useToast,
  Badge
} from '@chakra-ui/react';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

function App() {
  return (
    <ChakraProvider>
      <Box minH="100vh" bg="gray.50">
        <Header />
        <Box maxW="1200px" mx="auto" p={4}>
          <Tabs variant="enclosed" colorScheme="blue">
            <TabList>
              <Tab>Dashboard</Tab>
              <Tab>Process</Tab>
              <Tab>Clarify</Tab>
              <Tab>Generate</Tab>
              <Tab>Validate</Tab>
              <Tab>Settings</Tab>
            </TabList>
            <TabPanels>
              <TabPanel>
                <Dashboard />
              </TabPanel>
              <TabPanel>
                <ProcessTab />
              </TabPanel>
              <TabPanel>
                <ClarifyTab />
              </TabPanel>
              <TabPanel>
                <GenerateTab />
              </TabPanel>
              <TabPanel>
                <ValidateTab />
              </TabPanel>
              <TabPanel>
                <SettingsTab />
              </TabPanel>
            </TabPanels>
          </Tabs>
        </Box>
        <Footer />
      </Box>
    </ChakraProvider>
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
      
      <Flex mb={8} gap={4}>
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
