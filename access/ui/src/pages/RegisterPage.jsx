import React, { useState } from 'react';
import { Link as RouterLink } from 'react-router-dom';
import {
  Box,
  Button,
  Flex,
  FormControl,
  FormLabel,
  Heading,
  Input,
  Stack,
  Text,
  Link,
  useColorModeValue,
  HStack,
  FormErrorMessage,
  Alert,
  AlertIcon,
} from '@chakra-ui/react';
import { useAuth } from '../ui_system';

function RegisterPage() {
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    password: '',
    confirmPassword: '',
  });
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { login } = useAuth();

  const handleChange = (e) => {
    const { id, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [id]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      const { firstName, lastName, email, password, confirmPassword } = formData;
      
      if (!firstName || !lastName || !email || !password) {
        throw new Error('All fields are required');
      }
      
      if (password !== confirmPassword) {
        throw new Error('Passwords do not match');
      }

      setTimeout(() => {
        const userData = {
          id: '1',
          name: `${firstName} ${lastName}`,
          email: email,
          avatar: '',
        };
        const token = 'mock-jwt-token';
        login(userData, token);
        setIsLoading(false);
      }, 1000);
    } catch (err) {
      setError(err.message);
      setIsLoading(false);
    }
  };

  return (
    <Flex
      minH={'100vh'}
      align={'center'}
      justify={'center'}
      bg={useColorModeValue('gray.50', 'gray.800')}
    >
      <Stack spacing={8} mx={'auto'} maxW={'lg'} py={12} px={6}>
        <Stack align={'center'}>
          <Heading fontSize={'4xl'} textAlign={'center'}>
            Sign up for Expeta
          </Heading>
          <Text fontSize={'lg'} color={'gray.600'}>
            to enjoy all of our cool features ✌️
          </Text>
        </Stack>
        <Box
          rounded={'lg'}
          bg={useColorModeValue('white', 'gray.700')}
          boxShadow={'lg'}
          p={8}
        >
          {error && (
            <Alert status="error" mb={4} borderRadius="md">
              <AlertIcon />
              {error}
            </Alert>
          )}
          <form onSubmit={handleSubmit}>
            <Stack spacing={4}>
              <HStack>
                <Box>
                  <FormControl id="firstName" isRequired>
                    <FormLabel>First Name</FormLabel>
                    <Input 
                      type="text" 
                      value={formData.firstName}
                      onChange={handleChange}
                    />
                  </FormControl>
                </Box>
                <Box>
                  <FormControl id="lastName" isRequired>
                    <FormLabel>Last Name</FormLabel>
                    <Input 
                      type="text" 
                      value={formData.lastName}
                      onChange={handleChange}
                    />
                  </FormControl>
                </Box>
              </HStack>
              <FormControl id="email" isRequired>
                <FormLabel>Email address</FormLabel>
                <Input 
                  type="email" 
                  value={formData.email}
                  onChange={handleChange}
                />
              </FormControl>
              <FormControl id="password" isRequired>
                <FormLabel>Password</FormLabel>
                <Input 
                  type="password" 
                  value={formData.password}
                  onChange={handleChange}
                />
              </FormControl>
              <FormControl id="confirmPassword" isRequired>
                <FormLabel>Confirm Password</FormLabel>
                <Input 
                  type="password" 
                  value={formData.confirmPassword}
                  onChange={handleChange}
                />
              </FormControl>
              <Stack spacing={10} pt={2}>
                <Button
                  loadingText="Submitting"
                  size="lg"
                  bg={'blue.400'}
                  color={'white'}
                  _hover={{
                    bg: 'blue.500',
                  }}
                  type="submit"
                  isLoading={isLoading}
                >
                  Sign up
                </Button>
              </Stack>
              <Stack pt={6}>
                <Text align={'center'}>
                  Already a user?{' '}
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
}

export default RegisterPage;
