# Chama Management Platform

A comprehensive web application for managing investment groups (Chamas) in Kenya, featuring M-Pesa integration for seamless financial transactions.

## Overview

The Chama Management Platform empowers groups to digitize their financial operations, track contributions, manage loans, and achieve collective financial goals. Built specifically for the Kenyan market with native M-Pesa integration.

## Features

### 🏦 Chama Management
- **Group Setup**: Create and configure chama groups with custom rules
- **Member Management**: Add, remove, and manage member profiles
- **Role-based Access**: Admin, treasurer, secretary, and member roles
- **Group Settings**: Customize contribution schedules, meeting frequencies, and policies

### 💰 Financial Management
- **M-Pesa Integration**: Seamless mobile money transactions
- **Contribution Tracking**: Automated tracking of member contributions
- **Payment Reminders**: SMS and email notifications for due payments
- **Financial Reports**: Detailed financial statements and analytics
- **Multi-currency Support**: KES primary with USD/EUR options

### 🎯 Goal Setting & Tracking
- **Group Goals**: Set collective savings targets
- **Individual Goals**: Personal savings milestones within the group
- **Progress Visualization**: Charts and progress bars
- **Milestone Celebrations**: Automated notifications for achieved goals

### 📊 Loan Management
- **Loan Applications**: Digital loan request process
- **Approval Workflow**: Multi-level approval system
- **Payment Tracking**: Automated loan repayment monitoring
- **Interest Calculations**: Flexible interest rate configurations
- **Default Management**: Late payment alerts and penalties

### 📱 Communication
- **In-app Messaging**: Group chat and private messaging
- **Meeting Scheduler**: Plan and track group meetings
- **Announcements**: Broadcast important updates
- **Document Sharing**: Share meeting minutes and financial reports

### 📈 Analytics & Reporting
- **Dashboard**: Real-time group financial overview
- **Member Performance**: Individual contribution analytics
- **Financial Trends**: Historical data visualization
- **Export Options**: PDF and Excel report generation

## Technology Stack

### Frontend
- **Framework**: React 18+ with TypeScript
- **UI Library**: Material-UI or Chakra UI
- **State Management**: Redux Toolkit
- **Charts**: Recharts or Chart.js
- **Mobile Responsive**: Progressive Web App (PWA)

### Backend
- **Runtime**: Node.js with Express.js
- **Database**: PostgreSQL with Prisma ORM
- **Authentication**: JWT with refresh tokens
- **File Storage**: AWS S3 or Cloudinary
- **Email Service**: SendGrid or AWS SES

### Payment Integration
- **M-Pesa**: Safaricom Daraja API
- **Payment Processing**: Stripe (for card payments)
- **Webhook Handling**: Real-time payment notifications

### Infrastructure
- **Hosting**: Vercel (Frontend) + Railway/Heroku (Backend)
- **Database**: Supabase or AWS RDS
- **CDN**: Cloudflare
- **Monitoring**: Sentry for error tracking

## Getting Started

### Prerequisites
- Node.js 18+ and npm/yarn
- PostgreSQL database
- M-Pesa developer account (Safaricom Daraja API)
- Environment variables configured

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/chama-app.git
   cd chama-app
   ```

2. **Install dependencies**
   ```bash
   # Install backend dependencies
   cd backend
   npm install
   
   # Install frontend dependencies
   cd ../frontend
   npm install
   ```

3. **Environment Setup**
   ```bash
   # Backend environment variables
   cp backend/.env.example backend/.env
   
   # Frontend environment variables
   cp frontend/.env.example frontend/.env
   ```

4. **Database Setup**
   ```bash
   cd backend
   npx prisma generate
   npx prisma db push
   npx prisma db seed
   ```

5. **Start Development Servers**
   ```bash
   # Terminal 1 - Backend
   cd backend
   npm run dev
   
   # Terminal 2 - Frontend
   cd frontend
   npm start
   ```

### Environment Variables

#### Backend (.env)
```env
DATABASE_URL="postgresql://username:password@localhost:5432/chama_db"
JWT_SECRET="your-jwt-secret-key"
JWT_REFRESH_SECRET="your-refresh-secret-key"
MPESA_CONSUMER_KEY="your-mpesa-consumer-key"
MPESA_CONSUMER_SECRET="your-mpesa-consumer-secret"
MPESA_SHORTCODE="your-business-shortcode"
MPESA_PASSKEY="your-mpesa-passkey"
SENDGRID_API_KEY="your-sendgrid-key"
AWS_ACCESS_KEY_ID="your-aws-key"
AWS_SECRET_ACCESS_KEY="your-aws-secret"
```

#### Frontend (.env)
```env
REACT_APP_API_URL="http://localhost:3001/api"
REACT_APP_MPESA_CONSUMER_KEY="your-mpesa-consumer-key"
REACT_APP_ENVIRONMENT="development"
```

## API Documentation

### Authentication Endpoints
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/refresh` - Refresh access token
- `POST /api/auth/logout` - User logout

