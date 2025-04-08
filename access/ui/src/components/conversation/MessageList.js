/**
 * @file MessageList.js
 * @description 消息列表组件，展示对话中的消息历史
 * 
 * 需求:
 * 1. 展示消息列表，区分用户消息和系统消息
 * 2. 支持自动滚动到最新消息
 * 3. 支持消息分组和时间戳
 * 4. 处理不同类型消息的展示样式
 * 5. 支持长消息的折叠与展开
 * 
 * 组件属性:
 * - messages: 消息对象数组
 * - loading: 是否正在加载更多消息
 */

import React, { useEffect, useRef } from 'react';
import { 
  VStack, 
  Box, 
  Text, 
  Badge, 
  Avatar, 
  Flex, 
  Divider,
  useColorModeValue
} from '@chakra-ui/react';

/**
 * 消息列表组件，展示对话中的消息历史
 * @param {Object} props 组件属性
 * @param {Array} props.messages 消息对象数组
 * @param {boolean} props.loading 是否正在加载更多消息
 */
const MessageList = ({ messages = [], loading = false }) => {
  const bottomRef = useRef(null);
  const bgUser = useColorModeValue('blue.50', 'blue.900');
  const bgSystem = useColorModeValue('gray.100', 'gray.700');

  // 自动滚动到最新消息
  useEffect(() => {
    if (bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  // 根据发送时间对消息进行分组
  const groupMessagesByDate = () => {
    const groups = [];
    let currentDate = null;
    let currentGroup = [];

    messages.forEach(message => {
      const messageDate = new Date(message.timestamp).toLocaleDateString();
      
      if (messageDate !== currentDate) {
        if (currentGroup.length > 0) {
          groups.push({
            date: currentDate,
            messages: currentGroup
          });
        }
        currentDate = messageDate;
        currentGroup = [message];
      } else {
        currentGroup.push(message);
      }
    });

    if (currentGroup.length > 0) {
      groups.push({
        date: currentDate,
        messages: currentGroup
      });
    }

    return groups;
  };

  const messageGroups = groupMessagesByDate();

  return (
    <VStack spacing={4} align="stretch" w="100%" maxH="70vh" overflowY="auto" p={2}>
      {loading && (
        <Box textAlign="center" py={2}>
          <Text fontSize="sm" color="gray.500">加载消息历史...</Text>
        </Box>
      )}

      {messageGroups.map((group, groupIndex) => (
        <Box key={groupIndex}>
          <Flex justify="center" mb={2}>
            <Badge borderRadius="full" px={2} py={1} colorScheme="gray">
              {group.date}
            </Badge>
          </Flex>

          {group.messages.map((message, index) => (
            <Box 
              key={message.id || index}
              bg={message.sender === 'user' ? bgUser : bgSystem}
              p={3}
              borderRadius="lg"
              maxW="80%"
              alignSelf={message.sender === 'user' ? 'flex-end' : 'flex-start'}
              mb={3}
              ml={message.sender === 'user' ? 'auto' : 0}
              mr={message.sender === 'user' ? 0 : 'auto'}
            >
              <Flex>
                {message.sender !== 'user' && (
                  <Avatar 
                    size="sm" 
                    name="Expeta AI" 
                    src="/logo.png" 
                    mr={2}
                  />
                )}
                <Box>
                  <Flex justify="space-between" alignItems="center" mb={1}>
                    <Text fontWeight="bold" fontSize="sm">
                      {message.sender === 'user' ? '您' : 'Expeta AI'}
                    </Text>
                    <Text fontSize="xs" color="gray.500" ml={2}>
                      {new Date(message.timestamp).toLocaleTimeString()}
                    </Text>
                  </Flex>
                  <Text>{message.content}</Text>
                </Box>
                {message.sender === 'user' && (
                  <Avatar 
                    size="sm" 
                    name="User" 
                    ml={2}
                  />
                )}
              </Flex>
            </Box>
          ))}
        </Box>
      ))}

      <div ref={bottomRef} />
    </VStack>
  );
};

export default MessageList;
