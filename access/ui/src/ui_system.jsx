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
  const [generatedFiles, setGeneratedFiles] = useState([]);
  const [expectation, setExpectation] = useState(null);
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
    setGeneratedFiles([]);
    setExpectation(null);
    
    try {
      const expectationResponse = await fetch(`${API_BASE_URL}/memory/expectations/${expectationId}`);
      
      if (!expectationResponse.ok) {
        throw new Error(`Failed to fetch expectation: ${expectationResponse.statusText}`);
      }
      
      const expectationData = await expectationResponse.json();
      
      let generationData;
      const generationResponse = await fetch(`${API_BASE_URL}/memory/generations/${expectationId}`);
      
      if (generationResponse.ok) {
        generationData = await generationResponse.json();
      } else {
        const generateResponse = await fetch(`${API_BASE_URL}/generate`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(expectationData),
        });
        
        if (!generateResponse.ok) {
          throw new Error(`Failed to generate code: ${generateResponse.statusText}`);
        }
        
        generationData = await generateResponse.json();
      }
      
      const data = {
        success: true,
        expectation: expectationData,
        generated_code: generationData
      };
      
      setExpectation(data.expectation);
      setGeneratedFiles(data.generated_code.files);
      
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
  
  const handleDownloadFile = (file) => {
    const downloadUrl = `${API_BASE_URL}/download/file/${expectationId}/${file.name}`;
    
    const a = document.createElement('a');
    a.href = downloadUrl;
    a.download = file.name;
    document.body.appendChild(a);
    a.click();
    
    document.body.removeChild(a);
    
    toast({
      title: 'Download Started',
      description: `Downloading ${file.name}`,
      status: 'info',
      duration: 2000,
      isClosable: true
    });
  };
  
  const handleDownloadAll = () => {
    if (!generatedFiles.length) return;
    
    const downloadUrl = `${API_BASE_URL}/download/code/${expectationId}`;
    
    const a = document.createElement('a');
    a.href = downloadUrl;
    a.download = `code_${expectationId}.zip`;
    document.body.appendChild(a);
    a.click();
    
    document.body.removeChild(a);
    
    toast({
      title: 'Download Started',
      description: 'Downloading all files as ZIP',
      status: 'info',
      duration: 2000,
      isClosable: true
    });
  };
  
  const handleDownloadExpectation = () => {
    if (!expectation) return;
    
    const downloadUrl = `${API_BASE_URL}/download/expectation/${expectationId}?format=yaml`;
    
    const a = document.createElement('a');
    a.href = downloadUrl;
    a.download = `expectation_${expectationId}.yaml`;
    document.body.appendChild(a);
    a.click();
    
    document.body.removeChild(a);
    
    toast({
      title: 'Download Started',
      description: `Downloading expectation YAML`,
      status: 'info',
      duration: 2000,
      isClosable: true
    });
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
          mr={4}
        >
          Generate Code
        </Button>
        
        {generatedFiles.length > 0 && (
          <Button
            colorScheme="teal"
            onClick={handleDownloadAll}
            ml={2}
          >
            Download All Files
          </Button>
        )}
        
        {expectation && (
          <Button
            colorScheme="blue"
            onClick={handleDownloadExpectation}
            ml={2}
          >
            Download Expectation
          </Button>
        )}
      </Box>
      
      {error && (
        <Alert status="error" mb={6}>
          <AlertIcon />
          {error}
        </Alert>
      )}
      
      {expectation && (
        <Box bg="white" p={6} borderRadius="md" shadow="md" mb={6}>
          <Heading size="sm" mb={3}>Expectation: {expectation.name}</Heading>
          <Text mb={2}>{expectation.description}</Text>
          
          <Text fontWeight="bold" mt={4} mb={2}>Acceptance Criteria:</Text>
          {expectation.acceptance_criteria.map((criterion, index) => (
            <Text key={index} ml={4}>• {criterion}</Text>
          ))}
        </Box>
      )}
      
      {generatedFiles.length > 0 && (
        <Box bg="white" p={6} borderRadius="md" shadow="md">
          <Heading size="sm" mb={4}>Generated Files</Heading>
          
          {generatedFiles.map((file, index) => (
            <Box 
              key={index} 
              p={4} 
              borderWidth="1px" 
              borderRadius="md" 
              mb={4}
            >
              <Flex justify="space-between" align="center" mb={2}>
                <Text fontWeight="bold">{file.name}</Text>
                <Button
                  size="sm"
                  colorScheme="teal"
                  onClick={() => handleDownloadFile(file)}
                >
                  Download
                </Button>
              </Flex>
              
              <Box
                bg="gray.50"
                p={3}
                borderRadius="md"
                fontFamily="monospace"
                fontSize="sm"
                whiteSpace="pre-wrap"
                overflowX="auto"
              >
                {file.content}
              </Box>
            </Box>
          ))}
        </Box>
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
