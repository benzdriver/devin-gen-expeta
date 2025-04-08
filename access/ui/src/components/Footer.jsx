import React from 'react';
import { Box, Text, useColorModeValue } from '@chakra-ui/react';

function Footer() {
  return (
    <Box
      as="footer"
      py={4}
      px={4}
      mt="auto"
      bg={useColorModeValue('white', 'gray.800')}
      borderTop="1px"
      borderTopColor={useColorModeValue('gray.200', 'gray.700')}
      textAlign="center"
    >
      <Text fontSize="sm" color={useColorModeValue('gray.600', 'gray.400')}>
        © {new Date().getFullYear()} Expeta 2.0 - Semantic-Driven Software Development
      </Text>
    </Box>
  );
}

export default Footer;
