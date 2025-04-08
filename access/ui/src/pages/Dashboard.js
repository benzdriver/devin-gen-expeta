import React, { useState, useEffect } from 'react';
import {
  Box,
  Heading,
  Text,
  SimpleGrid,
  Flex,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  Badge,
  Icon,
  Progress,
  Spinner,
  Alert,
  AlertIcon,
  Button,
  useToast
} from '@chakra-ui/react';
import { 
  FiTarget, 
  FiCode, 
  FiCheckCircle, 
  FiFilePlus, 
  FiRefreshCw 
} from 'react-icons/fi';
import { useExpeta } from '../context/ExpetaContext';

const Dashboard = () => {
  const { 
    stats, 
    health, 
    loadStats, 
    loadHealth, 
    loading, 
    error 
  } = useExpeta();
  
  const [isRefreshing, setIsRefreshing] = useState(false);
  const toast = useToast();

  // 刷新数据
  const handleRefresh = async () => {
    setIsRefreshing(true);
    try {
      await Promise.all([loadStats(), loadHealth()]);
      toast({
        title: 'Dashboard refreshed',
        status: 'success',
        duration: 2000,
        isClosable: true
      });
    } catch (err) {
      toast({
        title: 'Refresh failed',
        description: err.message,
        status: 'error',
        duration: 3000,
        isClosable: true
      });
    } finally {
      setIsRefreshing(false);
    }
  };

  if (loading.stats || loading.health) {
    return (
      <Box textAlign="center" py={10}>
        <Spinner size="xl" />
        <Text mt={4}>Loading dashboard data...</Text>
      </Box>
    );
  }

  return (
    <Box>
      <Flex justify="space-between" align="center" mb={6}>
        <Heading size="lg">Dashboard</Heading>
        <Button 
          leftIcon={<FiRefreshCw />} 
          colorScheme="blue" 
          variant="outline"
          onClick={handleRefresh}
          isLoading={isRefreshing}
          loadingText="Refreshing"
          size="sm"
        >
          Refresh
        </Button>
      </Flex>

      {/* 错误提示 */}
      {(error.stats || error.health) && (
        <Alert status="error" mb={6} borderRadius="md">
          <AlertIcon />
          {error.stats || error.health}
        </Alert>
      )}

      {/* 系统状态卡片 */}
      <Box
        p={5}
        shadow="md"
        borderWidth="1px"
        borderRadius="md"
        bg="white"
        mb={6}
      >
        <Flex justify="space-between" align="center" mb={4}>
          <Heading size="md">System Status</Heading>
          <Badge
            colorScheme={health.status === 'healthy' ? 'green' : health.status === 'degraded' ? 'yellow' : 'red'}
            fontSize="0.9em"
            p={1}
            borderRadius="md"
          >
            {health.status?.toUpperCase() || 'UNKNOWN'}
          </Badge>
        </Flex>
        
        <Text color="gray.600" mb={4}>
          Overall system health and component status
        </Text>
        
        <SimpleGrid columns={{ base: 1, md: 3 }} spacing={4}>
          {/* 组件状态 */}
          {Object.entries(health.services || {}).map(([service, status]) => (
            <Box p={3} shadow="sm" borderWidth="1px" borderRadius="md" key={service}>
              <Flex align="center" mb={2}>
                <Text fontWeight="medium">{service}</Text>
                <Badge
                  ml="auto"
                  colorScheme={status === 'healthy' ? 'green' : status === 'degraded' ? 'yellow' : 'red'}
                  fontSize="0.8em"
                >
                  {status?.toUpperCase() || 'UNKNOWN'}
                </Badge>
              </Flex>
              <Progress 
                size="sm" 
                colorScheme={status === 'healthy' ? 'green' : status === 'degraded' ? 'yellow' : 'red'}
                value={status === 'healthy' ? 100 : status === 'degraded' ? 50 : 0}
              />
            </Box>
          ))}
        </SimpleGrid>
      </Box>

      {/* 统计卡片 */}
      <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={6} mb={10}>
        <StatCard
          title="Requirements"
          value={stats.requirements || 0}
          icon={FiFilePlus}
          description="Total requirements processed"
          colorScheme="blue"
        />
        <StatCard
          title="Expectations"
          value={stats.expectations || 0}
          icon={FiTarget}
          description="Total expectations created"
          colorScheme="green"
        />
        <StatCard
          title="Generations"
          value={stats.generations || 0}
          icon={FiCode}
          description="Total code generations"
          colorScheme="purple"
        />
        <StatCard
          title="Validations"
          value={stats.validations || 0}
          icon={FiCheckCircle}
          description="Total code validations"
          colorScheme="orange"
        />
      </SimpleGrid>

      {/* 最近活动 */}
      <Box
        p={5}
        shadow="md"
        borderWidth="1px"
        borderRadius="md"
        bg="white"
        mb={6}
      >
        <Heading size="md" mb={4}>Recent Activity</Heading>
        <Text color="gray.500" fontSize="sm">
          Recent activity will appear here once available
        </Text>
      </Box>
    </Box>
  );
};

// 统计卡片组件
const StatCard = ({ title, value, icon, description, colorScheme }) => {
  return (
    <Stat
      px={4}
      py={5}
      shadow="md"
      borderWidth="1px"
      borderRadius="md"
      bg="white"
    >
      <Flex justifyContent="space-between">
        <Box>
          <StatLabel fontWeight="medium" isTruncated>
            {title}
          </StatLabel>
          <StatNumber fontSize="3xl" fontWeight="bold">
            {value}
          </StatNumber>
          <StatHelpText>{description}</StatHelpText>
        </Box>
        <Flex
          flexDirection="column"
          alignItems="center"
          justifyContent="center"
          height="50px"
          width="50px"
          borderRadius="lg"
          bg={`${colorScheme}.50`}
          color={`${colorScheme}.400`}
        >
          <Icon as={icon} w={6} h={6} />
        </Flex>
      </Flex>
    </Stat>
  );
};

export default Dashboard; 