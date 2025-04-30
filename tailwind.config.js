/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ['class'],
  content: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        yes: '#3fb68b',
        no: '#ff5353',
        info: '#7a7c7d',
        main: '#7a7c7d',
        secondary: '#7a7c7d',
        active: '#7a7c7d',

        // REDESIGN
        'almost-black': '#111113' ,
        'addition': '#686868',
        'addition-1': '#222226',
        'main-text': '#FFFFFF',
        'button-text': '#3FB6A8',
        'header-text': '#71FFB8',
        'button': 'rgba(14, 255, 187, 20%)',
        'button-hover': 'rgba(2, 1, 1, 50%)',
        'button-v2': 'rgba(15, 51, 78, 100%)',
        'button-v2-hover': 'rgba(28, 28, 33, 100%)',
        'red-text': '#E41E1E',
        'green-text': '#61FF42',
        'tx-status-warning': '#F48E28',
        'tx-status-error': '#E41E1E',
        'tx-status-success': '#61FF42',
        'green-button': '#0A2B0C',
        'green-button-hover': '#0D4410',
        'menu-button': '#010101',
        'menu-button-hover': '#0A2220',
        'menu-button-active': '#17393D',
        'wallet-button': '#1D1C30',
        'wallet-button-hover': '#3A1F67',
        'proposal-status-approved': '#0D4410',
        'proposal-status-veto': '#621616',
        'proposal-status-rejected': '#720031',
        'proposal-status-voting': '#562E99',
        'status-text-approved': '#03F237',
        'status-text-rejected': '#DE1D71',
        'status-text-voting': '#8848F3',
        'status-text-veto': '#E41E1E',
        'star-yellow': '#EEBB4E',
        'blue-gradient': 'linear-gradient(to bottom, #3FB6A8, #1C504A)',
        'blue-transparent-gradient': 'linear-gradient(to bottom, rgba(31, 161, 217, 80%), rgba(6, 32, 42, 0%))',
        'сhart-line': '#03C6F2',
        'сhart-stroke': '#141415',
       
      },
      backgroundImage: {
        'main-image': "url('./public/images/main-bg.png')",
      },
      fontFamily: {
        'main': ['Inter'],
        'red-hat-mono': ['"Red Hat Mono"', 'monospace'],
        'roboto-flex': ['"Roboto Flex"', 'sans-serif'],
      },
    },
  },
  plugins: [require('daisyui'),
    require('tailwind-scrollbar'),
  ],
  daisyui: {
    themes: [
      {
        light: {
          ...require('daisyui/src/theming/themes')['[data-theme=light]'],
          primary: '#666cff',
          'base-100': '#141415',
          'base-200': '#252d37',
        },
      },
      {
        dark: {
          ...require('daisyui/src/theming/themes')['[data-theme=dark]'],
          primary: '#666cff',
          'base-100': '#141415',
          'base-200': '#252d37',
        },
      },
    ],
  },
};
