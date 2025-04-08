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
  Divider,
  Badge,
  List,
  ListItem,
  ListIcon,
  Icon,
  useColorModeValue
} from '@chakra-ui/react';
import { Routes, Route, useLocation, Navigate } from 'react-router-dom';
import { FiCheckCircle, FiAlertCircle, FiInfo } from 'react-icons/fi';
import Layout from './components/Layout';
import { AuthProvider, useAuth } from './context/AuthContext';
import { conversationService, clarifierService } from './services/api';
import { ExpetaProvider } from './context/ExpetaContext';

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
        <ExpetaProvider>
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
        </ExpetaProvider>
      </AuthProvider>
    </ChakraProvider>
  );
}

function ChatInterface() {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [conversationId, setConversationId] = useState(null);
  const [expectationSummary, setExpectationSummary] = useState(null);
  const [showSummary, setShowSummary] = useState(false);
  const toast = useToast();
  
  useEffect(() => {
    const createNewConversation = async () => {
      try {
        const newConversationId = 'conv-' + Date.now();
        setConversationId(newConversationId);
        console.log('Created new conversation:', newConversationId);
        
        const welcomeMessage = {
          id: Date.now(),
          text: "Welcome to Expeta! I'm your AI assistant specialized in software development. Describe what you want to build, and I'll help clarify requirements and generate code for your project.",
          sender: 'ai',
          timestamp: new Date().toISOString()
        };
        
        setMessages([welcomeMessage]);
      } catch (error) {
        console.error('Failed to create conversation:', error);
        toast({
          title: 'Error',
          description: 'Failed to start a new conversation',
          status: 'error',
          duration: 3000,
          isClosable: true
        });
      }
    };
    
    createNewConversation();
  }, [toast]);
  
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
      const userInput = input;
      
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const aiMessage = {
        id: Date.now() + 1,
        text: generateClarifierResponse(userInput),
        sender: 'ai',
        timestamp: new Date().toISOString()
      };
      
      setMessages(prev => [...prev, aiMessage]);
      
      if (messages.length >= 1) {
        setShowSummary(false);
        
        await generateExpectationSummary(userInput);
        
        setShowSummary(true);
      }
    } catch (error) {
      console.error('Error processing message:', error);
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
  
  const generateClarifierResponse = (userInput) => {
    const userInputLower = userInput.toLowerCase();
    
    if (userInputLower.includes('website') || userInputLower.includes('web app') || userInputLower.includes('homepage')) {
      return "I understand you're looking to build a website. Could you tell me more about its purpose and the key features you'd like to include? For example, is this a personal portfolio, a business site, or something else?";
    } else if (userInputLower.includes('app') || userInputLower.includes('mobile')) {
      return "I see you're interested in developing an app. To better understand your requirements, could you share what platform this is for (iOS, Android, or both), and what core functionality you envision?";
    } else if (userInputLower.includes('api') || userInputLower.includes('backend')) {
      return "You're looking to develop an API or backend system. Could you elaborate on what data this API will handle, what endpoints you need, and any specific requirements for authentication or performance?";
    } else {
      return "I'd like to help clarify your software requirements. Could you provide more details about what you're trying to build? What problem are you trying to solve, and who are the intended users?";
    }
  };
  
  const generateExpectationSummary = async (latestInput) => {
    try {
      const response = await clarifierService.clarifyRequirement(latestInput);
      
      if (response && response.data) {
        const { top_level_expectation, sub_expectations } = response.data;
        
        setExpectationSummary({
          ...top_level_expectation,
          sub_expectations: sub_expectations
        });
        
        console.log('Clarification result:', response.data);
      }
    } catch (error) {
      console.error('Error generating expectation summary:', error);
      
      const userInputLower = latestInput.toLowerCase();
      let summary = {
        name: "Software Project",
        description: "Based on our conversation, I understand you need a software solution.",
        acceptance_criteria: [
          "Must solve the core problem described",
          "Should be user-friendly and intuitive"
        ],
        constraints: [
          "Must be completed within reasonable timeframe",
          "Should follow industry best practices"
        ]
      };
      
      if (userInputLower.includes('website') || userInputLower.includes('web app') || userInputLower.includes('homepage')) {
        summary = {
          name: "Website Development",
          description: "A website that serves your specific needs and target audience.",
          acceptance_criteria: [
            "Responsive design that works on mobile and desktop",
            "Clear navigation and user interface",
            "Content management capabilities"
          ],
          constraints: [
            "Must follow web accessibility guidelines",
            "Should load quickly on various devices and connections"
          ]
        };
      } else if (userInputLower.includes('app') || userInputLower.includes('mobile')) {
        summary = {
          name: "Mobile Application",
          description: "A mobile app that delivers value to your users.",
          acceptance_criteria: [
            "Intuitive user interface",
            "Core functionality works offline",
            "Efficient performance on target devices"
          ],
          constraints: [
            "Must comply with app store guidelines",
            "Should minimize battery usage"
          ]
        };
      } else if (userInputLower.includes('api') || userInputLower.includes('backend')) {
        summary = {
          name: "API/Backend System",
          description: "A robust backend system to support your application needs.",
          acceptance_criteria: [
            "Secure authentication and authorization",
            "Well-documented API endpoints",
            "Efficient data processing"
          ],
          constraints: [
            "Must handle expected load",
            "Should implement proper error handling"
          ]
        };
      }
      
      setExpectationSummary(summary);
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
            <Text mb={4}>Start a conversation to clarify your software requirements</Text>
            <Text fontSize="sm" textAlign="center" maxW="500px">
              I'm your AI assistant specialized in software development. Describe what you want to build,
              and I'll help clarify requirements and generate code for your project.
            </Text>
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
            
            {/* Expectation Summary */}
            {expectationSummary && !isProcessing && (
              <Card 
                borderWidth={1}
                borderColor="green.200"
                bg="green.50"
                maxW="100%"
                mt={4}
                boxShadow="md"
              >
                <CardHeader pb={0}>
                  <Flex align="center">
                    <Icon as={FiInfo} color="green.500" mr={2} />
                    <Heading size="sm">AI Understanding Summary</Heading>
                  </Flex>
                </CardHeader>
                <CardBody pt={2}>
                  <Text fontWeight="bold" mb={1} fontSize="lg" color="blue.700">{expectationSummary.name}</Text>
                  <Text mb={3}>{expectationSummary.description}</Text>
                  
                  <Text fontWeight="bold" fontSize="sm" mb={1}>Acceptance Criteria:</Text>
                  <List spacing={1} mb={3}>
                    {expectationSummary.acceptance_criteria && expectationSummary.acceptance_criteria.map((criterion, index) => (
                      <ListItem key={index} fontSize="sm">
                        <ListIcon as={FiCheckCircle} color="green.500" />
                        {criterion}
                      </ListItem>
                    ))}
                  </List>
                  
                  <Text fontWeight="bold" fontSize="sm" mb={1}>Constraints:</Text>
                  <List spacing={1} mb={3}>
                    {expectationSummary.constraints && expectationSummary.constraints.map((constraint, index) => (
                      <ListItem key={index} fontSize="sm">
                        <ListIcon as={FiAlertCircle} color="orange.500" />
                        {constraint}
                      </ListItem>
                    ))}
                  </List>
                  
                  {/* Sub-Expectations Section */}
                  {expectationSummary.sub_expectations && expectationSummary.sub_expectations.length > 0 && (
                    <>
                      <Divider my={3} />
                      <Text fontWeight="bold" fontSize="md" mb={2} color="blue.600">Key Components:</Text>
                      
                      {expectationSummary.sub_expectations.map((subExp, index) => (
                        <Box 
                          key={index} 
                          mb={3} 
                          p={2} 
                          borderLeft="2px" 
                          borderColor="blue.300"
                          bg="blue.50"
                          borderRadius="sm"
                        >
                          <Text fontWeight="bold" fontSize="sm">{subExp.name}</Text>
                          <Text fontSize="sm" mb={1}>{subExp.description}</Text>
                          
                          {subExp.acceptance_criteria && subExp.acceptance_criteria.length > 0 && (
                            <Box ml={2} mt={1}>
                              <Text fontSize="xs" fontWeight="bold" color="gray.600">Key Requirements:</Text>
                              <List spacing={0}>
                                {subExp.acceptance_criteria.slice(0, 2).map((criterion, idx) => (
                                  <ListItem key={idx} fontSize="xs">
                                    <ListIcon as={FiCheckCircle} color="green.400" fontSize="xs" />
                                    {criterion}
                                  </ListItem>
                                ))}
                                {subExp.acceptance_criteria.length > 2 && (
                                  <Text fontSize="xs" color="gray.500" ml={5}>
                                    +{subExp.acceptance_criteria.length - 2} more
                                  </Text>
                                )}
                              </List>
                            </Box>
                          )}
                        </Box>
                      ))}
                    </>
                  )}
                  
                  <Flex justify="flex-end" mt={2}>
                    <Badge colorScheme="green" fontSize="xs">
                      Generated by Expeta Clarifier
                    </Badge>
                  </Flex>
                </CardBody>
              </Card>
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

export { ChatInterface };
export default App;
