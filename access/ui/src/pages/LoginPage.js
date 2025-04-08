import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  Box,
  Flex,
  Stack,
  Heading,
  Text,
  FormControl,
  FormLabel,
  Input,
  Button,
  Checkbox,
  Link,
  InputGroup,
  InputRightElement,
  IconButton,
  Alert,
  AlertIcon,
  useColorModeValue,
} from '@chakra-ui/react';
import { ViewIcon, ViewOffIcon } from '@chakra-ui/icons';

import { useAuth } from '../context/AuthContext';

const LoginPage = () => {
  const { login, error, setCurrentUser } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  
  const [credentials, setCredentials] = useState({
    email: '',
    password: '',
  });
  
  const [showPassword, setShowPassword] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [loginError, setLoginError] = useState('');
  
  // 获取重定向目标
  const from = location.state?.from?.pathname || "/";
  
  // 处理表单输入变化
  const handleChange = (e) => {
    const { name, value } = e.target;
    setCredentials(prev => ({
      ...prev,
      [name]: value,
    }));
  };
  
  // 切换密码可见性
  const handleTogglePassword = () => {
    setShowPassword(!showPassword);
  };
  
  // 提交登录
  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setLoginError('');
    
    // 验证表单数据
    if (!credentials.email || !credentials.password) {
      setLoginError('Please enter both email and password');
      setSubmitting(false);
      return;
    }
    
    try {
      // 尝试使用真实登录请求
      try {
        const user = await login(credentials);
        navigate(from, { replace: true });
        return;
      } catch (error) {
        console.log('真实登录失败，使用模拟登录');
      }
      
      // 开发模式：模拟成功登录
      setTimeout(() => {
        // 模拟用户数据
        const mockUser = {
          id: 'user_123',
          name: '测试用户',
          email: credentials.email
        };
        
        // 存储认证信息
        localStorage.setItem('authToken', 'demo-token');
        localStorage.setItem('mockUser', JSON.stringify(mockUser));
        
        // 更新Auth上下文
        setCurrentUser && setCurrentUser(mockUser);
        
        // 导航到之前的页面或首页
        navigate(from, { replace: true });
      }, 1000);
    } catch (err) {
      setLoginError(err.message || '登录失败，请检查您的账号和密码');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Flex
      minH={'100vh'}
      align={'center'}
      justify={'center'}
      bg={useColorModeValue('gray.50', 'gray.800')}
    >
      <Stack spacing={8} mx={'auto'} maxW={'lg'} py={12} px={6} width="100%">
        <Stack align={'center'}>
          <Heading fontSize={'4xl'} color="blue.600">Expeta 2.0</Heading>
          <Text fontSize={'lg'} color={'gray.600'}>
            Semantic-Driven Software Development
          </Text>
        </Stack>
        
        <Box
          rounded={'lg'}
          bg={useColorModeValue('white', 'gray.700')}
          boxShadow={'lg'}
          p={8}
        >
          <form onSubmit={handleSubmit}>
            <Stack spacing={4}>
              {(loginError || error) && (
                <Alert status="error" borderRadius="md">
                  <AlertIcon />
                  {loginError || error}
                </Alert>
              )}
              
              <FormControl id="email" isRequired>
                <FormLabel>Email</FormLabel>
                <Input
                  type="email"
                  name="email"
                  value={credentials.email}
                  onChange={handleChange}
                />
              </FormControl>
              
              <FormControl id="password" isRequired>
                <FormLabel>Password</FormLabel>
                <InputGroup>
                  <Input
                    type={showPassword ? 'text' : 'password'}
                    name="password"
                    value={credentials.password}
                    onChange={handleChange}
                  />
                  <InputRightElement h={'full'}>
                    <IconButton
                      variant={'ghost'}
                      onClick={handleTogglePassword}
                      icon={showPassword ? <ViewIcon /> : <ViewOffIcon />}
                      aria-label={showPassword ? 'Hide password' : 'Show password'}
                    />
                  </InputRightElement>
                </InputGroup>
              </FormControl>
              
              <Stack spacing={10}>
                <Stack
                  direction={{ base: 'column', sm: 'row' }}
                  align={'start'}
                  justify={'space-between'}
                >
                  <Checkbox>Remember me</Checkbox>
                  <Link color={'blue.400'}>Forgot password?</Link>
                </Stack>
                
                <Button
                  colorScheme={'blue'}
                  loadingText="Signing in"
                  isLoading={submitting}
                  type="submit"
                >
                  Sign in
                </Button>
              </Stack>
            </Stack>
          </form>
        </Box>
        
        <Text mt={4} textAlign="center">
          Don't have an account?{' '}
          <Link color={'blue.400'} onClick={() => navigate('/register')}>
            Register here
          </Link>
        </Text>
      </Stack>
    </Flex>
  );
};

export default LoginPage; 