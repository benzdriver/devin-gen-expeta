import React, { useState } from 'react';
import { Link as RouterLink, useLocation } from 'react-router-dom';
import {
  Box,
  VStack,
  Flex,
  Text,
  Icon,
  useColorModeValue,
  Drawer,
  DrawerContent,
  CloseButton,
  useBreakpointValue,
  Tooltip
} from '@chakra-ui/react';
import {
  FiHome,
  FiTarget,
  FiCode,
  FiCheckCircle,
  FiSettings,
  FiMessageSquare,
  FiChevronLeft,
  FiChevronRight,
  FiBookmark
} from 'react-icons/fi';
import { useAuth } from '../ui_system';

const LinkItems = [
  { name: 'Dashboard', icon: FiHome, href: '/' },
  { name: 'Expectations', icon: FiTarget, href: '/expectations' },
  { name: 'Generations', icon: FiCode, href: '/generations' },
  { name: 'Validations', icon: FiCheckCircle, href: '/validations' },
  { name: 'Settings', icon: FiSettings, href: '/settings' },
  { name: 'Documentation', icon: FiBookmark, href: '/docs' }
];

function SideNavigation({ isOpen, onClose }) {
  const location = useLocation();
  const [isCollapsed, setIsCollapsed] = useState(false);
  const { currentUser } = useAuth();
  
  const bgColor = useColorModeValue('white', 'gray.900');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const isMobile = useBreakpointValue({ base: true, md: false });
  
  const toggleSidebar = () => {
    setIsCollapsed(!isCollapsed);
  };
  
  if (!currentUser) {
    return null;
  }
  
  if (isMobile) {
    return (
      <Drawer
        autoFocus={false}
        isOpen={isOpen}
        placement="left"
        onClose={onClose}
        returnFocusOnClose={false}
        onOverlayClick={onClose}
        size="full"
      >
        <DrawerContent>
          <SidebarContent
            onClose={onClose}
            currentPath={location.pathname}
            isCollapsed={false}
            bgColor={bgColor}
            borderColor={borderColor}
          />
        </DrawerContent>
      </Drawer>
    );
  }
  
  return (
    <Box 
      w={isCollapsed ? "60px" : "250px"} 
      bg={bgColor}
      h="calc(100vh - 60px)" // 调整为仅匹配header高度
      shadow="md" 
      position="fixed" 
      left={0} 
      top="60px" // 匹配header高度
      zIndex={90}
      transition="width 0.3s ease"
      borderRight="1px"
      borderRightColor={borderColor}
      display={{ base: 'none', md: 'block' }}
      transform={isOpen ? 'translateX(0)' : 'translateX(-100%)'}
    >
      <SidebarContent
        onClose={() => {}}
        currentPath={location.pathname}
        isCollapsed={isCollapsed}
        bgColor={bgColor}
        borderColor={borderColor}
        hideLogo={true}
      />
      
      {/* 底部切换按钮 */}
      <Flex 
        position="absolute" 
        bottom="10px" 
        left="0" 
        right="0" 
        justifyContent="center"
        cursor="pointer"
        onClick={toggleSidebar}
        p={2}
      >
        <Icon as={isCollapsed ? FiChevronRight : FiChevronLeft} fontSize="18px" />
      </Flex>
    </Box>
  );
}

const SidebarContent = ({ onClose, currentPath, isCollapsed, bgColor, borderColor, hideLogo = false }) => {
  return (
    <Box
      bg={bgColor}
      w="full"
      h="full"
      overflowY="auto"
    >
      {!hideLogo && !isCollapsed && (
        <Flex h="20" alignItems="center" mx="8" justifyContent="space-between">
          <Text fontSize="xl" fontWeight="bold" color="blue.600">
            Expeta 2.0
          </Text>
          <CloseButton display={{ base: 'flex', md: 'none' }} onClick={onClose} />
        </Flex>
      )}

      <VStack spacing={2} align="stretch" py={4}>
        {LinkItems.map((link) => (
          <NavItem
            key={link.name}
            icon={link.icon}
            href={link.href}
            isActive={currentPath === link.href || (link.href !== '/' && currentPath.startsWith(link.href))}
            isCollapsed={isCollapsed}
          >
            {link.name}
          </NavItem>
        ))}
      </VStack>
    </Box>
  );
};

const NavItem = ({ icon, children, href, isActive, isCollapsed }) => {
  const activeBg = useColorModeValue('blue.50', 'gray.700');
  const activeColor = useColorModeValue('blue.600', 'blue.200');
  const hoverBg = useColorModeValue('blue.50', 'gray.700');
  
  return (
    <Tooltip label={isCollapsed ? children : ''} placement="right" isDisabled={!isCollapsed}>
      <RouterLink to={href}>
        <Flex
          align="center"
          p="4"
          mx="4"
          borderRadius="lg"
          role="group"
          cursor="pointer"
          bg={isActive ? activeBg : 'transparent'}
          color={isActive ? activeColor : 'inherit'}
          fontWeight={isActive ? "semibold" : "normal"}
          borderLeft={isActive ? "4px solid" : "4px solid transparent"}
          borderLeftColor={isActive ? "blue.500" : "transparent"}
          _hover={{
            bg: hoverBg,
            color: activeColor,
          }}
        >
          {icon && (
            <Icon
              mr={isCollapsed ? 0 : 4}
              fontSize="16"
              as={icon}
            />
          )}
          {!isCollapsed && children}
        </Flex>
      </RouterLink>
    </Tooltip>
  );
};

export default SideNavigation;
