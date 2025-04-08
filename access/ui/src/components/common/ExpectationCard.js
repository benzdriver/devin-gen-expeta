import React from 'react';
import {
  Box,
  Heading,
  Text,
  Badge,
  Button,
  Flex,
  List,
  ListItem,
  ListIcon,
  Divider,
  useDisclosure,
} from '@chakra-ui/react';
import { useNavigate } from 'react-router-dom';
import { CheckCircleIcon } from '@chakra-ui/icons';

// 期望卡片组件
const ExpectationCard = ({ 
  expectation, 
  onGenerate, 
  onView, 
  isDetailView = false,
  isGenerating = false 
}) => {
  const navigate = useNavigate();
  
  // 处理缺失的字段
  const {
    id = '',
    name = 'Unnamed Expectation',
    description = 'No description available',
    level = 'top',
    parent_id = null,
    acceptance_criteria = [],
    constraints = [],
    created_at = new Date().toISOString(),
    updated_at = new Date().toISOString(),
    has_generated_code = false,
    has_validation = false,
  } = expectation || {};

  // 计算创建时间
  const createdDate = new Date(created_at).toLocaleDateString();
  
  // 计算等级标签的颜色
  const levelColor = level === 'top' ? 'green' : level === 'sub' ? 'purple' : 'blue';

  // 处理生成代码事件
  const handleGenerate = (e) => {
    e.stopPropagation();
    if (onGenerate) {
      onGenerate(id);
    }
  };

  // 处理查看详情事件
  const handleView = () => {
    if (onView) {
      onView(id);
    } else {
      navigate(`/expectations/${id}`);
    }
  };

  return (
    <Box 
      p={5} 
      shadow="md" 
      borderWidth="1px" 
      borderRadius="md" 
      bg="white"
      onClick={isDetailView ? undefined : handleView}
      cursor={isDetailView ? 'default' : 'pointer'}
      _hover={isDetailView ? {} : { shadow: 'lg' }}
      transition="all 0.2s"
    >
      <Flex justifyContent="space-between" alignItems="flex-start" mb={2}>
        <Heading fontSize="xl" color="blue.600" isTruncated maxW="70%">
          {name}
        </Heading>
        <Flex>
          <Badge colorScheme={levelColor} mr={2}>
            {level}
          </Badge>
          {has_generated_code && (
            <Badge colorScheme="cyan" mr={2}>
              Generated
            </Badge>
          )}
          {has_validation && (
            <Badge colorScheme="green">
              Validated
            </Badge>
          )}
        </Flex>
      </Flex>
      
      <Text color="gray.600" mb={4} noOfLines={isDetailView ? undefined : 2}>
        {description}
      </Text>
      
      {isDetailView && (
        <>
          <Divider my={4} />
          
          {acceptance_criteria.length > 0 && (
            <Box mb={4}>
              <Heading size="sm" mb={2}>Acceptance Criteria</Heading>
              <List spacing={2}>
                {acceptance_criteria.map((criterion, index) => (
                  <ListItem key={index} display="flex" alignItems="flex-start">
                    <ListIcon as={CheckCircleIcon} color="green.500" mt={1} />
                    <Text>{criterion}</Text>
                  </ListItem>
                ))}
              </List>
            </Box>
          )}
          
          {constraints.length > 0 && (
            <Box mb={4}>
              <Heading size="sm" mb={2}>Constraints</Heading>
              <List spacing={2}>
                {constraints.map((constraint, index) => (
                  <ListItem key={index} display="flex" alignItems="flex-start">
                    <ListIcon as={CheckCircleIcon} color="orange.500" mt={1} />
                    <Text>{constraint}</Text>
                  </ListItem>
                ))}
              </List>
            </Box>
          )}
          
          {parent_id && (
            <Box mb={4}>
              <Heading size="sm" mb={2}>Parent Expectation</Heading>
              <Text color="blue.600" fontWeight="medium">
                {parent_id}
              </Text>
            </Box>
          )}
          
          <Divider my={4} />
          
          <Flex justifyContent="space-between" alignItems="center">
            <Text fontSize="sm" color="gray.500">
              Created: {createdDate}
            </Text>
            
            {!isDetailView && (
              <Button 
                size="sm" 
                colorScheme="blue"
                onClick={handleGenerate}
                isLoading={isGenerating}
                loadingText="Generating"
              >
                Generate Code
              </Button>
            )}
          </Flex>
        </>
      )}
      
      {!isDetailView && (
        <Flex justifyContent="space-between" alignItems="center" mt={4}>
          <Text fontSize="sm" color="gray.500">
            Created: {createdDate}
          </Text>
          
          <Button 
            size="sm" 
            colorScheme="blue"
            onClick={handleGenerate}
            isLoading={isGenerating}
            loadingText="Generating"
          >
            Generate Code
          </Button>
        </Flex>
      )}
    </Box>
  );
};

export default ExpectationCard; 