### Chama Management
- `GET /api/chamas` - List user's chamas
- `POST /api/chamas` - Create new chama
- `GET /api/chamas/:id` - Get chama details
- `PUT /api/chamas/:id` - Update chama settings
- `DELETE /api/chamas/:id` - Delete chama

### Member Management
- `GET /api/chamas/:id/members` - List chama members
- `POST /api/chamas/:id/members` - Add new member
- `PUT /api/chamas/:id/members/:memberId` - Update member
- `DELETE /api/chamas/:id/members/:memberId` - Remove member

### Payment & Contributions
- `POST /api/payments/mpesa/stk-push` - Initiate M-Pesa payment
- `POST /api/payments/mpesa/callback` - M-Pesa callback handler
- `GET /api/contributions/:chamaId` - Get contribution history
- `POST /api/contributions` - Record manual contribution

### Loans
- `GET /api/loans/:chamaId` - List chama loans
- `POST /api/loans` - Create loan application
- `PUT /api/loans/:loanId/approve` - Approve loan
- `POST /api/loans/:loanId/payments` - Record loan payment

## Database Schema

### Key Tables
- **users**: User account information
- **chamas**: Chama group details
- **chama_members**: Member-chama relationships
- **contributions**: Payment records
- **loans**: Loan applications and details
- **loan_payments**: Loan repayment tracking
- **goals**: Group and individual goals
- **transactions**: All financial transactions

## Deployment

### Production Build
```bash
# Build frontend
cd frontend
npm run build

# Build backend
cd backend
npm run build
```

### Deployment Checklist
- [ ] Environment variables configured
- [ ] Database migrations run
- [ ] M-Pesa webhook URLs updated
- [ ] SSL certificates installed
- [ ] Domain DNS configured
- [ ] Monitoring tools setup

## Security Features

- **Authentication**: JWT-based with refresh tokens
- **Authorization**: Role-based access control
- **Data Encryption**: Sensitive data encrypted at rest
- **API Rate Limiting**: Prevent abuse and DDoS
- **Input Validation**: Comprehensive request validation
- **Audit Logging**: Track all financial transactions

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Standards
- TypeScript for type safety
- ESLint and Prettier for code formatting
- Jest for unit testing
- Cypress for end-to-end testing

## Testing

```bash
# Run backend tests
cd backend
npm test

# Run frontend tests
cd frontend
npm test

# Run e2e tests
npm run test:e2e
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Documentation**: [docs.chamaapp.com](https://docs.chamaapp.com)
- **Email Support**: support@chamaapp.com
- **Community**: [Discord Server](https://discord.gg/chamaapp)
- **Issues**: [GitHub Issues](https://github.com/yourusername/chama-app/issues)

## Roadmap

### Phase 1 (MVP) ✅
- Basic chama creation and management
- M-Pesa integration
- Member management
- Contribution tracking

### Phase 2 (Q2 2025)
- [ ] Loan management system
- [ ] Advanced reporting
- [ ] Mobile app (React Native)
- [ ] Multi-language support (Swahili)

### Phase 3 (Q3 2025)
- [ ] Investment tracking
- [ ] Integration with banks
- [ ] AI-powered financial insights
- [ ] Micro-insurance products

---

**Built with ❤️ for the Kenyan chama community**
