import React from 'react';
import { Outlet } from 'react-router-dom';
import {
  Box,
  Container
} from '@chakra-ui/react';

import Header from './Header';
import Footer from './Footer';

function Layout() {
  return (
    <Box minH="100vh" bg="gray.50">
      <Header />
      
      <Box flex="1" w="100%">
        <Container maxW="1200px" py={6} px={4} minH="calc(100vh - 140px)">
          <Outlet />
        </Container>
        
        <Footer />
      </Box>
    </Box>
  );
}

export default Layout;
