// tailwind.config.js - African Theme Configuration
module.exports = {
  content: [
    "./public/**/*.{html,js}",
    "./src/**/*.{html,js,vue}",
    "./myChama/src/**/*.{html,js,vue}",
    "./*.html"
  ],
  theme: {
    extend: {
      colors: {
        // African Orange Palette
        'african-orange': {
          50: '#fff7ed',
          100: '#ffedd5',
          200: '#fed7aa',
          300: '#fdba74',
          400: '#fb923c',
          500: '#f97316', // Main orange
          600: '#ea580c',
          700: '#c2410c',
          800: '#9a3412',
          900: '#7c2d12'
        },
        // African Green Palette
        'african-green': {
          50: '#f0fdf4',
          100: '#dcfce7',
          200: '#bbf7d0',
          300: '#86efac',
          400: '#4ade80',
          500: '#22c55e', // Main green
          600: '#16a34a',
          700: '#15803d',
          800: '#166534',
          900: '#14532d'
        },
        // Warm Neutrals
        'warm-white': '#fefefe',
        'cream': '#fef7f0',
        'warm-gray': {
          50: '#fafaf9',
          100: '#f5f5f4',
          200: '#e7e5e4',
          300: '#d6d3d1',
          400: '#a8a29e',
          500: '#78716c',
          600: '#57534e',
          700: '#44403c',
          800: '#292524',
          900: '#1c1917'
        }
      },
      fontFamily: {
        'sans': ['Inter', 'ui-sans-serif', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'Helvetica Neue', 'Arial', 'Noto Sans', 'sans-serif'],
        'display': ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
      },
      backgroundImage: {
        'african-gradient': 'linear-gradient(135deg, #f97316 0%, #22c55e 100%)',
        'african-pattern': `
          radial-gradient(circle at 25% 25%, rgba(249, 115, 22, 0.08) 0%, transparent 50%),
          radial-gradient(circle at 75% 75%, rgba(34, 197, 94, 0.08) 0%, transparent 50%),
          linear-gradient(135deg, rgba(249, 115, 22, 0.02) 0%, rgba(34, 197, 94, 0.02) 100%)
        `,
        'subtle-gradient': 'linear-gradient(135deg, #fff7ed 0%, #f0fdf4 100%)'
      },
      boxShadow: {
        'african': '0 4px 6px rgba(249, 115, 22, 0.25)',
        'african-lg': '0 8px 15px rgba(249, 115, 22, 0.35)',
        'green': '0 4px 6px rgba(34, 197, 94, 0.25)',
        'green-lg': '0 8px 15px rgba(34, 197, 94, 0.35)',
        'warm': '0 4px 6px rgba(0, 0, 0, 0.05)',
        'warm-lg': '0 12px 24px rgba(0, 0, 0, 0.1)'
      },
      borderRadius: {
        'xl': '12px',
        '2xl': '16px',
        '3xl': '24px'
      },
      animation: {
        'bounce-slow': 'bounce 2s infinite',
        'pulse-slow': 'pulse 3s infinite',
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.5s ease-out'
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' }
        },
        slideUp: {
          '0%': { transform: 'translateY(100%)' },
          '100%': { transform: 'translateY(0)' }
        }
      },
      spacing: {
        '18': '4.5rem',
        '88': '22rem'
      }
    }
  },
  plugins: [
    // Add any additional plugins here
    function({ addUtilities }) {
      const newUtilities = {
        '.hover-lift': {
          transition: 'transform 0.3s ease, box-shadow 0.3s ease',
          '&:hover': {
            transform: 'translateY(-2px)',
            boxShadow: '0 8px 15px rgba(0, 0, 0, 0.1)'
          }
        },
        '.african-accent': {
          position: 'relative',
          '&::before': {
            content: '""',
            position: 'absolute',
            top: '-4px',
            left: '0',
            right: '0',
            height: '4px',
            background: 'linear-gradient(90deg, #f97316 0%, #22c55e 33%, #f97316 66%, #22c55e 100%)',
            borderRadius: '2px'
          }
        }
      }
      addUtilities(newUtilities)
    }
  ]
}