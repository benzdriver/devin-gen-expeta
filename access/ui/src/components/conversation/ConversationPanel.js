/**
 * @file ConversationPanel.js
 * @description 对话面板组件，实现用户与系统的对话交互
 * 
 * 需求:
 * 1. 实现对话消息的展示，包括用户消息和系统消息
 * 2. 提供消息输入和发送功能
 * 3. 支持消息历史滚动和加载
 * 4. 显示对话状态和期望确认界面
 * 5. 响应式设计，适应不同屏幕尺寸
 * 6. 使用WebSocket实现实时消息更新
 * 
 * 组件属性:
 * - conversationId: 当前会话ID
 * - initialMessages: 初始消息列表
 * - onSendMessage: 发送消息的回调函数
 */

import React, { useState, useEffect } from 'react';
import { 
  Box, 
  VStack, 
  HStack, 
  Text, 
  Divider, 
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  Button,
  useColorModeValue,
  Flex,
  Heading,
  Badge,
  Progress
} from '@chakra-ui/react';
import MessageList from './MessageList';
import MessageInput from './MessageInput';
import { ConversationStates, getStateDescription } from '../../../shared/states/ConversationStates';

/**
 * 对话面板组件，实现用户与系统的对话交互
 * @param {Object} props 组件属性
 * @param {string} props.conversationId 当前会话ID
 * @param {Array} props.initialMessages 初始消息列表
 * @param {Function} props.onSendMessage 发送消息的回调函数
 */
