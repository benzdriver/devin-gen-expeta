/**
 * @file GenerationsPage.js
 * @description 代码生成页面，处理代码生成和查看
 * 
 * 需求:
 * 1. 更新现有GenerationsPage，简化并聚焦于MVP功能
 * 2. 支持从确认的期望生成代码
 * 3. 展示生成结果和进度
 * 4. 提供代码查看和下载功能
 * 5. 与ConversationPage集成，实现流畅的用户体验
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
  SimpleGrid,
  HStack,
  VStack,
  Badge,
  Divider,
  Tab,
  Tabs,
  TabList,
  TabPanel,
  TabPanels,
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink
} from '@chakra-ui/react';
import { useNavigate, useParams } from 'react-router-dom';
import { ChevronRightIcon } from '@chakra-ui/icons';
import CodeViewer from '../components/code/CodeViewer';
import useGeneration from '../hooks/useGeneration';
import { generationService } from '../services/api';

/**
 * 代码生成页面组件
 */
const GenerationsPage = () => {
  const { generationId } = useParams();
  const navigate = useNavigate();
  const toast = useToast();
  const [generations, setGenerations] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  
  const {
    generation,
    expectation,
    loadGeneration,
    downloadCode,
    loading,
    error
  } = useGeneration(generationId);
  
  // 加载生成历史
  useEffect(() => {
    const fetchGenerations = async () => {
      if (!generationId) {
        setIsLoading(true);
        try {
          const response = await generationService.getGenerations();
          setGenerations(response.data || []);
        } catch (error) {
          console.error('加载生成历史失败:', error);
          toast({
            title: '加载失败',
            description: error.message || '无法加载生成历史',
            status: 'error',
            duration: 3000,
            isClosable: true,
          });
        } finally {
          setIsLoading(false);
        }
      }
    };
    
    fetchGenerations();
  }, [generationId, toast]);
  
  // 处理错误提示
  useEffect(() => {
    if (error) {
      toast({
        title: '出错了',
        description: error,
        status: 'error',
        duration: 5000,
        isClosable: true
      });
    }
  }, [error, toast]);
  
  // 如果没有生成ID，显示生成历史列表
  if (!generationId) {
    return (
      <Container maxW="container.xl" py={4}>
        <Heading size="lg" mb={6}>代码生成历史</Heading>
        
        {isLoading ? (
          <Flex justify="center" align="center" h="50vh">
            <Spinner size="xl" />
            <Text ml={4}>加载生成历史...</Text>
          </Flex>
        ) : generations.length === 0 ? (
          <Box textAlign="center" py={20}>
            <Heading size="md" mb={4}>暂无生成历史</Heading>
            <Button 
              colorScheme="blue"
              onClick={() => navigate('/conversation')}
            >
              开始新对话
            </Button>
          </Box>
        ) : (
          <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={4}>
            {generations.map(generation => (
              <Box key={generation.id} p={4} borderWidth="1px" borderRadius="lg">
                <Heading size="md" mb={2}>生成 {generation.id.slice(0, 8)}...</Heading>
                <Text>生成时间: {new Date(generation.timestamp).toLocaleString()}</Text>
                <Text>生成状态: {generation.status === 'completed' ? '已完成' : 
                  generation.status === 'generating' ? '生成中' : 
                  generation.status === 'failed' ? '失败' : generation.status}</Text>
                <Text>文件数量: {generation.files?.length || 0}个文件</Text>
                <Button 
                  colorScheme="blue" 
                  mt={4}
                  onClick={() => navigate(`/generations/${generation.id}`)}
                >
                  查看详情
                </Button>
              </Box>
            ))}
          </SimpleGrid>
        )}
      </Container>
    );
  }
  
  // 渲染面包屑导航
  const renderBreadcrumb = () => (
    <Breadcrumb 
      separator={<ChevronRightIcon color="gray.500" />} 
      mb={4} 
      fontSize="sm"
    >
      <BreadcrumbItem>
        <BreadcrumbLink onClick={() => navigate('/')}>首页</BreadcrumbLink>
      </BreadcrumbItem>
      <BreadcrumbItem>
        <BreadcrumbLink onClick={() => navigate('/generations')}>生成历史</BreadcrumbLink>
      </BreadcrumbItem>
      <BreadcrumbItem isCurrentPage>
        <BreadcrumbLink>
          {generationId ? `生成 ${generationId.slice(0, 8)}...` : ''}
        </BreadcrumbLink>
      </BreadcrumbItem>
    </Breadcrumb>
  );
  
  return (
    <Container maxW="container.xl" py={4}>
      {renderBreadcrumb()}
      
      <Flex justify="space-between" align="center" mb={4}>
        <Heading size="lg">代码生成详情</Heading>
      </Flex>
      
      {loading ? (
        <Flex justify="center" align="center" h="50vh">
          <Spinner size="xl" />
          <Text ml={4}>加载生成结果...</Text>
        </Flex>
      ) : !generation ? (
        <Box textAlign="center" py={20}>
          <Heading size="md" mb={4}>未找到生成结果</Heading>
          <Button onClick={() => navigate('/generations')}>
            返回生成历史
          </Button>
        </Box>
      ) : (
        <Box>
          <Tabs mb={6}>
            <TabList>
              <Tab>代码查看</Tab>
              <Tab>需求详情</Tab>
              <Tab>生成信息</Tab>
            </TabList>
            
            <TabPanels>
              {/* 代码查看面板 */}
              <TabPanel p={0} pt={4}>
                <Box h="calc(100vh - 250px)">
                  <CodeViewer 
                    files={generation.files || []}
                    generation={generation}
                  />
                </Box>
              </TabPanel>
              
              {/* 需求详情面板 */}
              <TabPanel>
                {expectation ? (
                  <Box p={4} borderWidth="1px" borderRadius="md">
                    <Heading size="md" mb={2}>{expectation.name}</Heading>
                    <Text mb={4}>{expectation.description}</Text>
                    
                    <Heading size="sm" mb={2}>验收标准</Heading>
                    <VStack align="start" pl={4} mb={4}>
                      {expectation.acceptanceCriteria && expectation.acceptanceCriteria.map((criterion, index) => (
                        <Text key={index}>• {criterion}</Text>
                      ))}
                    </VStack>
                    
                    {expectation.constraints && expectation.constraints.length > 0 && (
                      <>
                        <Heading size="sm" mb={2}>约束条件</Heading>
                        <VStack align="start" pl={4}>
                          {expectation.constraints.map((constraint, index) => (
                            <Text key={index}>• {constraint}</Text>
                          ))}
                        </VStack>
                      </>
                    )}
                  </Box>
                ) : (
                  <Text>未找到相关期望信息</Text>
                )}
              </TabPanel>
              
              {/* 生成信息面板 */}
              <TabPanel>
                <VStack align="stretch" spacing={4}>
                  <Box>
                    <Heading size="sm" mb={2}>生成时间</Heading>
                    <Text>{new Date(generation.timestamp).toLocaleString()}</Text>
                  </Box>
                  
                  <Box>
                    <Heading size="sm" mb={2}>生成状态</Heading>
                    <Badge colorScheme={generation.status === 'completed' ? 'green' : 'blue'}>
                      {generation.status === 'completed' ? '已完成' : 
                       generation.status === 'generating' ? '生成中' : 
                       generation.status === 'failed' ? '失败' : generation.status}
                    </Badge>
                  </Box>
                  
                  <Box>
                    <Heading size="sm" mb={2}>文件数量</Heading>
                    <Text>{generation.files?.length || 0}个文件</Text>
                  </Box>
                  
                  <Box>
                    <Heading size="sm" mb={2}>存储路径</Heading>
                    <Text fontFamily="mono">{generation.outputDir}</Text>
                  </Box>
                  
                  <Box>
                    <Button 
                      colorScheme="blue" 
                      onClick={() => downloadCode(generation.id)}
                    >
                      下载生成代码
                    </Button>
                  </Box>
                </VStack>
              </TabPanel>
            </TabPanels>
          </Tabs>
        </Box>
      )}
    </Container>
  );
};

export default GenerationsPage;
