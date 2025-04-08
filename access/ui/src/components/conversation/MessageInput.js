/**
 * @file MessageInput.js
 * @description 消息输入组件，用于用户输入和发送消息
 * 
 * 需求:
 * 1. 提供消息输入框和发送按钮
 * 2. 支持Enter键发送和Shift+Enter换行
 * 3. 处理输入验证和长度限制
 * 4. 支持发送状态反馈
 * 5. 支持暂时禁用输入（等待系统响应时）
 * 
 * 组件属性:
 * - onSend: 发送消息的回调函数
 * - disabled: 是否禁用输入
 * - placeholder: 输入框占位文本
 */

import React, { useState, useRef } from 'react';
import { 
  Input, 
  Button, 
  HStack, 
  Textarea, 
  useToast,
  Box,
  FormControl,
  useColorModeValue
} from '@chakra-ui/react';
import { ArrowUpIcon } from '@chakra-ui/icons';

/**
 * 消息输入组件，用于用户输入和发送消息
 * @param {Object} props 组件属性
 * @param {Function} props.onSend 发送消息的回调函数
 * @param {boolean} props.disabled 是否禁用输入
 * @param {string} props.placeholder 输入框占位文本
 */
const MessageInput = ({ 
  onSend, 
  disabled = false, 
  placeholder = '输入您的需求或问题...',
  maxLength = 1000 
}) => {
  const [message, setMessage] = useState('');
  const [isSending, setIsSending] = useState(false);
  const textareaRef = useRef(null);
  const toast = useToast();
  const bgColor = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');

  // 处理消息发送
  const handleSend = async () => {
    const trimmedMessage = message.trim();
    
    if (!trimmedMessage) {
      return;
    }
    
    if (trimmedMessage.length > maxLength) {
      toast({
        title: '消息过长',
        description: `消息不能超过${maxLength}个字符`,
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
      return;
    }
    
    setIsSending(true);
    
    try {
      await onSend(trimmedMessage);
      setMessage('');
      if (textareaRef.current) {
        textareaRef.current.focus();
      }
    } catch (error) {
      toast({
        title: '发送失败',
        description: error.message || '无法发送消息，请稍后重试',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
    } finally {
      setIsSending(false);
    }
  };

  // 处理键盘事件
  const handleKeyPress = (e) => {
    // Enter发送，Shift+Enter换行
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <Box 
      p={3} 
      borderTop="1px" 
      borderColor={borderColor}
      bg={bgColor}
      position="sticky"
      bottom="0"
      width="100%"
    >
      <FormControl>
        <HStack>
          <Textarea
            ref={textareaRef}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={placeholder}
            size="md"
            resize="none"
            rows={2}
            disabled={disabled || isSending}
            maxLength={maxLength}
            bg={bgColor}
            borderRadius="md"
            flex="1"
          />
          <Button
            colorScheme="blue"
            onClick={handleSend}
            isLoading={isSending}
            isDisabled={disabled || !message.trim()}
            borderRadius="md"
            h="100%"
          >
            <ArrowUpIcon />
          </Button>
        </HStack>
      </FormControl>
    </Box>
  );
};

export default MessageInput;
