import React from 'react';
import { Box, Flex, Text } from '@chakra-ui/react';

function Footer() {
  return (
    <Box bg="gray.100" color="gray.600" py={2} px={4} h="40px">
      <Flex h="100%" mx="auto" justify="space-between" align="center">
        <Text fontSize="xs">© 2025 Expeta 2.0</Text>
        <Text fontSize="xs">Version 0.1.0</Text>
      </Flex>
    </Box>
  );
}

export default Footer;
