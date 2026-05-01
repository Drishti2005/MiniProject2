/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  safelist: [
    'border-l-red-500','border-l-amber-400','border-l-teal-400',
    'bg-red-50','bg-amber-50','bg-teal-50',
    'text-red-700','text-amber-700','text-teal-700',
    'border-red-200','border-amber-200','border-teal-200',
  ],
  theme: {
    extend: {
      fontFamily: { sans: ['Inter','sans-serif'] },
      colors: {
        navy:  { DEFAULT:'#0B2A46', light:'#1a3d5c', dark:'#071e33', muted:'#1e4060' },
        cred:  { DEFAULT:'#BC2719', light:'#d63020' },
        slate: { panel:'#F4F6F8', border:'#D0D5DD', muted:'#667085' },
      },
      boxShadow: {
        card:   '0 4px 24px rgba(11,42,70,0.09)',
        'card-hv':'0 8px 32px rgba(11,42,70,0.16)',
        glass:  '0 8px 32px rgba(0,0,0,0.28)',
        glow:   '0 0 20px rgba(147,242,242,0.2)',
      },
      animation: {
        'pulse-ring': 'pulse-ring 1.6s ease-out infinite',
        'ecg':        'ecg 2s ease-in-out infinite',
        'shimmer':    'shimmer 1.8s linear infinite',
        'fade-up':    'fade-up 0.4s ease-out',
        'shake':      'shake 0.5s ease-in-out',
      },
      keyframes: {
        'pulse-ring': { '0%':{ transform:'scale(1)', opacity:'0.8' }, '100%':{ transform:'scale(2.6)', opacity:'0' } },
        'ecg':        { '0%,100%':{ opacity:'1' }, '50%':{ opacity:'0.25' } },
        'shimmer':    { '0%':{ backgroundPosition:'-200% 0' }, '100%':{ backgroundPosition:'200% 0' } },
        'fade-up':    { '0%':{ opacity:'0', transform:'translateY(14px)' }, '100%':{ opacity:'1', transform:'translateY(0)' } },
        'shake':      { '0%,100%':{ transform:'translateX(0)' }, '20%,60%':{ transform:'translateX(-6px)' }, '40%,80%':{ transform:'translateX(6px)' } },
      },
    },
  },
  plugins: [],
}
