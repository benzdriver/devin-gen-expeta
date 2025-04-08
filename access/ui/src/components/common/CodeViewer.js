import React, { useState } from 'react';
import {
  Box,
  Flex,
  Text,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  Button,
  useClipboard,
  useToast
} from '@chakra-ui/react';

// 简单的代码语法高亮功能
const highlightCode = (code, language) => {
  // 在实际项目中，可以使用highlight.js或prism.js等库
  // 这里仅做简单处理
  return code;
};

const CodeViewer = ({ files = [], language = 'javascript' }) => {
  const [activeIndex, setActiveIndex] = useState(0);
  const activeFile = files[activeIndex] || { name: '', content: '' };
  const { hasCopied, onCopy } = useClipboard(activeFile.content || '');
  const toast = useToast();

  // 文件为空时的处理
  if (!files.length) {
    return (
      <Box p={4} bg="gray.50" borderRadius="md" borderWidth="1px">
        <Text color="gray.500">No code files available</Text>
      </Box>
    );
  }

  const handleCopy = () => {
    onCopy();
    toast({
      title: 'Code copied',
      description: `Code from ${activeFile.name} copied to clipboard`,
      status: 'success',
      duration: 2000,
      isClosable: true,
    });
  };

  return (
    <Box borderWidth="1px" borderRadius="md" overflow="hidden" bg="white">
      <Flex justify="space-between" alignItems="center" bg="gray.100" p={2}>
        <Tabs 
          variant="soft-rounded" 
          colorScheme="blue" 
          size="sm"
          index={activeIndex}
          onChange={setActiveIndex}
          flex="1"
          overflow="auto"
        >
          <TabList>
            {files.map((file, index) => (
              <Tab key={index}>{file.name || `File ${index + 1}`}</Tab>
            ))}
          </TabList>
        </Tabs>
        <Button size="sm" onClick={handleCopy} ml={2}>
          {hasCopied ? 'Copied' : 'Copy'}
        </Button>
      </Flex>
      
      <Box 
        p={4} 
        overflowX="auto" 
        fontFamily="monospace" 
        fontSize="sm"
        whiteSpace="pre"
        bg="gray.50"
        h="400px"
        maxH="400px"
        overflowY="auto"
      >
        {highlightCode(activeFile.content || '', language)}
      </Box>
    </Box>
  );
};

export default CodeViewer; 