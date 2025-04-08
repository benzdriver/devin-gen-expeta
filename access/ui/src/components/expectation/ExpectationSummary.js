/**
 * @file ExpectationSummary.js
 * @description 期望摘要组件，展示期望的关键信息
 */

import React from 'react';
import {
  Box,
  Heading,
  Text,
  VStack,
  HStack,
  Badge,
  Divider,
  Button,
  useColorModeValue
} from '@chakra-ui/react';

/**
 * 期望摘要组件
 * @param {Object} props 组件属性
 * @param {Object} props.expectation 期望对象
 * @param {boolean} props.showActions 是否显示操作按钮
 * @param {Function} props.onEdit 编辑回调
 * @param {Function} props.onGenerate 生成代码回调
 */
const ExpectationSummary = ({ 
  expectation, 
  showActions = true,
  onEdit,
  onGenerate
}) => {
  // 即使 expectation 为 null，也要调用所有的 Hook
  const bgColor = useColorModeValue('white', 'gray.700');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  
  // 如果没有 expectation，提前返回
  if (!expectation) return null;
  
  // 状态颜色映射
  const statusColors = {
    draft: 'gray',
    confirmed: 'green',
    generating: 'blue',
    completed: 'teal'
  };
  
  // 获取状态对应的颜色
  const getStatusColor = (status) => {
    return statusColors[status] || 'gray';
  };
  
  // 获取状态的可读文本
  const getStatusText = (status) => {
    return status === 'draft' ? '草稿' : 
      status === 'confirmed' ? '已确认' : 
      status === 'generating' ? '生成中' :
      status === 'completed' ? '已完成' : status;
  };
  
  return (
    <Box 
      p={4} 
      borderWidth="1px" 
      borderRadius="md"
      bg={bgColor}
      borderColor={borderColor}
      shadow="sm"
    >
      <HStack mb={2} justify="space-between">
        <Heading size="md">{expectation.name}</Heading>
        <Badge colorScheme={getStatusColor(expectation.status)}>
          {getStatusText(expectation.status)}
        </Badge>
      </HStack>
      
      <Divider my={2} />
      
      <Box mb={3}>
        <Text>{expectation.description}</Text>
      </Box>
      
      <Box mb={3}>
        <Heading size="sm" mb={1}>验收标准</Heading>
        <VStack align="start" pl={4} spacing={1}>
          {expectation.acceptanceCriteria && expectation.acceptanceCriteria.map((criterion, index) => (
            <Text key={index} fontSize="sm">• {criterion}</Text>
          ))}
        </VStack>
      </Box>
      
      {expectation.constraints && expectation.constraints.length > 0 && (
        <Box mb={3}>
          <Heading size="sm" mb={1}>约束条件</Heading>
          <VStack align="start" pl={4} spacing={1}>
            {expectation.constraints.map((constraint, index) => (
              <Text key={index} fontSize="sm">• {constraint}</Text>
            ))}
          </VStack>
        </Box>
      )}
      
      {showActions && (
        <HStack spacing={4} mt={4} justify="flex-end">
          {onEdit && (
            <Button 
              size="sm" 
              variant="outline" 
              onClick={() => onEdit(expectation)}
            >
              编辑
            </Button>
          )}
          
          {onGenerate && expectation.status === 'confirmed' && (
            <Button 
              size="sm" 
              colorScheme="blue"
              onClick={() => onGenerate(expectation.id)}
            >
              生成代码
            </Button>
          )}
        </HStack>
      )}
    </Box>
  );
};

export default ExpectationSummary;
