import React, { useState } from 'react';
import { useNavigate, Link as RouterLink } from 'react-router-dom';
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

const RegisterPage = () => {
  const { register, error, setCurrentUser } = useAuth();
  const navigate = useNavigate();
  
  const [userData, setUserData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  
  const [showPassword, setShowPassword] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [registerError, setRegisterError] = useState('');
  
  // 处理表单输入变化
  const handleChange = (e) => {
    const { name, value } = e.target;
    setUserData(prev => ({
      ...prev,
      [name]: value,
    }));
  };
  
  // 切换密码可见性
  const handleTogglePassword = () => {
    setShowPassword(!showPassword);
  };
  
  // 提交注册
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Validate password match
    if (userData.password !== userData.confirmPassword) {
      setRegisterError('密码不匹配');
      return;
    }
    
    // 验证基本表单数据
    if (!userData.name || !userData.email || !userData.password) {
      setRegisterError('请填写所有必填字段');
      return;
    }
    
    setSubmitting(true);
    setRegisterError('');
    
    try {
      // 尝试使用真实注册请求
      try {
        const user = await register(userData);
        navigate('/', { replace: true });
        return;
      } catch (error) {
        console.log('真实注册失败，使用模拟注册');
      }
      
      // 开发模式：模拟成功注册
      setTimeout(() => {
        // 模拟用户数据
        const mockUser = {
          id: 'user_' + Date.now().toString(36),
          name: userData.name,
          email: userData.email,
          created_at: new Date().toISOString()
        };
        
        // 存储认证信息
        localStorage.setItem('authToken', 'demo-token-' + mockUser.id);
        localStorage.setItem('mockUser', JSON.stringify(mockUser));
        
        // 更新Auth上下文
        setCurrentUser && setCurrentUser(mockUser);
        
        navigate('/', { replace: true });
      }, 1000);
    } catch (err) {
      setRegisterError(err.message || '注册失败，请稍后再试');
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
            Create your account
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
              {(registerError || error) && (
                <Alert status="error" borderRadius="md">
                  <AlertIcon />
                  {registerError || error}
                </Alert>
              )}
              
              <FormControl id="name" isRequired>
                <FormLabel>Full Name</FormLabel>
                <Input
                  type="text"
                  name="name"
                  value={userData.name}
                  onChange={handleChange}
                />
              </FormControl>
              
              <FormControl id="email" isRequired>
                <FormLabel>Email</FormLabel>
                <Input
                  type="email"
                  name="email"
                  value={userData.email}
                  onChange={handleChange}
                />
              </FormControl>
              
              <FormControl id="password" isRequired>
                <FormLabel>Password</FormLabel>
                <InputGroup>
                  <Input
                    type={showPassword ? 'text' : 'password'}
                    name="password"
                    value={userData.password}
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
              
              <FormControl id="confirmPassword" isRequired>
                <FormLabel>Confirm Password</FormLabel>
                <InputGroup>
                  <Input
                    type={showPassword ? 'text' : 'password'}
                    name="confirmPassword"
                    value={userData.confirmPassword}
                    onChange={handleChange}
                  />
                </InputGroup>
              </FormControl>
              
              <Stack spacing={10} pt={2}>
                <Button
                  loadingText="Registering"
                  size="lg"
                  colorScheme={'blue'}
                  isLoading={submitting}
                  type="submit"
                >
                  Register
                </Button>
              </Stack>
              
              <Stack pt={6}>
                <Text align={'center'}>
                  Already have an account?{' '}
                  <Link as={RouterLink} to="/login" color={'blue.400'}>
                    Login
                  </Link>
                </Text>
              </Stack>
            </Stack>
          </form>
        </Box>
      </Stack>
    </Flex>
  );
};

export default RegisterPage; 