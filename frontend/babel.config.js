module.exports = {
  presets: [
    'module:metro-react-native-babel-preset',  // Metro preset for React Native
    'module:@react-native/babel-preset',       // Optional, useful for additional React Native configurations
  ],
  plugins: [
    [
      'module-resolver',
      {
        root: ['./src'],  // Set the root to 'src' for cleaner imports
        alias: {
          '@assets': './src/assets',
          '@components': './src/components',
          '@services': './src/services',
          '@screens': './src/screens',
          '@api': './src/api',
        },
      },
    ],
    'react-native-dotenv',  // Enable dotenv support
  ],
};
