/**
 * UI System Access Layer for Expeta 2.0
 * 
 * This module provides a web-based user interface for Expeta system with a unified chat interface.
 */

import React, { useState, useEffect, useRef } from 'react';
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
  VStack,
  HStack,
  Avatar,
  IconButton,
  Divider,
  Progress,
  Code,
  Tag,
  Tooltip,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  Accordion,
  AccordionItem,
  AccordionButton,
  AccordionPanel,
  AccordionIcon
} from '@chakra-ui/react';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

function App() {
  return (
    <ChakraProvider>
      <Box minH="100vh" bg="gray.50">
        <Header />
        <Box maxW="1200px" mx="auto" p={4}>
          <UnifiedChatInterface />
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

function UnifiedChatInterface() {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [expectationId, setExpectationId] = useState(null);
  const [generatedFiles, setGeneratedFiles] = useState([]);
  const [tokenUsage, setTokenUsage] = useState(null);
  const [memoryUsage, setMemoryUsage] = useState(null);
  const [availableTokens, setAvailableTokens] = useState(null);
  const [uiState, setUiState] = useState('initial'); // initial, clarifying, confirming, generating, completed, error
  const messagesEndRef = useRef(null);
  const toast = useToast();
  
  useEffect(() => {
    const initSession = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/chat/session`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ 
            user_message: 'Hello',
            session_id: null
          }),
        });
        
        if (!response.ok) {
          throw new Error(`Failed to create session: ${response.statusText}`);
        }
        
        const data = await response.json();
        setSessionId(data.session_id);
        
        if (data.messages && Array.isArray(data.messages)) {
          setMessages(data.messages);
        } else {
          setMessages([
            {
              role: 'assistant',
              content: 'Welcome to Expeta 2.0! I\'m your product manager assistant. How can I help you with your software project today?',
              timestamp: new Date().toISOString()
            }
          ]);
        }
        
        if (data.status) {
          setUiState(data.status);
        }
        
        if (data.token_usage) {
          setTokenUsage(data.token_usage);
        }
      } catch (error) {
        console.error('Error initializing session:', error);
        toast({
          title: 'Connection Error',
          description: 'Failed to connect to the server. Please try again later.',
          status: 'error',
          duration: 5000,
          isClosable: true,
        });
      }
    };
    
    initSession();
  }, [toast]);
  
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);
  
  const handleSendMessage = async () => {
    if (!inputMessage.trim() || !sessionId || isLoading) return;
    
    const userMessage = {
      role: 'user',
      content: inputMessage,
      timestamp: new Date().toISOString()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);
    
    try {
      const response = await fetch(`${API_BASE_URL}/chat/session`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_message: userMessage.content,
          session_id: sessionId
        }),
      });
      
      if (!response.ok) {
        throw new Error(`Failed to send message: ${response.statusText}`);
      }
      
      const data = await response.json();
      
      if (data.ui_state) {
        setUiState(data.ui_state);
      }
      
      if (data.token_usage) {
        setTokenUsage(data.token_usage);
      }
      
      if (data.memory_usage) {
        setMemoryUsage(data.memory_usage);
      }
      
      if (data.available_tokens) {
        setAvailableTokens(data.available_tokens);
      }
      
      if (data.expectation_id) {
        setExpectationId(data.expectation_id);
      }
      
      if (data.files) {
        setGeneratedFiles(data.files);
      }
      
      const assistantMessage = {
        role: 'assistant',
        content: data.response,
        timestamp: new Date().toISOString(),
        expectation: data.expectation,
        files: data.files,
        show_downloads: data.show_downloads
      };
      
      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      
      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          content: 'Sorry, there was an error processing your request. Please try again.',
          timestamp: new Date().toISOString(),
          isError: true
        }
      ]);
      
      toast({
        title: 'Error',
        description: error.message || 'Failed to process your message',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };
  
  const handleDownloadFile = (fileName) => {
    if (!expectationId) return;
    
    const downloadUrl = `${API_BASE_URL}/download/file/${expectationId}/${fileName}`;
    
    const a = document.createElement('a');
    a.href = downloadUrl;
    a.download = fileName;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    
    toast({
      title: 'Download Started',
      description: `Downloading ${fileName}`,
      status: 'info',
      duration: 2000,
      isClosable: true
    });
  };
  
  const handleDownloadAll = () => {
    if (!expectationId) return;
    
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
    if (!expectationId) return;
    
    const downloadUrl = `${API_BASE_URL}/download/expectation/${expectationId}?format=yaml`;
    
    const a = document.createElement('a');
    a.href = downloadUrl;
    a.download = `expectation_${expectationId}.yaml`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    
    toast({
      title: 'Download Started',
      description: 'Downloading expectation YAML',
      status: 'info',
      duration: 2000,
      isClosable: true
    });
  };
  
  return (
    <Box>
      <Flex mb={4} justify="space-between" align="center">
        <Heading size="md">Chat with Expeta</Heading>
        {tokenUsage && (
          <Tooltip label="Token usage statistics">
            <Box>
              <Menu>
                <MenuButton as={Button} size="sm" colorScheme="blue" variant="outline">
                  Token Usage
                </MenuButton>
                <MenuList p={4}>
                  <Heading size="sm" mb={3}>Token Usage</Heading>
                  {Object.entries(tokenUsage).map(([provider, usage]) => (
                    <Stat key={provider} mb={3}>
                      <StatLabel>{provider}</StatLabel>
                      <StatNumber>{usage.total}</StatNumber>
                      <StatHelpText>tokens used</StatHelpText>
                    </Stat>
                  ))}
                  
                  {memoryUsage && (
                    <>
                      <Divider my={3} />
                      <Heading size="sm" mb={3}>Memory Usage</Heading>
                      <Stat mb={2}>
                        <StatLabel>Total</StatLabel>
                        <StatNumber>{memoryUsage.total}</StatNumber>
                        <StatHelpText>tokens in memory</StatHelpText>
                      </Stat>
                      <Progress 
                        value={(memoryUsage.total / 100000) * 100} 
                        colorScheme="blue" 
                        size="sm" 
                        mb={3}
                      />
                      
                      <Text fontSize="sm" mb={1}>Breakdown:</Text>
                      <Text fontSize="sm">Expectations: {memoryUsage.expectations}</Text>
                      <Text fontSize="sm">Generations: {memoryUsage.generations}</Text>
                      <Text fontSize="sm">Validations: {memoryUsage.validations}</Text>
                    </>
                  )}
                  
                  {availableTokens && (
                    <>
                      <Divider my={3} />
                      <Heading size="sm" mb={3}>Available Tokens</Heading>
                      {Object.entries(availableTokens).map(([model, tokens]) => (
                        <Text key={model} fontSize="sm">
                          {model}: {tokens} tokens
                        </Text>
                      ))}
                    </>
                  )}
                </MenuList>
              </Menu>
            </Box>
          </Tooltip>
        )}
      </Flex>
      
      {/* Chat Messages */}
      <Box 
        bg="white" 
        borderRadius="md" 
        shadow="md" 
        height="60vh" 
        overflowY="auto"
        p={4}
        mb={4}
      >
        <VStack spacing={4} align="stretch">
          {messages.map((message, index) => (
            <Box 
              key={index}
              alignSelf={message.role === 'user' ? 'flex-end' : 'flex-start'}
              maxW="80%"
              bg={message.role === 'user' ? 'blue.100' : message.isError ? 'red.100' : 'gray.100'}
              p={3}
              borderRadius="lg"
            >
              <Flex mb={2}>
                <Avatar 
                  size="sm" 
                  name={message.role === 'user' ? 'User' : 'Expeta'} 
                  bg={message.role === 'user' ? 'blue.500' : 'green.500'} 
                  mr={2}
                />
                <Box>
                  <Text fontWeight="bold">
                    {message.role === 'user' ? 'You' : 'Expeta PM'}
                  </Text>
                  <Text fontSize="xs" color="gray.500">
                    {new Date(message.timestamp).toLocaleTimeString()}
                  </Text>
                </Box>
              </Flex>
              
              <Text whiteSpace="pre-wrap">{message.content}</Text>
              
              {/* Show download buttons if this message has files */}
              {message.show_downloads && message.files && message.files.length > 0 && (
                <Box mt={4}>
                  <Text fontWeight="bold" mb={2}>Generated Files:</Text>
                  <Flex wrap="wrap" gap={2}>
                    {message.files.map((file, fileIndex) => (
                      <Button
                        key={fileIndex}
                        size="sm"
                        colorScheme="teal"
                        onClick={() => handleDownloadFile(file.name)}
                        leftIcon={<span>📄</span>}
                      >
                        {file.name}
                      </Button>
                    ))}
                    <Button
                      size="sm"
                      colorScheme="blue"
                      onClick={handleDownloadAll}
                      leftIcon={<span>📦</span>}
                    >
                      Download All (ZIP)
                    </Button>
                    <Button
                      size="sm"
                      colorScheme="purple"
                      onClick={handleDownloadExpectation}
                      leftIcon={<span>📋</span>}
                    >
                      Download Expectation
                    </Button>
                  </Flex>
                </Box>
              )}
              
              {/* Show expectation details if available */}
              {message.expectation && (
                <Box mt={4} p={3} bg="gray.50" borderRadius="md">
                  <Accordion allowToggle>
                    <AccordionItem border="none">
                      <AccordionButton px={0}>
                        <Box flex="1" textAlign="left" fontWeight="bold">
                          Expectation Details
                        </Box>
                        <AccordionIcon />
                      </AccordionButton>
                      <AccordionPanel pb={4}>
                        <Text fontWeight="bold">{message.expectation.name}</Text>
                        <Text>{message.expectation.description}</Text>
                        
                        {message.expectation.acceptance_criteria && (
                          <Box mt={2}>
                            <Text fontWeight="bold">Acceptance Criteria:</Text>
                            <VStack align="start" spacing={1} mt={1}>
                              {message.expectation.acceptance_criteria.map((criterion, i) => (
                                <Text key={i}>• {criterion}</Text>
                              ))}
                            </VStack>
                          </Box>
                        )}
                      </AccordionPanel>
                    </AccordionItem>
                  </Accordion>
                </Box>
              )}
            </Box>
          ))}
          <div ref={messagesEndRef} />
        </VStack>
      </Box>
      
      {/* Generation Status */}
      {uiState === 'generating' && (
        <Box mb={4} p={4} bg="purple.50" borderRadius="md">
          <Flex align="center">
            <Spinner size="sm" mr={3} color="purple.500" />
            <Text>Generating code... This may take a moment.</Text>
          </Flex>
          <Progress size="sm" isIndeterminate colorScheme="purple" mt={2} />
        </Box>
      )}
      
      {/* Input Area */}
      <Flex>
        <Textarea
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type your message here..."
          size="md"
          resize="none"
          mr={2}
          disabled={isLoading}
        />
        <Button
          colorScheme="blue"
          onClick={handleSendMessage}
          isLoading={isLoading}
          loadingText="Sending"
          disabled={!inputMessage.trim() || !sessionId}
        >
          Send
        </Button>
      </Flex>
      
      {/* Status Indicator */}
      <Flex justify="flex-end" mt={2}>
        <Tag size="sm" colorScheme={sessionId ? 'green' : 'red'}>
          {sessionId ? 'Connected' : 'Disconnected'}
        </Tag>
        {uiState !== 'initial' && (
          <Tag size="sm" ml={2} colorScheme={
            uiState === 'clarifying' ? 'blue' :
            uiState === 'confirming' ? 'cyan' :
            uiState === 'generating' ? 'purple' :
            uiState === 'completed' ? 'green' :
            uiState === 'error' ? 'red' : 'gray'
          }>
            {uiState.charAt(0).toUpperCase() + uiState.slice(1)}
          </Tag>
        )}
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
