import React from 'react';
import { Outlet } from 'react-router-dom';
import {
  Box,
  Container,
  Flex
} from '@chakra-ui/react';

import Header from './Header';
import Footer from './Footer';

function Layout() {
  return (
    <Flex direction="column" minH="100vh" bg="gray.50">
      <Header />
      
      <Box flex="1" w="100%" display="flex" justifyContent="center">
        <Container 
          maxW="900px" 
          py={6} 
          px={4} 
          flex="1"
          display="flex"
          flexDirection="column"
        >
          <Outlet />
        </Container>
      </Box>
      
      <Footer />
    </Flex>
  );
}

export default Layout;
