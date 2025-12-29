/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/templates/**/*.html",
    "./app/static/js/**/*.js",
  ],
  darkMode: 'class', // Enable class-based dark mode
  theme: {
    extend: {
      colors: {
        // Custom theme colors for light/dark/gray modes
        theme: {
          light: {
            primary: '#3B82F6',    // Blue
            secondary: '#6B7280',  // Gray
            background: '#F9FAFB', // Light gray
            surface: '#FFFFFF',    // White
            text: '#111827',       // Dark gray
            'text-secondary': '#6B7280', // Medium gray
          },
          dark: {
            primary: '#60A5FA',    // Light blue
            secondary: '#9CA3AF',  // Light gray
            background: '#111827', // Dark blue-gray
            surface: '#1F2937',    // Darker blue-gray
            text: '#F9FAFB',       // Light gray
            'text-secondary': '#D1D5DB', // Medium light gray
          },
          gray: {
            primary: '#6B7280',    // Medium gray
            secondary: '#9CA3AF',  // Light gray
            background: '#F3F4F6', // Light gray background
            surface: '#FFFFFF',    // White
            text: '#374151',       // Dark gray
            'text-secondary': '#6B7280', // Medium gray
          }
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'bounce-subtle': 'bounceSubtle 0.6s ease-in-out',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        bounceSubtle: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-5px)' },
        },
      },
      boxShadow: {
        'soft': '0 2px 15px rgba(0, 0, 0, 0.08)',
        'medium': '0 4px 25px rgba(0, 0, 0, 0.12)',
      },
      transitionDuration: {
        '400': '400ms',
      },
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
      },
    },
  },
  plugins: [
    // Custom plugin for theme utilities
    function({ addUtilities, theme }) {
      const themes = theme('colors.theme');

      Object.keys(themes).forEach(themeName => {
        const themeColors = themes[themeName];

        addUtilities({
          [`.theme-${themeName}`]: {
            '--color-primary': themeColors.primary,
            '--color-secondary': themeColors.secondary,
            '--color-background': themeColors.background,
            '--color-surface': themeColors.surface,
            '--color-text': themeColors.text,
            '--color-text-secondary': themeColors['text-secondary'],
          },
        });
      });
    },
  ],
}
