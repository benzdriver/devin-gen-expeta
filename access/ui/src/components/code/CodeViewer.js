/**
 * @file CodeViewer.js
 * @description 代码查看组件，展示生成的代码文件
 * 
 * 需求:
 * 1. 展示代码内容，支持语法高亮
 * 2. 提供文件树导航，支持多文件切换
 * 3. 支持代码折叠和搜索
 * 4. 提供代码下载功能
 * 5. 代码行号和复制功能
 * 
 * 组件属性:
 * - files: 代码文件对象数组，包含path和content
 * - generation: 生成结果对象
 */

import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Flex, 
  VStack, 
  HStack, 
  Text, 
  Button,
  Heading,
  Divider,
  useColorModeValue,
  IconButton,
  Tooltip,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  Code,
  Select
} from '@chakra-ui/react';
import { 
  DownloadIcon, 
  CopyIcon, 
  ChevronRightIcon, 
  ChevronDownIcon, 
  SearchIcon,
  HamburgerIcon
} from '@chakra-ui/icons';

/**
 * 获取文件扩展名对应的语言
 * @param {string} fileName 文件名
 * @returns {string} 语言名称
 */
const getLanguageFromFilename = (fileName) => {
  const ext = fileName.split('.').pop().toLowerCase();
  const languageMap = {
    'js': 'javascript',
    'jsx': 'jsx',
    'ts': 'typescript',
    'tsx': 'tsx',
    'py': 'python',
    'html': 'html',
    'css': 'css',
    'json': 'json',
    'md': 'markdown',
    'java': 'java',
    'c': 'c',
    'cpp': 'cpp',
    'go': 'go',
    'rs': 'rust',
    'php': 'php',
    'rb': 'ruby',
    'sh': 'bash',
    'yml': 'yaml',
    'yaml': 'yaml',
    'sql': 'sql',
    'graphql': 'graphql',
    'swift': 'swift',
    'kt': 'kotlin'
  };
  
  return languageMap[ext] || 'text';
};

/**
 * 简化版代码查看组件，不使用react-syntax-highlighter
 */
