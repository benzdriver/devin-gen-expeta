import React from 'react';
import { Box, Text, Link, Flex, useColorModeValue } from '@chakra-ui/react';

function Footer() {
  return (
    <Box
      as="footer"
      py={6}
      px={4}
      mt="auto"
      bg={useColorModeValue('gray.50', 'gray.900')}
      borderTop="1px"
      borderTopColor={useColorModeValue('gray.200', 'gray.700')}
    >
      <Flex
        maxW="1200px"
        mx="auto"
        align="center"
        justify="space-between"
        direction={{ base: 'column', md: 'row' }}
        textAlign={{ base: 'center', md: 'left' }}
        gap={2}
      >
        <Text fontSize="sm" color={useColorModeValue('gray.600', 'gray.400')}>
          © {new Date().getFullYear()} Expeta 2.0 - Semantic-Driven Software Development
        </Text>
        
        <Flex gap={4}>
          <Link 
            href="#" 
            fontSize="sm" 
            color={useColorModeValue('gray.600', 'gray.400')}
            _hover={{ color: 'blue.500' }}
          >
            Documentation
          </Link>
          <Link 
            href="#" 
            fontSize="sm" 
            color={useColorModeValue('gray.600', 'gray.400')}
            _hover={{ color: 'blue.500' }}
          >
            About
          </Link>
          <Link 
            href="#" 
            fontSize="sm" 
            color={useColorModeValue('gray.600', 'gray.400')}
            _hover={{ color: 'blue.500' }}
          >
            Contact
          </Link>
        </Flex>
      </Flex>
    </Box>
  );
}

export default Footer;
