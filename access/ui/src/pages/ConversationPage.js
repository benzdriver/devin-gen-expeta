/**
 * @file ConversationPage.js
 * @description 对话页面，集成对话组件和功能
 * 
 * 需求:
 * 1. 作为主要的需求收集和澄清界面
 * 2. 集成ConversationPanel组件
 * 3. 处理会话创建和加载
 * 4. 提供会话状态反馈
 * 5. 当期望确认后，提供进入代码生成的选项
 */

import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Heading, 
  Button, 
  Flex, 
  useToast,
  Text,
  Spinner,
  Container,
  VStack,
  HStack,
  Textarea,
  Divider
} from '@chakra-ui/react';
import { AddIcon } from '@chakra-ui/icons';
import { useNavigate, useParams } from 'react-router-dom';

/**
 * 对话页面组件
 */
const ConversationPage = () => {
  const { conversationId } = useParams();
  const navigate = useNavigate();
  const toast = useToast();
  
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  
  // 模拟加载对话历史
  useEffect(() => {
    if (conversationId) {
      setLoading(true);
      // 模拟API请求延迟
      setTimeout(() => {
        setMessages([
          {
            id: 'system-welcome',
            sender: 'system',
            content: '欢迎使用Expeta对话式需求收集，请描述您的需求。',
            timestamp: new Date().toISOString()
          }
        ]);
        setLoading(false);
      }, 500);
    }
  }, [conversationId]);
  
  // 创建新会话
  const createNewConversation = () => {
    // 实际项目中应该调用API创建新会话
    // 这里只是简单模拟
    const newId = `conv_${Date.now()}`;
    navigate(`/conversation/${newId}`);
  };
  
  // 发送消息
  const sendMessage = () => {
    if (!input.trim()) return;
    
    // 添加用户消息
    const newMessage = {
      id: `msg_${Date.now()}`,
      sender: 'user',
      content: input,
      timestamp: new Date().toISOString()
    };
    
    setMessages(prev => [...prev, newMessage]);
    setInput('');
    setLoading(true);
    
    // 模拟系统响应
    setTimeout(() => {
      const systemMessage = {
        id: `msg_${Date.now()}`,
        sender: 'system',
        content: generateSystemResponse(input),
        timestamp: new Date().toISOString()
      };
      
      setMessages(prev => [...prev, systemMessage]);
      setLoading(false);
    }, 1000);
  };
  
  // 模拟系统响应生成
  const generateSystemResponse = (userInput) => {
    const userInputLower = userInput.toLowerCase();
    
    if (userInputLower.includes('登录') || userInputLower.includes('认证')) {
      return '您是否需要实现一个用户认证系统？可以告诉我更多关于您期望的登录方式和安全需求吗？';
    } else if (userInputLower.includes('数据库') || userInputLower.includes('存储')) {
      return '您需要一个数据存储解决方案。您希望使用什么类型的数据库？有任何特定的性能或扩展性要求吗？';
    } else if (userInputLower.includes('api') || userInputLower.includes('接口')) {
      return '您需要开发API接口。这些接口需要支持哪些功能？是否需要特定的认证或限流机制？';
    } else {
      return '谢谢您的描述。能否提供更多关于功能需求、性能要求或技术栈偏好的细节，这将帮助我更好地理解您的需求。';
    }
  };
  
  // 处理Enter键发送
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };
  
  // 渲染消息
  const renderMessage = (message) => {
    const isUser = message.sender === 'user';
    return (
      <Box 
        key={message.id}
        bg={isUser ? 'blue.50' : 'gray.50'}
        p={3}
        borderRadius="lg"
        mb={3}
        ml={isUser ? 'auto' : 0}
        mr={isUser ? 0 : 'auto'}
        maxW="80%"
      >
        <Text 
          fontSize="xs" 
          fontWeight="bold" 
          mb={1}
          color={isUser ? 'blue.600' : 'gray.600'}
        >
          {isUser ? '您' : 'Expeta AI'}
        </Text>
        <Text>{message.content}</Text>
        <Text fontSize="xs" color="gray.500" mt={1} textAlign="right">
          {new Date(message.timestamp).toLocaleTimeString()}
        </Text>
      </Box>
    );
  };
  
  return (
    <Container maxW="container.xl" py={4}>
      <Flex justify="space-between" align="center" mb={4}>
        <Heading size="lg">
          {conversationId ? '对话' : '开始新对话'}
        </Heading>
        
        <Button 
          leftIcon={<AddIcon />} 
          colorScheme="blue" 
          onClick={createNewConversation}
        >
          新对话
        </Button>
      </Flex>
      
      {!conversationId ? (
        // 没有会话ID时显示欢迎信息
        <Box textAlign="center" py={20}>
          <Heading size="xl" mb={4}>欢迎使用Expeta对话式需求收集</Heading>
          <Text fontSize="lg" mb={8}>通过自然对话方式表达您的需求，我们将帮您生成高质量代码</Text>
          <Button 
            size="lg" 
            colorScheme="blue" 
            onClick={createNewConversation}
          >
            开始新对话
          </Button>
        </Box>
      ) : (
        // 有会话ID时显示对话界面
        <Box 
          borderWidth="1px" 
          borderRadius="lg" 
          overflow="hidden" 
          h="calc(100vh - 200px)"
          display="flex"
          flexDirection="column"
        >
          {/* 消息区域 */}
          <Box 
            flex="1" 
            p={4} 
            overflowY="auto"
            display="flex"
            flexDirection="column"
          >
            {loading && messages.length === 0 ? (
              <Flex justify="center" align="center" h="100%">
                <Spinner size="xl" />
                <Text ml={4}>加载对话历史...</Text>
              </Flex>
            ) : (
              <>
                {messages.map(renderMessage)}
                {loading && (
                  <Flex justify="center" py={4}>
                    <Spinner size="sm" />
                    <Text ml={2} fontSize="sm">思考中...</Text>
                  </Flex>
                )}
              </>
            )}
          </Box>
          
          {/* 输入区域 */}
          <Box p={4} borderTopWidth="1px">
            <Textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="输入您的需求或问题..."
              size="md"
              resize="none"
              rows={3}
              disabled={loading}
            />
            <Flex justify="flex-end" mt={2}>
              <Button
                colorScheme="blue"
                onClick={sendMessage}
                isLoading={loading}
                isDisabled={!input.trim()}
              >
                发送
              </Button>
            </Flex>
          </Box>
        </Box>
      )}
    </Container>
  );
};

export default ConversationPage;