const CodeViewer = ({ files = [], generation = null }) => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [selectedContent, setSelectedContent] = useState('');
  const [showLineNumbers, setShowLineNumbers] = useState(true);
  
  // 将所有Hook移到组件顶层
  const isDarkMode = useColorModeValue(false, true);
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const codeBgColor = useColorModeValue('gray.50', 'gray.700');
  
  // 文件树状态
  const [expandedFolders, setExpandedFolders] = useState({});
  
  // 初始选择第一个文件
  useEffect(() => {
    if (files.length > 0 && !selectedFile) {
      setSelectedFile(files[0].path);
      setSelectedContent(files[0].content);
    }
  }, [files, selectedFile]);
  
  // 文件选择处理
  const handleFileSelect = (path) => {
    const file = files.find(f => f.path === path);
    if (file) {
      setSelectedFile(path);
      setSelectedContent(file.content);
    }
  };
  
  // 复制代码处理
  const handleCopyCode = () => {
    navigator.clipboard.writeText(selectedContent);
  };
  
  // 处理文件夹展开/折叠
  const toggleFolder = (folderPath) => {
    setExpandedFolders(prev => ({
      ...prev,
      [folderPath]: !prev[folderPath]
    }));
  };
  
  // 按目录组织文件
  const organizeFilesByDirectory = () => {
    const result = {};
    
    files.forEach(file => {
      const parts = file.path.split('/');
      const fileName = parts.pop();
      const directory = parts.join('/');
      
      if (!result[directory]) {
        result[directory] = [];
      }
      
      result[directory].push({
        name: fileName,
        path: file.path,
        content: file.content
      });
    });
    
    return result;
  };
  
  const filesByDirectory = organizeFilesByDirectory();
  
  // 渲染文件树
  const renderFileTree = () => {
    const directories = Object.keys(filesByDirectory).sort();
    
    return (
      <VStack align="stretch" spacing={0}>
        {directories.map(directory => {
          const isRoot = directory === '';
          const isExpanded = expandedFolders[directory] !== false; // 默认展开
          
          return (
            <Box key={directory || 'root'}>
              {!isRoot && (
                <Flex 
                  py={1}
                  px={2}
                  cursor="pointer"
                  onClick={() => toggleFolder(directory)}
                  fontSize="sm"
                  fontWeight="bold"
                  alignItems="center"
                >
                  {isExpanded ? <ChevronDownIcon mr={1} /> : <ChevronRightIcon mr={1} />}
                  <Text>{directory}</Text>
                </Flex>
              )}
              
              {isExpanded && (
                <VStack align="stretch" spacing={0} pl={isRoot ? 0 : 4}>
                  {filesByDirectory[directory]
                    .sort((a, b) => a.name.localeCompare(b.name))
                    .map(file => (
                      <Box 
                        key={file.path}
                        py={1}
                        px={2}
                        cursor="pointer"
                        borderRadius="md"
                        bg={file.path === selectedFile ? 'blue.50' : 'transparent'}
                        _hover={{ bg: file.path === selectedFile ? 'blue.50' : 'gray.50' }}
                        onClick={() => handleFileSelect(file.path)}
                        fontSize="sm"
                      >
                        <Text>📄 {file.name}</Text>
                      </Box>
                    ))
                  }
                </VStack>
              )}
            </Box>
          );
        })}
      </VStack>
    );
  };
  
  return (
    <Box h="full">
      <Flex justify="space-between" align="center" mb={4}>
        <Heading size="md">代码查看器</Heading>
        
        <HStack>
          <Button 
            size="sm" 
            variant="outline" 
            leftIcon={<DownloadIcon />}
            onClick={() => {
              if (generation && generation.id) {
                window.open(`/api/generations/${generation.id}/download`, '_blank');
              }
            }}
          >
            下载全部
          </Button>
        </HStack>
      </Flex>
      
      <Flex h="calc(100% - 60px)" borderWidth="1px" borderRadius="md">
        {/* 文件树 */}
        <Box w="250px" borderRightWidth="1px" bg={bgColor} overflowY="auto">
          {renderFileTree()}
        </Box>
        
        {/* 代码查看区域 */}
        <Box flex="1" position="relative">
          {selectedFile ? (
            <>
              <Flex 
                justify="space-between" 
                align="center" 
                p={2} 
                borderBottomWidth="1px" 
                bg={codeBgColor}
              >
                <Text fontWeight="bold" fontSize="sm">{selectedFile}</Text>
                
                <HStack>
                  <Tooltip label="显示/隐藏行号">
                    <Button 
                      size="xs" 
                      variant={showLineNumbers ? "solid" : "outline"}
                      onClick={() => setShowLineNumbers(!showLineNumbers)}
                    >
                      行号
                    </Button>
                  </Tooltip>
                  
                  <Tooltip label="复制代码">
                    <IconButton 
                      size="xs" 
                      icon={<CopyIcon />}
                      onClick={handleCopyCode}
                      aria-label="复制代码"
                    />
                  </Tooltip>
                </HStack>
              </Flex>
              
              <Box 
                overflowY="auto" 
                h="calc(100% - 40px)" 
                fontSize="sm"
                p={4}
                fontFamily="monospace"
                whiteSpace="pre"
                bg={isDarkMode ? 'gray.800' : 'white'}
                color={isDarkMode ? 'white' : 'black'}
              >
                {showLineNumbers ? (
                  <table style={{ borderCollapse: 'collapse', width: '100%' }}>
                    <tbody>
                      {selectedContent.split('\n').map((line, i) => (
                        <tr key={i} style={{ lineHeight: '1.5' }}>
                          <td 
                            style={{ 
                              color: isDarkMode ? 'gray.400' : 'gray.500', 
                              textAlign: 'right', 
                              paddingRight: '1rem',
                              userSelect: 'none',
                              width: '1%', 
                              whiteSpace: 'nowrap',
                              borderRight: '1px solid',
                              borderColor: isDarkMode ? 'gray.600' : 'gray.200',
                            }}
                          >
                            {i + 1}
                          </td>
                          <td style={{ paddingLeft: '1rem' }}>{line}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                ) : (
                  selectedContent
                )}
              </Box>
            </>
          ) : (
            <Flex h="100%" justify="center" align="center">
              <Text color="gray.500">请选择文件查看代码</Text>
            </Flex>
          )}
        </Box>
      </Flex>
    </Box>
  );
};

export default CodeViewer;
