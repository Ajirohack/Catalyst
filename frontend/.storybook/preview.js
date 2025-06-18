// .storybook/preview.js
import '../src/index.css';
import { initialize, mswDecorator } from 'msw-storybook-addon';
import { handlers } from '../src/mocks/handlers';

// Initialize MSW
initialize({
    onUnhandledRequest: 'bypass',
});

// Global decorators
export const decorators = [
    mswDecorator,
    (Story) => (
        <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
            <Story />
        </div>
    ),
];

export const parameters = {
    actions: { argTypesRegex: "^on[A-Z].*" },
    controls: {
        matchers: {
            color: /(background|color)$/i,
            date: /Date$/,
        },
    },
    msw: {
        handlers: handlers,
    },
    backgrounds: {
        default: 'light',
        values: [
            {
                name: 'light',
                value: '#f9fafb',
            },
            {
                name: 'dark',
                value: '#111827',
            },
        ],
    },
    layout: 'fullscreen',
    a11y: {
        config: {
            rules: [
                {
                    // Temporarily disable this rule as it causes noise
                    id: 'color-contrast',
                    enabled: true,
                },
            ],
        },
    },
};
