import React from 'react';
import { Link as RouterLink } from 'react-router-dom';
import {
  Box,
  Flex,
  Button,
  useColorModeValue,
  Avatar,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  MenuDivider,
  Heading
} from '@chakra-ui/react';
import { useAuth } from '../ui_system';

function Header() {
  const { currentUser, logout } = useAuth();

  return (
    <Box
      bg={useColorModeValue('white', 'gray.800')}
      color={useColorModeValue('gray.600', 'white')}
      borderBottom={1}
      borderStyle={'solid'}
      borderColor={useColorModeValue('gray.200', 'gray.900')}
      position="sticky"
      top="0"
      zIndex="100"
      boxShadow="sm"
      minH="60px"
    >
      <Flex
        minH={'60px'}
        py={{ base: 2 }}
        px={{ base: 4 }}
        align={'center'}
        maxW="1600px"
        mx="auto"
        justify="space-between"
      >
        <Flex flex={1} justify="center">
          <RouterLink to="/">
            <Heading
              fontFamily={'heading'}
              color={useColorModeValue('blue.600', 'white')}
              size="md"
            >
              EXPETA 2.0
            </Heading>
          </RouterLink>
        </Flex>

        {currentUser ? (
          <Menu>
            <MenuButton
              as={Button}
              rounded={'full'}
              variant={'link'}
              cursor={'pointer'}
              minW={0}
            >
              <Avatar
                size={'sm'}
                name={currentUser.name || 'User'}
                src={currentUser.avatar}
              />
            </MenuButton>
            <MenuList>
              <MenuItem as={RouterLink} to="/settings">Settings</MenuItem>
              <MenuDivider />
              <MenuItem onClick={logout}>Sign Out</MenuItem>
            </MenuList>
          </Menu>
        ) : (
          <Button
            as={RouterLink}
            to={'/login'}
            fontSize={'sm'}
            fontWeight={400}
            variant={'link'}
          >
            Sign In
          </Button>
        )}
      </Flex>
    </Box>
  );
}

export default Header;
