import React from 'react';
import { Box, Heading, Text, Button, Flex } from '@chakra-ui/react';
import { Link as RouterLink } from 'react-router-dom';

function NotFoundPage() {
  return (
    <Flex
      align="center"
      justify="center"
      minHeight="100vh"
      direction="column"
      p={5}
      textAlign="center"
    >
      <Heading
        display="inline-block"
        as="h1"
        size="4xl"
        bgGradient="linear(to-r, blue.400, blue.600)"
        backgroundClip="text"
        mb={4}
      >
        404
      </Heading>
      <Text fontSize="xl" mb={6}>
        Page Not Found
      </Text>
      <Text color={'gray.500'} mb={6}>
        The page you're looking for does not seem to exist
      </Text>

      <Button
        as={RouterLink}
        to="/"
        colorScheme="blue"
        bgGradient="linear(to-r, blue.400, blue.500, blue.600)"
        color="white"
        variant="solid"
      >
        Go to Home
      </Button>
    </Flex>
  );
}

export default NotFoundPage;