const ConversationPanel = ({ 
  conversationId,
  initialMessages = [],
  initialState = ConversationStates.INITIAL,
  initialExpectation = null,
  onSendMessage,
  onGenerateCode,
  onConfirmExpectation,
  onEditExpectation,
  loading = false
}) => {
  const [messages, setMessages] = useState(initialMessages);
  const [state, setState] = useState(initialState);
  const [currentExpectation, setCurrentExpectation] = useState(initialExpectation);
  
  // 将所有 useColorModeValue 调用移到组件顶层
  const stateBgColor = useColorModeValue('gray.100', 'gray.700');
  const expectationBgColor = useColorModeValue('green.50', 'green.900');
  
  // 状态背景色映射
  const stateBgColors = {
    'initial': 'gray.100',
    'collecting_requirement': 'blue.50',
    'clarifying': 'blue.100',
    'expectation_draft': 'green.50',
    'expectation_confirmed': 'green.100',
    'generating': 'purple.50',
    'reviewing': 'orange.50',
    'completed': 'teal.50'
  };

  // 状态图标
  const stateIcons = {
    'initial': '🆕',
    'collecting_requirement': '📝',
    'clarifying': '🔍',
    'expectation_draft': '📋',
    'expectation_confirmed': '✅',
    'generating': '⚙️',
    'reviewing': '👀',
    'completed': '🏁'
  };

  // 更新WebSocket消息
  useEffect(() => {
    if (conversationId) {
      // 订阅WebSocket更新
      const subscription = subscribeToConversation(conversationId, (update) => {
        if (update.messages) {
          setMessages(update.messages);
        }
        if (update.state) {
          setState(update.state);
        }
        if (update.currentExpectation) {
          setCurrentExpectation(update.currentExpectation);
        }
      });
      
      return () => {
        // 取消订阅
        if (subscription && subscription.unsubscribe) {
          subscription.unsubscribe();
        }
      };
    }
  }, [conversationId]);

  // 模拟订阅函数，实际项目中应该由WebSocket服务提供
  const subscribeToConversation = (id, callback) => {
    console.log(`订阅会话更新: ${id}`);
    // 模拟实现，实际应该返回一个可取消的订阅
    return {
      unsubscribe: () => console.log(`取消订阅会话: ${id}`)
    };
  };

  // 处理发送消息
  const handleSendMessage = async (messageText) => {
    if (!onSendMessage) return;
    
    // 先本地添加用户消息以提供即时反馈
    const userMessage = {
      id: `local_${Date.now()}`,
      sender: 'user',
      content: messageText,
      timestamp: new Date().toISOString()
    };
    
    setMessages(prev => [...prev, userMessage]);
    
    try {
      // 调用父组件提供的发送消息函数
      await onSendMessage(messageText);
    } catch (error) {
      // 显示错误或撤销本地添加的消息
      console.error('发送消息失败:', error);
    }
  };

  // 修改 renderStateIndicator 函数，使用组件顶层定义的 stateBgColor
  const renderStateIndicator = () => (
    <Box 
      p={2} 
      bg={stateBgColor}  // 使用组件顶层定义的 stateBgColor
      borderRadius="md"
      mb={4}
    >
      <Flex align="center">
        <Text fontSize="xl" mr={2}>{stateIcons[state] || '🔄'}</Text>
        <Box flex="1">
          <Text fontWeight="bold">
            {state === 'initial' ? '会话初始化' :
             state === 'collecting_requirement' ? '收集需求中' :
             state === 'clarifying' ? '澄清需求细节中' :
             state === 'expectation_draft' ? '期望草稿已形成' :
             state === 'expectation_confirmed' ? '期望已确认' :
             state === 'generating' ? '生成代码中' :
             state === 'reviewing' ? '代码审核中' :
             state === 'completed' ? '流程已完成' : state}
          </Text>
          {state === 'generating' && (
            <Progress size="xs" isIndeterminate colorScheme="blue" mt={1} />
          )}
        </Box>
      </Flex>
    </Box>
  );

  // 渲染期望确认界面
  const renderExpectationConfirmation = () => {
    if (!currentExpectation || state !== 'expectation_draft') {
      return null;
    }
    
    return (
      <Box 
        p={4} 
        borderWidth="1px" 
        borderRadius="md" 
        bg={expectationBgColor}
        mb={4}
      >
        <Heading size="md" mb={2}>期望摘要</Heading>
        
        <Box mb={3}>
          <Text fontWeight="bold">名称:</Text>
          <Text>{currentExpectation.name}</Text>
        </Box>
        
        <Box mb={3}>
          <Text fontWeight="bold">描述:</Text>
          <Text>{currentExpectation.description}</Text>
        </Box>
        
        <Box mb={3}>
          <Text fontWeight="bold">验收标准:</Text>
          <VStack align="start" pl={4}>
            {currentExpectation.acceptanceCriteria && currentExpectation.acceptanceCriteria.map((criterion, index) => (
              <Text key={index}>• {criterion}</Text>
            ))}
          </VStack>
        </Box>
        
        {currentExpectation.constraints && currentExpectation.constraints.length > 0 && (
          <Box mb={3}>
            <Text fontWeight="bold">约束条件:</Text>
            <VStack align="start" pl={4}>
              {currentExpectation.constraints.map((constraint, index) => (
                <Text key={index}>• {constraint}</Text>
              ))}
            </VStack>
          </Box>
        )}
        
        <HStack spacing={4} mt={4}>
          <Button 
            colorScheme="blue" 
            onClick={() => onConfirmExpectation && onConfirmExpectation(currentExpectation)}
          >
            确认期望
          </Button>
          <Button 
            variant="outline" 
            onClick={() => onEditExpectation && onEditExpectation(currentExpectation)}
          >
            编辑
          </Button>
        </HStack>
      </Box>
    );
  };

  // 渲染生成代码按钮
  const renderGenerateButton = () => {
    if (state !== 'expectation_confirmed' || !currentExpectation) {
      return null;
    }
    
    return (
      <Box textAlign="center" mb={4}>
        <Button 
          colorScheme="purple"
          size="lg"
          isLoading={loading}
          loadingText="准备生成..."
          onClick={() => onGenerateCode && onGenerateCode(currentExpectation.id)}
        >
          生成代码
        </Button>
      </Box>
    );
  };

  return (
    <Box 
      borderWidth="1px" 
      borderRadius="lg" 
      overflow="hidden" 
      h="full" 
      display="flex" 
      flexDirection="column"
    >
      {renderStateIndicator()}
      
      {renderExpectationConfirmation()}
      
      {renderGenerateButton()}
      
      <Box flex="1" overflowY="auto" px={4} pb={2}>
        <MessageList messages={messages} loading={loading} />
      </Box>
      
      <MessageInput 
        onSend={handleSendMessage} 
        disabled={loading || state === ConversationStates.GENERATING}
        placeholder={
          state === ConversationStates.INITIAL 
            ? "请描述您的需求..." 
            : state === ConversationStates.CLARIFYING 
              ? "请回答问题，帮助我更好地理解您的需求..." 
              : "输入消息..."
        }
      />
    </Box>
  );
};

export default ConversationPanel;
