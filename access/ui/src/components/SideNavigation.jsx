import React, { useState } from 'react';
import { Box, VStack, Flex, Text, Icon, Divider, useMediaQuery } from '@chakra-ui/react';
import { useNavigate, useLocation } from 'react-router-dom';

const navItems = [
  { name: 'Dashboard', path: '/', icon: '📊' },
  { name: 'Process', path: '/process', icon: '🔄' },
  { name: 'Clarify', path: '/clarify', icon: '🔍' },
  { name: 'Generate', path: '/generate', icon: '⚙️' },
  { name: 'Validate', path: '/validate', icon: '✅' },
  { name: 'Settings', path: '/settings', icon: '⚙️' }
];

function SideNavigation() {
  const navigate = useNavigate();
  const location = useLocation();
  const [isLargerThan768] = useMediaQuery("(min-width: 768px)");
  const [isCollapsed, setIsCollapsed] = useState(false);
  
  const handleNavigation = (path) => {
    navigate(path);
  };
  
  if (!isLargerThan768) {
    return null;
  }
  
  return (
    <Box 
      w={isCollapsed ? "60px" : "250px"} 
      bg="white" 
      h="calc(100vh - 64px)" 
      shadow="md" 
      position="fixed" 
      left={0} 
      top="64px"
      zIndex={10}
      transition="width 0.3s ease"
    >
      <VStack spacing={0} align="stretch">
        {navItems.map((item) => (
          <Box key={item.name}>
            <Flex
              py={3}
              px={4}
              cursor="pointer"
              bg={location.pathname === item.path ? "blue.50" : "transparent"}
              borderLeft={location.pathname === item.path ? "4px solid" : "4px solid transparent"}
              borderLeftColor="blue.500"
              onClick={() => handleNavigation(item.path)}
              _hover={{ bg: "gray.100" }}
              transition="all 0.2s"
              align="center"
            >
              <Box mr={isCollapsed ? 0 : 3} fontSize="18px">
                {item.icon}
              </Box>
              {!isCollapsed && (
                <Text 
                  fontWeight={location.pathname === item.path ? "bold" : "normal"}
                  color={location.pathname === item.path ? "blue.600" : "gray.700"}
                >
                  {item.name}
                </Text>
              )}
            </Flex>
            <Divider />
          </Box>
        ))}
      </VStack>
      
      {/* Toggle button at the bottom */}
      <Flex 
        position="absolute" 
        bottom="10px" 
        left="0" 
        right="0" 
        justifyContent="center"
        cursor="pointer"
        onClick={() => setIsCollapsed(!isCollapsed)}
        p={2}
      >
        <Box fontSize="18px">
          {isCollapsed ? '➡️' : '⬅️'}
        </Box>
      </Flex>
    </Box>
  );
}

export default SideNavigation;
