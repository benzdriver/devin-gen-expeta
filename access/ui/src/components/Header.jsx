import React from 'react';
import { Box, Flex, Heading, Text } from '@chakra-ui/react';

function Header() {
  return (
    <Box bg="blue.600" color="white" py={3} px={4} shadow="md" h="64px">
      <Flex h="100%" mx="auto" justify="space-between" align="center">
        <Heading size="md">Expeta 2.0</Heading>
        <Text fontSize="sm" display={{ base: 'none', md: 'block' }}>Semantic-Driven Software Development</Text>
      </Flex>
    </Box>
  );
}

export default Header;
