import React from 'react';
import { Link as RouterLink, useLocation } from 'react-router-dom';
import {
  Box,
  Flex,
  Text,
  CloseButton,
  VStack,
  Icon,
  useColorModeValue,
  Drawer,
  DrawerContent,
  useDisclosure,
  BoxProps,
  useBreakpointValue
} from '@chakra-ui/react';
import {
  FiHome,
  FiTarget,
  FiCode,
  FiCheckCircle,
  FiSettings,
  FiBookmark
} from 'react-icons/fi';

const LinkItems = [
  { name: 'Dashboard', icon: FiHome, href: '/' },
  { name: 'Expectations', icon: FiTarget, href: '/expectations' },
  { name: 'Generations', icon: FiCode, href: '/generations' },
  { name: 'Validations', icon: FiCheckCircle, href: '/validations' },
  { name: 'Settings', icon: FiSettings, href: '/settings' },
  { name: 'Documentation', icon: FiBookmark, href: '/docs' }
];

// 侧边栏组件
const Sidebar = ({ isOpen, onClose }) => {
  const location = useLocation();
  const isMobile = useBreakpointValue({ base: true, md: false });
  const bgColor = useColorModeValue('white', 'gray.900');
  const borderColor = useColorModeValue('gray.200', 'gray.700');

  // 移动端使用Drawer，桌面端使用固定侧边栏
  return (
    <>
      {isMobile ? (
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
              bgColor={bgColor}
              borderColor={borderColor}
            />
          </DrawerContent>
        </Drawer>
      ) : (
        <Box
          display={{ base: 'none', md: 'block' }}
          w={'250px'}
          pos="fixed"
          top="60px"
          h="calc(100vh - 60px)"
          borderRight="1px"
          borderRightColor={borderColor}
          transition="0.3s ease"
          transform={isOpen ? 'translateX(0)' : 'translateX(-100%)'}
          zIndex="90"
          bg={bgColor}
        >
          <SidebarContent
            onClose={() => onClose}
            currentPath={location.pathname}
            hideLogo
            bgColor={bgColor}
            borderColor={borderColor}
          />
        </Box>
      )}
    </>
  );
};

// 侧边栏内容
const SidebarContent = ({ onClose, currentPath, hideLogo = false, bgColor, borderColor, ...rest }) => {
  return (
    <Box
      bg={bgColor}
      borderRight="1px"
      borderRightColor={borderColor}
      w={{ base: 'full', md: 250 }}
      h="full"
      {...rest}
    >
      {!hideLogo && (
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
          >
            {link.name}
          </NavItem>
        ))}
      </VStack>
    </Box>
  );
};

// 导航项
const NavItem = ({ icon, children, href, isActive, ...rest }) => {
  const activeBg = useColorModeValue('blue.50', 'gray.700');
  const activeColor = useColorModeValue('blue.600', 'blue.200');
  const hoverBg = useColorModeValue('blue.50', 'gray.700');
  
  return (
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
        _hover={{
          bg: hoverBg,
          color: activeColor,
        }}
        {...rest}
      >
        {icon && (
          <Icon
            mr="4"
            fontSize="16"
            as={icon}
          />
        )}
        {children}
      </Flex>
    </RouterLink>
  );
};

export default Sidebar; 