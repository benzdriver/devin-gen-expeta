import React from 'react';
import { Link as RouterLink } from 'react-router-dom';
import { Box, Heading, Text, Button, Flex } from '@chakra-ui/react';

const NotFoundPage = () => {
  return (
    <Flex
      direction="column"
      align="center"
      justify="center"
      minH="70vh"
      p={8}
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
      <Text fontSize="xl" mb={8}>
        Page not found
      </Text>
      <Text color="gray.500" mb={8}>
        The page you're looking for doesn't seem to exist.
      </Text>
      <Button
        as={RouterLink}
        to="/"
        colorScheme="blue"
        variant="solid"
      >
        Go to Dashboard
      </Button>
    </Flex>
  );
};

export default NotFoundPage; 