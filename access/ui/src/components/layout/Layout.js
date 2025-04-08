import React from 'react';
import { Outlet } from 'react-router-dom';
import {
  Box,
  Flex,
  Container,
  useDisclosure
} from '@chakra-ui/react';

import Header from './Header';
import Sidebar from './Sidebar';
import Footer from './Footer';

const Layout = () => {
  // 侧边栏折叠状态
  const { isOpen, onOpen, onClose, onToggle } = useDisclosure({
    defaultIsOpen: true
  });

  return (
    <Box minH="100vh" bg="gray.50">
      <Header onMenuToggle={onToggle} isSidebarOpen={isOpen} />
      
      <Flex>
        <Sidebar isOpen={isOpen} onClose={onClose} />
        
        <Box 
          flex="1" 
          transition="margin-left 0.3s"
          ml={isOpen ? { base: 0, md: '250px' } : 0}
          w={isOpen ? { base: '100%', md: 'calc(100% - 250px)' } : '100%'}
        >
          <Container maxW="1200px" py={6} px={4}>
            <Outlet />
          </Container>
          
          <Footer />
        </Box>
      </Flex>
    </Box>
  );
};

export default Layout; 