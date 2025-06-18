// .storybook/main.js
const path = require('path');

module.exports = {
    stories: ['../src/**/*.stories.jsx'],
    addons: [
        '@storybook/addon-links',
        '@storybook/addon-essentials',
        '@storybook/addon-interactions',
        '@storybook/addon-a11y',
        '@storybook/preset-create-react-app',
    ],
    framework: {
        name: '@storybook/react-webpack5',
        options: {},
    },
    docs: {
        autodocs: true,
    },
    webpackFinal: async (config) => {
        config.resolve.alias = {
            ...config.resolve.alias,
            '@': path.resolve(__dirname, '../src'),
        };
        return config;
    },
};
